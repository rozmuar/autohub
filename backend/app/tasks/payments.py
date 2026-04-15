"""Задачи для платежей."""

import structlog

from app.worker import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(
    name="app.tasks.payments.process_payout",
    bind=True,
    max_retries=5,
    default_retry_delay=300,
    queue="payments",
)
def process_payout(self, partner_id: str, amount: int, order_id: str) -> dict:
    """Выплата партнёру через ЮKassa после закрытия заказа."""
    try:
        # TODO: Фаза 1 — интеграция ЮKassa выплат
        logger.info("payout.process", partner_id=partner_id, amount=amount)
        return {"status": "queued"}
    except Exception as exc:
        logger.error("payout.process.error", error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.tasks.payments.handle_webhook",
    bind=True,
    max_retries=3,
    queue="payments",
)
def handle_webhook(self, payload: dict) -> dict:
    """Обработка webhook от ЮKassa в фоне."""
    # TODO: Фаза 1
    logger.info("payment.webhook", event=payload.get("event"))
    return {"processed": True}
