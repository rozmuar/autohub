"""Эндпоинты уведомлений."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas import MessageResponse
from app.schemas.notification import NotificationMarkReadRequest, NotificationResponse
from app.services import notification as notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await notification_service.get_user_notifications(current_user.id, unread_only, db)
    return [NotificationResponse.model_validate(n) for n in items]


@router.patch("/read", response_model=MessageResponse)
async def mark_read(
    body: NotificationMarkReadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = await notification_service.mark_as_read(current_user.id, body.ids, db)
    return MessageResponse(message=f"Отмечено прочитанными: {count}")
