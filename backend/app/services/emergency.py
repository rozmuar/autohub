"""Сервис экстренной помощи."""

import json
import math
import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError, NotFoundError
from app.models.emergency import (
    EmergencyRequest,
    EmergencyResponse,
    EmergencyStatus,
    EmergencyType,
    PartnerLocation,
)
from app.models.partner import Partner, PartnerStatus
from app.schemas.emergency import EmergencyCreateRequest, EmergencyRequestResponse

logger = structlog.get_logger(__name__)

_INITIAL_RADIUS_KM = 15
_EXPANDED_RADIUS_KM = 30
_PARTNER_RESPONSE_TIMEOUT_SEC = 60


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Расстояние между двумя точками в км (формула Хаверсина)."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


async def create_emergency(
    user_id: uuid.UUID,
    data: EmergencyCreateRequest,
    db: AsyncSession,
) -> EmergencyRequestResponse:
    """Создаёт запрос экстренной помощи и ищет партнёров."""
    req = EmergencyRequest(
        user_id=user_id,
        emergency_type=data.emergency_type,
        latitude=data.latitude,
        longitude=data.longitude,
        address=data.address,
        description=data.description,
        status=EmergencyStatus.searching,
        search_radius_km=_INITIAL_RADIUS_KM,
    )
    db.add(req)
    await db.flush()
    await db.commit()
    await db.refresh(req)

    # Рассылаем уведомления партнёрам в радиусе
    count = await broadcast_to_partners(req.id, user_id, data.latitude, data.longitude, _INITIAL_RADIUS_KM, db)
    if count == 0:
        # Расширяем радиус
        req.search_radius_km = _EXPANDED_RADIUS_KM
        count = await broadcast_to_partners(req.id, user_id, data.latitude, data.longitude, _EXPANDED_RADIUS_KM, db)

    req.broadcast_count = count
    if count == 0:
        req.status = EmergencyStatus.no_response
    await db.commit()
    await db.refresh(req)
    return EmergencyRequestResponse.model_validate(req)


async def broadcast_to_partners(
    request_id: uuid.UUID,
    user_id: uuid.UUID,
    lat: float,
    lon: float,
    radius_km: float,
    db: AsyncSession,
) -> int:
    """Рассылает push-уведомления партнёрам в радиусе."""
    # Получаем партнёров с известной геолокацией
    q = await db.execute(
        select(PartnerLocation, Partner)
        .join(Partner, Partner.id == PartnerLocation.partner_id)
        .where(
            PartnerLocation.is_online.is_(True),
            Partner.status == PartnerStatus.active,
        )
    )
    rows = q.all()

    notified = 0
    for loc, partner in rows:
        dist = _haversine_km(lat, lon, loc.latitude, loc.longitude)
        if dist <= radius_km:
            # TODO: Отправить push-уведомление партнёру через FCM/APNs
            logger.info("emergency.broadcast", request_id=str(request_id), partner_id=str(partner.id), dist_km=round(dist, 1))
            notified += 1

    return notified


async def partner_respond(
    request_id: uuid.UUID,
    partner_id: uuid.UUID,
    estimated_minutes: int,
    proposed_price: float | None,
    comment: str | None,
    db: AsyncSession,
) -> None:
    """Партнёр откликается на запрос."""
    req_q = await db.execute(select(EmergencyRequest).where(EmergencyRequest.id == request_id))
    req = req_q.scalar_one_or_none()
    if not req:
        raise NotFoundError("Запрос не найден")
    if req.status != EmergencyStatus.searching:
        raise BusinessError("Запрос уже обработан")

    # Проверяем — не откликался ли уже
    existing_q = await db.execute(
        select(EmergencyResponse).where(
            EmergencyResponse.request_id == request_id,
            EmergencyResponse.partner_id == partner_id,
        )
    )
    if existing_q.scalar_one_or_none():
        raise BusinessError("Вы уже откликнулись на этот запрос")

    resp = EmergencyResponse(
        request_id=request_id,
        partner_id=partner_id,
        estimated_arrival_minutes=estimated_minutes,
        proposed_price=proposed_price,
        comment=comment,
    )
    db.add(resp)
    await db.commit()


async def client_accept_partner(
    request_id: uuid.UUID,
    response_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> EmergencyRequestResponse:
    """Клиент принимает отклик партнёра."""
    req_q = await db.execute(select(EmergencyRequest).where(EmergencyRequest.id == request_id))
    req = req_q.scalar_one_or_none()
    if not req or req.user_id != user_id:
        raise NotFoundError("Запрос не найден")
    if req.status != EmergencyStatus.searching:
        raise BusinessError("Запрос уже обработан")

    resp_q = await db.execute(
        select(EmergencyResponse).where(EmergencyResponse.id == response_id)
    )
    resp = resp_q.scalar_one_or_none()
    if not resp or resp.request_id != request_id:
        raise NotFoundError("Отклик не найден")

    resp.is_accepted = True
    req.status = EmergencyStatus.partner_found
    req.accepted_partner_id = resp.partner_id
    req.accepted_at = datetime.now(timezone.utc)
    req.estimated_arrival_minutes = resp.estimated_arrival_minutes

    # Отклоняем остальные отклики
    other_q = await db.execute(
        select(EmergencyResponse).where(
            EmergencyResponse.request_id == request_id,
            EmergencyResponse.id != response_id,
        )
    )
    for other in other_q.scalars().all():
        other.is_accepted = False

    await db.commit()
    await db.refresh(req)
    return EmergencyRequestResponse.model_validate(req)


async def update_partner_location(
    partner_id: uuid.UUID,
    latitude: float,
    longitude: float,
    is_online: bool,
    db: AsyncSession,
) -> None:
    """Обновляет геолокацию партнёра."""
    q = await db.execute(
        select(PartnerLocation).where(PartnerLocation.partner_id == partner_id)
    )
    loc = q.scalar_one_or_none()
    if loc:
        loc.latitude = latitude
        loc.longitude = longitude
        loc.is_online = is_online
    else:
        loc = PartnerLocation(
            partner_id=partner_id,
            latitude=latitude,
            longitude=longitude,
            is_online=is_online,
        )
        db.add(loc)
    await db.commit()


async def get_emergency(
    request_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> EmergencyRequestResponse:
    from sqlalchemy.orm import selectinload
    q = await db.execute(
        select(EmergencyRequest)
        .options(selectinload(EmergencyRequest.responses))
        .where(EmergencyRequest.id == request_id)
    )
    req = q.scalar_one_or_none()
    if not req:
        raise NotFoundError("Запрос не найден")
    if req.user_id != user_id:
        raise BusinessError("Нет доступа")
    return EmergencyRequestResponse.model_validate(req)


async def cancel_emergency(
    request_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> None:
    q = await db.execute(select(EmergencyRequest).where(EmergencyRequest.id == request_id))
    req = q.scalar_one_or_none()
    if not req or req.user_id != user_id:
        raise NotFoundError("Запрос не найден")
    if req.status in (EmergencyStatus.completed, EmergencyStatus.cancelled):
        raise BusinessError(f"Нельзя отменить запрос со статусом {req.status.value}")
    req.status = EmergencyStatus.cancelled
    await db.commit()
