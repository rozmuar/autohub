"""Эндпоинты партнёров."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas import MessageResponse
from app.schemas.partner import (
    PartnerCreate,
    PartnerResponse,
    PartnerUpdate,
    WorkScheduleIn,
    WorkScheduleResponse,
)
from app.services import partner as partner_service

router = APIRouter(prefix="/partners", tags=["partners"])


@router.get("/me", response_model=PartnerResponse)
async def get_my_partner(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await partner_service.get_my_partner(db, current_user.id)


@router.post("", response_model=PartnerResponse, status_code=status.HTTP_201_CREATED)
async def create_partner(
    body: PartnerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await partner_service.create_partner(db, current_user.id, body)


@router.get("/{partner_id}", response_model=PartnerResponse)
async def get_partner(
    partner_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await partner_service.get_partner_by_id(db, partner_id)


@router.patch("/{partner_id}", response_model=PartnerResponse)
async def update_partner(
    partner_id: uuid.UUID,
    body: PartnerUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await partner_service.update_partner(db, partner_id, current_user.id, body)


@router.post("/{partner_id}/submit", response_model=PartnerResponse)
async def submit_for_verification(
    partner_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await partner_service.submit_for_verification(db, partner_id, current_user.id)


@router.put("/{partner_id}/schedule", response_model=list[WorkScheduleResponse])
async def set_schedule(
    partner_id: uuid.UUID,
    body: list[WorkScheduleIn],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await partner_service.set_schedule(db, partner_id, current_user.id, body)


@router.patch("/{partner_id}/location", response_model=PartnerResponse)
async def update_location(
    partner_id: uuid.UUID,
    latitude: float,
    longitude: float,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await partner_service.update_location(db, partner_id, current_user.id, latitude, longitude)
