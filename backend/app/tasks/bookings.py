"""Задачи для бронирований."""

import structlog

from app.worker import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(
    name="app.tasks.bookings.release_expired_slots",
    queue="default",
)
def release_expired_slots() -> dict:
    """Освобождает слоты с истёкшим временем резервирования (5 мин)."""
    # TODO: Фаза 1 — SELECT * FROM slots WHERE status='reserved' AND reservation_expires_at < NOW()
    logger.info("slots.release_expired.run")
    return {"released": 0}


@celery_app.task(
    name="app.tasks.bookings.auto_release_slot",
    bind=True,
    queue="default",
)
def auto_release_slot(self, slot_id: str) -> dict:
    """Освобождает конкретный слот если заказ не подтверждён."""
    # TODO: Фаза 1
    logger.info("slot.auto_release", slot_id=slot_id)
    return {"slot_id": slot_id, "released": False}
