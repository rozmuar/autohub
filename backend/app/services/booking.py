"""Сервис бронирования слотов."""

import uuid
from datetime import date, datetime, time, timedelta

import structlog
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError, NotFoundError
from app.models.booking import Booking, BookingStatus, Slot, SlotStatus
from app.models.partner import WorkSchedule
from app.schemas.booking import BookingCreate, BookingResponse, SlotResponse

logger = structlog.get_logger(__name__)
_RESERVATION_TTL = 300  # 5 минут


async def generate_slots(partner_id: uuid.UUID, target_date: date, db: AsyncSession) -> list[Slot]:
    """Генерирует слоты для партнёра на выбранную дату по его расписанию."""
    day_of_week = target_date.weekday()  # 0=пн, 6=вс

    schedule_q = await db.execute(
        select(WorkSchedule).where(
            WorkSchedule.partner_id == partner_id,
            WorkSchedule.day_of_week == day_of_week,
        )
    )
    schedule = schedule_q.scalar_one_or_none()
    if not schedule or schedule.is_day_off:
        return []

    duration_minutes = 60  # TODO: брать из PartnerService по умолчанию

    slots = []
    current = datetime.combine(target_date, schedule.open_time)
    end = datetime.combine(target_date, schedule.close_time)

    while current + timedelta(minutes=duration_minutes) <= end:
        # Пропускаем перерыв
        if schedule.break_start and schedule.break_end:
            break_start = datetime.combine(target_date, schedule.break_start)
            break_end = datetime.combine(target_date, schedule.break_end)
            if current < break_end and (current + timedelta(minutes=duration_minutes)) > break_start:
                current = break_end
                continue

        # Проверяем — существует ли уже слот
        existing_q = await db.execute(
            select(Slot).where(
                Slot.partner_id == partner_id,
                Slot.start_time == current,
            )
        )
        existing = existing_q.scalar_one_or_none()
        if not existing:
            slot = Slot(
                partner_id=partner_id,
                start_time=current,
                end_time=current + timedelta(minutes=duration_minutes),
                status=SlotStatus.available,
            )
            db.add(slot)
            slots.append(slot)

        current += timedelta(minutes=duration_minutes)

    await db.commit()
    return slots


async def get_available_slots(
    partner_id: uuid.UUID,
    date_from: datetime,
    date_to: datetime,
    service_id: uuid.UUID | None,
    db: AsyncSession,
) -> list[SlotResponse]:
    """Возвращает доступные слоты в диапазоне дат."""
    q = await db.execute(
        select(Slot).where(
            Slot.partner_id == partner_id,
            Slot.start_time >= date_from,
            Slot.start_time <= date_to,
            Slot.status == SlotStatus.available,
        ).order_by(Slot.start_time)
    )
    slots = q.scalars().all()
    return [SlotResponse.model_validate(s) for s in slots]


async def reserve_slot(
    slot_id: uuid.UUID,
    user_id: uuid.UUID,
    redis_client,
) -> str:
    """
    Резервирует слот через Redis SETNX с TTL=5 мин.
    Возвращает reservation_key или бросает BusinessError.
    """
    lock_key = f"slot_lock:{slot_id}"
    reservation_key = str(uuid.uuid4())

    acquired = await redis_client.set(lock_key, reservation_key, nx=True, ex=_RESERVATION_TTL)
    if not acquired:
        raise BusinessError("Слот уже зарезервирован. Попробуйте другое время.")
    return reservation_key


async def confirm_booking(
    slot_id: uuid.UUID,
    reservation_key: str,
    data: BookingCreate,
    user_id: uuid.UUID,
    redis_client,
    db: AsyncSession,
) -> BookingResponse:
    """Подтверждает бронирование после проверки резервирования."""
    lock_key = f"slot_lock:{slot_id}"
    stored_key = await redis_client.get(lock_key)
    if stored_key is None:
        raise BusinessError("Время резервирования истекло. Начните заново.")
    if stored_key != reservation_key:
        raise BusinessError("Недействительный ключ резервирования.")

    slot_q = await db.execute(select(Slot).where(Slot.id == slot_id))
    slot = slot_q.scalar_one_or_none()
    if not slot:
        raise NotFoundError("Слот не найден")
    if slot.status != SlotStatus.available:
        raise BusinessError("Слот недоступен")

    slot.status = SlotStatus.booked
    booking = Booking(
        slot_id=slot_id,
        user_id=user_id,
        partner_id=slot.partner_id,
        service_id=data.service_id,
        vehicle_id=data.vehicle_id,
        status=BookingStatus.pending,
    )
    db.add(booking)
    await db.flush()
    await db.refresh(booking)
    await db.commit()

    # Снимаем Redis-блокировку
    await redis_client.delete(lock_key)

    return BookingResponse.model_validate(booking)


async def cancel_booking(
    booking_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> None:
    """Отменяет бронирование и освобождает слот."""
    q = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = q.scalar_one_or_none()
    if not booking:
        raise NotFoundError("Бронирование не найдено")
    if booking.user_id != user_id:
        raise BusinessError("Нет доступа")
    if booking.status in (BookingStatus.completed, BookingStatus.cancelled):
        raise BusinessError(f"Нельзя отменить бронирование со статусом {booking.status.value}")

    booking.status = BookingStatus.cancelled

    slot_q = await db.execute(select(Slot).where(Slot.id == booking.slot_id))
    slot = slot_q.scalar_one_or_none()
    if slot:
        slot.status = SlotStatus.available

    await db.commit()


async def get_user_bookings(user_id: uuid.UUID, db: AsyncSession) -> list[BookingResponse]:
    q = await db.execute(
        select(Booking)
        .where(Booking.user_id == user_id)
        .order_by(Booking.created_at.desc())
    )
    return [BookingResponse.model_validate(b) for b in q.scalars().all()]


async def release_expired_reservations(db: AsyncSession) -> int:
    """Освобождает слоты, у которых истекло время резервирования (Celery task)."""
    now = datetime.utcnow()
    q = await db.execute(
        select(Slot).where(
            Slot.status == SlotStatus.reserved,
            Slot.reserved_until < now,
        )
    )
    slots = q.scalars().all()
    for slot in slots:
        slot.status = SlotStatus.available
        slot.reservation_key = None
        slot.reserved_until = None
        slot.reserved_by_user_id = None

    await db.commit()
    return len(slots)
