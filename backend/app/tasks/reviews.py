"""Celery задачи: запрос отзывов после закрытия заказа."""

from datetime import datetime, timedelta

import structlog

from app.worker import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="app.tasks.reviews.request_reviews_for_closed_orders", bind=True)
def request_reviews_for_closed_orders(self) -> dict:
    """Отправляет запрос на отзыв клиентам, чьи заказы закрыты 2+ часа назад.

    Запускается каждые 5 минут через beat_schedule.
    Использует синхронный контекст — asyncio.run() для каждой пачки.
    """
    import asyncio
    from sqlalchemy import select
    from app.database import _session_factory
    from app.models.order import Order, OrderStatus
    from app.models.review import Review

    async def _run() -> int:
        if _session_factory is None:
            return 0
        threshold = datetime.utcnow() - timedelta(hours=2)
        processed = 0
        async with _session_factory() as db:
            # Заказы, закрытые 2-26ч назад без отзыва
            result = await db.execute(
                select(Order).where(
                    Order.status == OrderStatus.closed,
                    Order.updated_at >= threshold - timedelta(hours=24),
                    Order.updated_at <= threshold,
                )
            )
            orders = result.scalars().all()

            for order in orders:
                # Проверяем, нет ли уже отзыва
                review_q = await db.execute(
                    select(Review.id).where(Review.order_id == order.id)
                )
                if review_q.scalar_one_or_none():
                    continue

                # Отправляем пуш через задачу уведомлений
                from app.tasks.notifications import send_push_notification
                send_push_notification.delay(
                    user_id=str(order.client_id),
                    title="Оцените качество обслуживания",
                    body="Ваш заказ выполнен. Поделитесь впечатлением — это займёт 1 минуту.",
                    data={"type": "review_request", "order_id": str(order.id)},
                )
                processed += 1

        return processed

    try:
        count = asyncio.run(_run())
        logger.info("review_requests_sent", count=count)
        return {"sent": count}
    except Exception as exc:
        logger.exception("review_request_task_failed", error=str(exc))
        raise self.retry(exc=exc, countdown=60)
