"""Задачи для уведомлений."""

import structlog

from app.worker import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(
    name="app.tasks.notifications.send_sms",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="notifications",
)
def send_sms(self, phone: str, message: str) -> dict:
    """Отправка SMS через SMS Центр."""
    try:
        # TODO: Фаза 1 — интеграция smsc.ru
        logger.info("sms.send", phone=phone[:4] + "****")
        return {"status": "queued"}
    except Exception as exc:
        logger.error("sms.send.error", error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.tasks.notifications.send_email",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="notifications",
)
def send_email(self, to: str, subject: str, html_body: str) -> dict:
    """Отправка Email."""
    try:
        # TODO: Фаза 1 — интеграция SMTP / Unisender
        logger.info("email.send", to=to)
        return {"status": "queued"}
    except Exception as exc:
        logger.error("email.send.error", error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.tasks.notifications.send_push",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="notifications",
)
def send_push(self, user_id: str, title: str, body: str, data: dict | None = None) -> dict:
    """Отправка Push-уведомления через FCM/APNs."""
    try:
        # TODO: Фаза 1 — интеграция Firebase FCM
        logger.info("push.send", user_id=user_id, title=title)
        return {"status": "queued"}
    except Exception as exc:
        logger.error("push.send.error", error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.tasks.notifications.send_booking_reminders",
    queue="notifications",
)
def send_booking_reminders() -> dict:
    """Периодическая задача: напоминания за 24ч и 2ч до записи."""
    # TODO: Фаза 1 — запрос к БД и отправка напоминаний
    logger.info("booking_reminders.run")
    return {"processed": 0}
