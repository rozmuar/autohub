"""Сервис чата с фильтрацией контактных данных."""

import re
import uuid

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BusinessError, NotFoundError
from app.models.chat import (
    ChatMessage,
    ChatParticipant,
    ChatRoom,
    ChatRoomType,
    MessageStatus,
    MessageType,
)
from app.schemas.chat import ChatMessageResponse, ChatRoomResponse, SendMessageRequest

logger = structlog.get_logger(__name__)

# Паттерны для маскировки контактных данных
_PHONE_RE = re.compile(r"(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}")
_EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_URL_RE = re.compile(r"(https?://[^\s]+|www\.[^\s]+|t\.me/[^\s]+|wa\.me/[^\s]+)")


def _mask_contacts(text: str) -> str:
    """Скрывает телефоны, email и ссылки в тексте сообщения."""
    text = _PHONE_RE.sub("[телефон скрыт]", text)
    text = _EMAIL_RE.sub("[email скрыт]", text)
    text = _URL_RE.sub("[ссылка скрыта]", text)
    return text


async def get_or_create_room(
    room_type: ChatRoomType,
    user_id: uuid.UUID,
    order_id: uuid.UUID | None = None,
    emergency_request_id: uuid.UUID | None = None,
    partner_user_id: uuid.UUID | None = None,
    db: AsyncSession = None,
) -> ChatRoomResponse:
    """Возвращает существующую комнату или создаёт новую."""
    # Ищем существующую комнату
    q_filter = [ChatRoom.room_type == room_type]
    if order_id:
        q_filter.append(ChatRoom.order_id == order_id)
    if emergency_request_id:
        q_filter.append(ChatRoom.emergency_request_id == emergency_request_id)

    q = await db.execute(select(ChatRoom).where(*q_filter))
    room = q.scalar_one_or_none()

    if not room:
        room = ChatRoom(
            room_type=room_type,
            order_id=order_id,
            emergency_request_id=emergency_request_id,
        )
        db.add(room)
        await db.flush()

        # Добавляем участников
        participants = [user_id]
        if partner_user_id:
            participants.append(partner_user_id)

        for uid in participants:
            participant = ChatParticipant(room_id=room.id, user_id=uid)
            db.add(participant)

        await db.commit()
        await db.refresh(room)

    # Считаем непрочитанные
    unread_q = await db.execute(
        select(ChatParticipant).where(
            ChatParticipant.room_id == room.id,
            ChatParticipant.user_id == user_id,
        )
    )
    participant = unread_q.scalar_one_or_none()
    unread = participant.unread_count if participant else 0

    resp = ChatRoomResponse.model_validate(room)
    resp.unread_count = unread
    return resp


async def send_message(
    room_id: uuid.UUID,
    sender_id: uuid.UUID,
    data: SendMessageRequest,
    db: AsyncSession,
) -> ChatMessageResponse:
    """Отправляет сообщение. Применяет маскировку контактов."""
    # Проверяем участие в комнате
    part_q = await db.execute(
        select(ChatParticipant).where(
            ChatParticipant.room_id == room_id,
            ChatParticipant.user_id == sender_id,
        )
    )
    if not part_q.scalar_one_or_none():
        raise BusinessError("Вы не являетесь участником этого чата")

    content = data.content
    if content and data.message_type == MessageType.text:
        content = _mask_contacts(content)

    msg = ChatMessage(
        room_id=room_id,
        sender_id=sender_id,
        message_type=data.message_type,
        content=content,
        file_url=data.file_url,
        file_name=data.file_name,
        status=MessageStatus.sent,
    )
    db.add(msg)

    # Обновляем unread_count для остальных участников
    await db.execute(
        update(ChatParticipant)
        .where(
            ChatParticipant.room_id == room_id,
            ChatParticipant.user_id != sender_id,
        )
        .values(unread_count=ChatParticipant.unread_count + 1)
    )

    await db.commit()
    await db.refresh(msg)
    return ChatMessageResponse.model_validate(msg)


async def get_messages(
    room_id: uuid.UUID,
    user_id: uuid.UUID,
    before_id: uuid.UUID | None,
    limit: int,
    db: AsyncSession,
) -> list[ChatMessageResponse]:
    """Возвращает историю сообщений (cursor-based пагинация)."""
    part_q = await db.execute(
        select(ChatParticipant).where(
            ChatParticipant.room_id == room_id,
            ChatParticipant.user_id == user_id,
        )
    )
    if not part_q.scalar_one_or_none():
        raise BusinessError("Нет доступа")

    q = select(ChatMessage).where(
        ChatMessage.room_id == room_id,
        ChatMessage.is_deleted.is_(False),
    )
    if before_id:
        # Cursor pagination
        ref_q = await db.execute(select(ChatMessage).where(ChatMessage.id == before_id))
        ref = ref_q.scalar_one_or_none()
        if ref:
            q = q.where(ChatMessage.created_at < ref.created_at)

    q = q.order_by(ChatMessage.created_at.desc()).limit(limit)
    result = await db.execute(q)
    messages = result.scalars().all()
    return [ChatMessageResponse.model_validate(m) for m in reversed(messages)]


async def mark_room_read(
    room_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> None:
    """Помечает все сообщения комнаты прочитанными для данного пользователя."""
    await db.execute(
        update(ChatParticipant)
        .where(
            ChatParticipant.room_id == room_id,
            ChatParticipant.user_id == user_id,
        )
        .values(unread_count=0)
    )
    # Помечаем delivered/read сообщения
    await db.execute(
        update(ChatMessage)
        .where(
            ChatMessage.room_id == room_id,
            ChatMessage.sender_id != user_id,
            ChatMessage.status != MessageStatus.read,
        )
        .values(status=MessageStatus.read)
    )
    await db.commit()


async def get_user_rooms(user_id: uuid.UUID, db: AsyncSession) -> list[ChatRoomResponse]:
    """Возвращает все комнаты пользователя."""
    q = await db.execute(
        select(ChatRoom)
        .join(ChatParticipant, ChatParticipant.room_id == ChatRoom.id)
        .where(ChatParticipant.user_id == user_id, ChatRoom.is_active.is_(True))
        .order_by(ChatRoom.created_at.desc())
    )
    rooms = q.scalars().all()
    result = []
    for room in rooms:
        unread_q = await db.execute(
            select(ChatParticipant).where(
                ChatParticipant.room_id == room.id,
                ChatParticipant.user_id == user_id,
            )
        )
        part = unread_q.scalar_one_or_none()
        resp = ChatRoomResponse.model_validate(room)
        resp.unread_count = part.unread_count if part else 0
        result.append(resp)
    return result
