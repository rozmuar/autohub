"""Схемы уведомлений."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.notification import NotificationChannel, NotificationStatus


class NotificationResponse(BaseModel):
    id: uuid.UUID
    channel: NotificationChannel
    event_type: str
    title: str | None
    body: str
    status: NotificationStatus
    is_read: bool
    entity_type: str | None
    entity_id: uuid.UUID | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationMarkReadRequest(BaseModel):
    notification_ids: list[uuid.UUID]
