"""Эндпоинты пользователей."""

import uuid

from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas import MessageResponse
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.partner import PartnerShortResponse
from app.services import user as user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updated = await user_service.update_profile(db, current_user.id, body)
    return updated


@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    updated = await user_service.update_avatar(db, current_user.id, content, file.content_type or "image/jpeg")
    return updated


@router.delete("/me", response_model=MessageResponse)
async def delete_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await user_service.delete_account(db, current_user.id)
    return MessageResponse(message="Аккаунт удалён")


@router.get("/me/favorites", response_model=list[PartnerShortResponse])
async def get_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.get_favorites(db, current_user.id)


@router.post("/me/favorites/{partner_id}", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    partner_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await user_service.add_favorite(db, current_user.id, partner_id)
    return MessageResponse(message="Добавлено в избранное")


@router.delete("/me/favorites/{partner_id}", response_model=MessageResponse)
async def remove_favorite(
    partner_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await user_service.remove_favorite(db, current_user.id, partner_id)
    return MessageResponse(message="Удалено из избранного")
