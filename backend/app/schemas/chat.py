"""Схемы чата."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.chat import ChatRoomType, MessageStatus, MessageType


class ChatRoomCreate(BaseModel):
    room_type: ChatRoomType
    order_id: uuid.UUID | None = None
    emergency_request_id: uuid.UUID | None = None


class ChatRoomResponse(BaseModel):
    id: uuid.UUID
    room_type: ChatRoomType
    order_id: uuid.UUID | None
    emergency_request_id: uuid.UUID | None
    is_active: bool
    unread_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SendMessageRequest(BaseModel):
    content: str | None = Field(None, max_length=4000)
    message_type: MessageType = MessageType.text
    file_url: str | None = None
    file_name: str | None = None


class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    room_id: uuid.UUID
    sender_id: uuid.UUID
    message_type: MessageType
    content: str | None
    file_url: str | None
    file_name: str | None
    status: MessageStatus
    is_deleted: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WsMessagePayload(BaseModel):
    """Пэйлоад WebSocket сообщения."""
    type: str  # "message" | "typing" | "read" | "status"
    data: dict
