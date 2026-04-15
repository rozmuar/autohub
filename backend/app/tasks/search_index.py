"""Задачи индексации в Elasticsearch."""

import structlog

from app.worker import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(
    name="app.tasks.search_index.index_partner",
    queue="search_index",
)
def index_partner(partner_id: str) -> dict:
    """Индексирует/обновляет партнёра в Elasticsearch."""
    # TODO: Фаза 1
    logger.info("es.index_partner", partner_id=partner_id)
    return {"indexed": False}


@celery_app.task(
    name="app.tasks.search_index.reindex_all_partners",
    queue="search_index",
)
def reindex_all_partners() -> dict:
    """Полная переиндексация всех партнёров."""
    # TODO: Фаза 1
    logger.info("es.reindex_all_partners.run")
    return {"indexed": 0}
