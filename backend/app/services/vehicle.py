"""Сервис автомобилей/гаража."""

import re
import uuid

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from app.models.vehicle import CarBrand, CarModel, Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate

logger = structlog.get_logger(__name__)


def _validate_vin(vin: str) -> bool:
    """Базовая проверка VIN: 17 символов, только A-Z и 0-9 (без I, O, Q)."""
    pattern = r"^[A-HJ-NPR-Z0-9]{17}$"
    return bool(re.match(pattern, vin.upper()))


async def get_garage(db: AsyncSession, user_id: uuid.UUID) -> list[Vehicle]:
    result = await db.execute(
        select(Vehicle).where(
            Vehicle.owner_id == user_id,
            Vehicle.deleted_at.is_(None),
        ).order_by(Vehicle.is_primary.desc(), Vehicle.created_at)
    )
    return list(result.scalars().all())


async def get_vehicle(db: AsyncSession, vehicle_id: uuid.UUID, user_id: uuid.UUID) -> Vehicle:
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.deleted_at.is_(None))
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise NotFoundError("Автомобиль не найден")
    if vehicle.owner_id != user_id:
        raise PermissionDeniedError("Нет доступа к этому автомобилю")
    return vehicle


async def add_vehicle(db: AsyncSession, user_id: uuid.UUID, data: VehicleCreate) -> Vehicle:
    if data.vin and not _validate_vin(data.vin):
        raise ValidationError("Некорректный VIN номер")

    # Если is_primary=True, снимаем флаг с остальных
    if data.is_primary:
        await _unset_primary(db, user_id)

    vehicle = Vehicle(
        owner_id=user_id,
        **data.model_dump(),
    )
    db.add(vehicle)
    await db.flush()
    logger.info("vehicle.added", user_id=str(user_id), vehicle_id=str(vehicle.id))
    return vehicle


async def update_vehicle(
    db: AsyncSession, vehicle_id: uuid.UUID, user_id: uuid.UUID, data: VehicleUpdate
) -> Vehicle:
    vehicle = await get_vehicle(db, vehicle_id, user_id)

    if data.vin and not _validate_vin(data.vin):
        raise ValidationError("Некорректный VIN номер")

    if data.is_primary:
        await _unset_primary(db, user_id)

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(vehicle, field, value)
    await db.flush()
    return vehicle


async def delete_vehicle(db: AsyncSession, vehicle_id: uuid.UUID, user_id: uuid.UUID) -> None:
    from datetime import datetime, timezone
    vehicle = await get_vehicle(db, vehicle_id, user_id)
    vehicle.deleted_at = datetime.now(timezone.utc)
    await db.flush()


async def _unset_primary(db: AsyncSession, user_id: uuid.UUID) -> None:
    result = await db.execute(
        select(Vehicle).where(
            Vehicle.owner_id == user_id,
            Vehicle.is_primary.is_(True),
            Vehicle.deleted_at.is_(None),
        )
    )
    for v in result.scalars().all():
        v.is_primary = False
    await db.flush()


async def get_brands(db: AsyncSession) -> list[CarBrand]:
    result = await db.execute(
        select(CarBrand)
        .where(CarBrand.is_active.is_(True))
        .order_by(CarBrand.name)
    )
    return list(result.scalars().all())


async def get_models(db: AsyncSession, brand_name: str) -> list[CarModel]:
    result = await db.execute(
        select(CarModel)
        .join(CarBrand, CarModel.brand_id == CarBrand.id)
        .where(
            CarBrand.name == brand_name,
            CarModel.is_active.is_(True),
        )
        .order_by(CarModel.name)
    )
    return list(result.scalars().all())
