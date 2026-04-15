"""Celery задачи: истечение откликов на экстренные заявки."""

from datetime import datetime, timedelta

import structlog

from app.worker import celery_app

logger = structlog.get_logger(__name__)

# Время ожидания ответа партнёра до истечения
RESPONSE_TIMEOUT_SECONDS = 60


@celery_app.task(name="app.tasks.emergency.expire_emergency_responses", bind=True)
def expire_emergency_responses(self) -> dict:
    """Помечает устаревшие отклики как timed_out.

    Партнёр имеет 60 секунд чтобы его отклик был принят клиентом.
    """
    import asyncio
    from sqlalchemy import select, update
    from app.database import _session_factory
    from app.models.emergency import EmergencyResponse, EmergencyRequest, EmergencyStatus

    async def _run() -> int:
        if _session_factory is None:
            return 0
        threshold = datetime.utcnow() - timedelta(seconds=RESPONSE_TIMEOUT_SECONDS)
        async with _session_factory() as db:
            result = await db.execute(
                update(EmergencyResponse)
                .where(
                    EmergencyResponse.is_accepted.is_(False),
                    EmergencyResponse.timed_out.is_(False),
                    EmergencyResponse.created_at <= threshold,
                )
                .values(timed_out=True)
            )
            count = result.rowcount
            await db.commit()
        return count

    async def _expand_radius() -> None:
        """Расширяет радиус поиска для заявок без откликов"""
        if _session_factory is None:
            return
        from app.models.emergency import EmergencyRequest, EmergencyStatus
        no_response_threshold = datetime.utcnow() - timedelta(minutes=3)
        async with _session_factory() as db:
            result = await db.execute(
                select(EmergencyRequest).where(
                    EmergencyRequest.status == EmergencyStatus.searching,
                    EmergencyRequest.search_radius_km < 30,
                    EmergencyRequest.created_at <= no_response_threshold,
                )
            )
            requests = result.scalars().all()
            for req in requests:
                req.search_radius_km = 30
                # Повторное сканирование партнёров
                from app.services.emergency import broadcast_to_partners
                await broadcast_to_partners(
                    request_id=req.id,
                    user_id=req.user_id,
                    lat=req.latitude,
                    lon=req.longitude,
                    radius_km=30,
                    db=db,
                )
            await db.commit()

    try:
        expired = asyncio.run(_run())
        asyncio.run(_expand_radius())
        logger.debug("emergency_responses_expired", count=expired)
        return {"expired": expired}
    except Exception as exc:
        logger.exception("emergency_expire_task_failed", error=str(exc))
        raise self.retry(exc=exc, countdown=30)
