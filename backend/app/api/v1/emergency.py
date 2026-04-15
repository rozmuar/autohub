"""API маршруты экстренной помощи."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.emergency import (
    EmergencyCreateRequest,
    EmergencyRequestResponse,
    EmergencyResponseCreate,
    EmergencyResponseItem,
    PartnerLocationUpdate,
)
from app.services import emergency as svc

router = APIRouter(prefix="/emergency", tags=["emergency"])


@router.post("", response_model=EmergencyRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_emergency(
    data: EmergencyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Создать экстренную заявку и начать поиск партнёра."""
    return await svc.create_emergency(current_user.id, data, db)


@router.get("/{request_id}", response_model=EmergencyRequestResponse)
async def get_emergency(
    request_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    return await svc.get_emergency(request_id, current_user.id, db)


@router.post("/{request_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_emergency(
    request_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    await svc.cancel_emergency(request_id, current_user.id, db)


@router.post("/{request_id}/respond", response_model=EmergencyResponseItem, status_code=status.HTTP_201_CREATED)
async def partner_respond(
    request_id: uuid.UUID,
    data: EmergencyResponseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Партнёр откликается на экстренную заявку."""
    return await svc.partner_respond(
        request_id=request_id,
        partner_id=current_user.id,
        estimated_arrival_minutes=data.estimated_arrival_minutes,
        proposed_price=data.proposed_price,
        comment=data.comment,
        db=db,
    )


@router.post("/{request_id}/accept/{response_id}", response_model=EmergencyRequestResponse)
async def accept_partner_response(
    request_id: uuid.UUID,
    response_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Клиент принимает отклик партнёра."""
    return await svc.client_accept_partner(request_id, response_id, current_user.id, db)


@router.patch("/location", status_code=status.HTTP_204_NO_CONTENT)
async def update_location(
    data: PartnerLocationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Партнёр обновляет своё местоположение."""
    await svc.update_partner_location(
        current_user.id, data.latitude, data.longitude, data.is_online, db
    )
