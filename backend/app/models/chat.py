"""Модели чата."""

import enum
import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ChatRoomType(str, enum.Enum):
    order = "order"           # Чат по заказу
    emergency = "emergency"   # Чат по экстренному вызову
    support = "support"       # Чат с поддержкой
    expert = "expert"         # Чат с экспертом-подборщиком


class MessageStatus(str, enum.Enum):
    sent = "sent"
    delivered = "delivered"
    read = "read"


class MessageType(str, enum.Enum):
    text = "text"
    image = "image"
    document = "document"
    system = "system"   # Системное сообщение (изменение статуса и т.п.)


class ChatRoom(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chat_rooms"

    room_type: Mapped[ChatRoomType] = mapped_column(Enum(ChatRoomType), nullable=False)

    # Привязка к сущности
    order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True
    )
    emergency_request_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("emergency_requests.id", ondelete="SET NULL"), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_message_at: Mapped[uuid.UUID | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        Index("ix_chat_rooms_order_id", "order_id"),
        Index("ix_chat_rooms_emergency_request_id", "emergency_request_id"),
    )

    participants: Mapped[list["ChatParticipant"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )


class ChatParticipant(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chat_participants"

    room_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    is_muted: Mapped[bool] = mapped_column(Boolean, default=False)
    unread_count: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint("room_id", "user_id", name="uq_chat_participant"),
        Index("ix_chat_participants_room_id", "room_id"),
        Index("ix_chat_participants_user_id", "user_id"),
    )

    room: Mapped["ChatRoom"] = relationship(back_populates="participants")


class ChatMessage(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chat_messages"

    room_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType), default=MessageType.text, nullable=False
    )
    # Текст с маскировкой контактов
    content: Mapped[str | None] = mapped_column(Text)
    # Для файлов
    file_url: Mapped[str | None] = mapped_column(String(500))
    file_name: Mapped[str | None] = mapped_column(String(255))
    file_size: Mapped[int | None] = mapped_column(Integer)

    status: Mapped[MessageStatus] = mapped_column(
        Enum(MessageStatus), default=MessageStatus.sent, nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Для системных сообщений — метаданные
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    __table_args__ = (
        Index("ix_chat_messages_room_id", "room_id"),
        Index("ix_chat_messages_sender_id", "sender_id"),
        Index("ix_chat_messages_created_at", "created_at"),
    )

    room: Mapped["ChatRoom"] = relationship(back_populates="messages")
