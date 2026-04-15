"""Эндпоинты бронирований."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import get_redis
from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas import MessageResponse
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    SlotReserveRequest,
    SlotReserveResponse,
    SlotResponse,
)
from app.services import booking as booking_service

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/slots", response_model=list[SlotResponse])
async def get_available_slots(
    partner_id: uuid.UUID,
    date_from: datetime,
    date_to: datetime,
    service_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await booking_service.get_available_slots(partner_id, date_from, date_to, service_id, db)


@router.post("/slots/{slot_id}/reserve", response_model=SlotReserveResponse)
async def reserve_slot(
    slot_id: uuid.UUID,
    body: SlotReserveRequest,
    current_user: User = Depends(get_current_user),
    redis=Depends(get_redis),
):
    reservation_key = await booking_service.reserve_slot(slot_id, current_user.id, redis)
    return SlotReserveResponse(reservation_key=reservation_key, ttl_seconds=300)


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    body: BookingCreate,
    current_user: User = Depends(get_current_user),
    redis=Depends(get_redis),
    db: AsyncSession = Depends(get_db),
):
    return await booking_service.confirm_booking(
        slot_id=body.slot_id,
        reservation_key=body.reservation_key,
        data=body,
        user_id=current_user.id,
        redis_client=redis,
        db=db,
    )


@router.get("", response_model=list[BookingResponse])
async def list_bookings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await booking_service.get_user_bookings(current_user.id, db)


@router.delete("/{booking_id}", response_model=MessageResponse)
async def cancel_booking(
    booking_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await booking_service.cancel_booking(booking_id, current_user.id, db)
    return MessageResponse(message="Бронирование отменено")
