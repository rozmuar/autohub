"""Сервис уведомлений (strategy pattern)."""

import uuid
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationChannel, NotificationStatus

logger = structlog.get_logger(__name__)


class _Channel:
    async def send(self, notification: Notification, user_phone: str | None, user_email: str | None) -> bool:
        raise NotImplementedError


class _SmsChannel(_Channel):
    async def send(self, notification: Notification, user_phone: str | None, user_email: str | None) -> bool:
        if not user_phone:
            return False
        logger.info("sms.send", phone=user_phone, title=notification.title)
        # TODO: интеграция с реальным SMS-провайдером (например, СМС.ру)
        return True


class _EmailChannel(_Channel):
    async def send(self, notification: Notification, user_phone: str | None, user_email: str | None) -> bool:
        if not user_email:
            return False
        logger.info("email.send", email=user_email, title=notification.title)
        # TODO: интеграция с SMTP / SendGrid
        return True


class _PushChannel(_Channel):
    async def send(self, notification: Notification, user_phone: str | None, user_email: str | None) -> bool:
        logger.info("push.send", user_id=str(notification.user_id), title=notification.title)
        # TODO: Firebase Cloud Messaging
        return True


class _TelegramChannel(_Channel):
    async def send(self, notification: Notification, user_phone: str | None, user_email: str | None) -> bool:
        logger.info("telegram.send", user_id=str(notification.user_id), title=notification.title)
        # TODO: Bot API
        return True


_CHANNELS: dict[NotificationChannel, _Channel] = {
    NotificationChannel.sms: _SmsChannel(),
    NotificationChannel.email: _EmailChannel(),
    NotificationChannel.push: _PushChannel(),
    NotificationChannel.telegram: _TelegramChannel(),
}

_EVENT_TEMPLATES: dict[str, dict] = {
    "booking_confirmed": {
        "title": "Бронирование подтверждено",
        "body": "Ваш визит в {partner_name} запланирован на {date}.",
    },
    "booking_cancelled": {
        "title": "Бронирование отменено",
        "body": "Бронирование #{booking_id} было отменено.",
    },
    "order_status_changed": {
        "title": "Статус заказа изменён",
        "body": "Заказ #{order_number}: {status}.",
    },
    "payment_succeeded": {
        "title": "Оплата прошла успешно",
        "body": "Заказ #{order_number} оплачен на сумму {amount} ₽.",
    },
    "otp_code": {
        "title": "Код подтверждения",
        "body": "Ваш код: {code}. Действителен 5 минут.",
    },
}


async def send_notification(
    user_id: uuid.UUID,
    event_type: str,
    data: dict[str, Any],
    channels: list[NotificationChannel],
    db: AsyncSession,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
) -> None:
    """Создаёт и отправляет уведомление пользователю по заданным каналам."""
    from app.models.user import User
    user_q = await db.execute(select(User).where(User.id == user_id))
    user = user_q.scalar_one_or_none()
    if not user:
        logger.warning("notification.user_not_found", user_id=str(user_id))
        return

    template = _EVENT_TEMPLATES.get(event_type, {"title": event_type, "body": str(data)})
    try:
        title = template["title"].format(**data)
        body = template["body"].format(**data)
    except KeyError:
        title = template["title"]
        body = template["body"]

    notifications = []
    for channel in channels:
        notif = Notification(
            user_id=user_id,
            channel=channel,
            event_type=event_type,
            title=title,
            body=body,
            status=NotificationStatus.pending,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        db.add(notif)
        notifications.append((notif, channel))

    await db.flush()

    for notif, channel in notifications:
        handler = _CHANNELS.get(channel)
        if not handler:
            continue
        try:
            success = await handler.send(notif, user.phone, user.email)
            notif.status = NotificationStatus.sent if success else NotificationStatus.failed
            notif.attempts += 1
        except Exception as e:
            logger.error("notification.send_error", channel=channel.value, error=str(e))
            notif.status = NotificationStatus.failed
            notif.attempts += 1

    await db.commit()


async def get_user_notifications(
    user_id: uuid.UUID,
    unread_only: bool,
    db: AsyncSession,
) -> list[Notification]:
    q = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        q = q.where(Notification.is_read.is_(False))
    q = q.order_by(Notification.created_at.desc()).limit(50)
    result = await db.execute(q)
    return list(result.scalars().all())


async def mark_as_read(
    user_id: uuid.UUID,
    notification_ids: list[uuid.UUID] | None,
    db: AsyncSession,
) -> int:
    """Помечает уведомления прочитанными. Если ids=None — все непрочитанные."""
    from sqlalchemy import update
    stmt = (
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read.is_(False))
    )
    if notification_ids:
        stmt = stmt.where(Notification.id.in_(notification_ids))

    result = await db.execute(stmt.values(is_read=True))
    await db.commit()
    return result.rowcount
