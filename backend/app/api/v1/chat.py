"""API маршруты чата."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.chat import (
    ChatMessageResponse,
    ChatRoomCreate,
    ChatRoomResponse,
    SendMessageRequest,
)
from app.services import chat as svc

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/rooms", response_model=list[ChatRoomResponse])
async def list_rooms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Список чат-комнат текущего пользователя."""
    return await svc.get_user_rooms(current_user.id, db)


@router.post("/rooms", response_model=ChatRoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    data: ChatRoomCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Создать или получить чат-комнату (идемпотентно)."""
    return await svc.get_or_create_room(
        room_type=data.room_type,
        user_id=current_user.id,
        order_id=data.order_id,
        emergency_request_id=data.emergency_request_id,
        partner_user_id=data.partner_user_id,
        db=db,
    )


@router.get("/rooms/{room_id}/messages", response_model=list[ChatMessageResponse])
async def get_messages(
    room_id: uuid.UUID,
    before_id: uuid.UUID | None = Query(None, description="Cursor: загрузить до этого ID"),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """История сообщений (cursor-based пагинация)."""
    return await svc.get_messages(room_id, current_user.id, before_id, limit, db)


@router.post(
    "/rooms/{room_id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    room_id: uuid.UUID,
    data: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Отправить сообщение (REST fallback для WebSocket)."""
    return await svc.send_message(room_id, current_user.id, data, db)


@router.post("/rooms/{room_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_read(
    room_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Пометить все сообщения комнаты прочитанными."""
    await svc.mark_room_read(room_id, current_user.id, db)
