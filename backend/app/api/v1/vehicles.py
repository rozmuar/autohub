"""Эндпоинты гаража (автомобили пользователя)."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas import MessageResponse
from app.schemas.vehicle import (
    CarBrandResponse,
    CarModelResponse,
    VehicleCreate,
    VehicleResponse,
    VehicleUpdate,
)
from app.services import vehicle as vehicle_service
from app.services.vin import decode_vin_extended

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("/vin/{vin}")
async def decode_vin_endpoint(vin: str):
    """Декодирует VIN через NHTSA API — марку, модель, год, тип топлива и фото."""
    return await decode_vin_extended(vin)


@router.get("/brands", response_model=list[CarBrandResponse])
async def list_brands(db: AsyncSession = Depends(get_db)):
    """Список всех активных марок автомобилей из каталога."""
    return await vehicle_service.get_brands(db)


@router.get("/models", response_model=list[CarModelResponse])
async def list_models(brand: str, db: AsyncSession = Depends(get_db)):
    """Список моделей для указанной марки (?brand=Toyota)."""
    return await vehicle_service.get_models(db, brand)


@router.get("", response_model=list[VehicleResponse])
async def get_garage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await vehicle_service.get_garage(db, current_user.id)


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def add_vehicle(
    body: VehicleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await vehicle_service.add_vehicle(db, current_user.id, body)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await vehicle_service.get_vehicle(db, vehicle_id, current_user.id)


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: uuid.UUID,
    body: VehicleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await vehicle_service.update_vehicle(db, vehicle_id, current_user.id, body)


@router.delete("/{vehicle_id}", response_model=MessageResponse)
async def delete_vehicle(
    vehicle_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await vehicle_service.delete_vehicle(db, vehicle_id, current_user.id)
    return MessageResponse(message="Автомобиль удалён")
