import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import sentry_sdk
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.config import settings
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware, RequestLoggingMiddleware
from app.database import create_db_pool, dispose_db_pool
from app.search import create_es_client, close_es_client
from app.cache import create_redis_pool, close_redis_pool
from app.api.v1.router import api_router

logger = structlog.get_logger(__name__)


def configure_sentry() -> None:
    if not settings.sentry_dsn:
        return
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1 if settings.is_production else 1.0,
        send_default_pii=False,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Жизненный цикл приложения: инициализация и освобождение ресурсов."""
    logger.info("startup", env=settings.app_env, debug=settings.app_debug)

    # Инициализация пула БД
    await create_db_pool()
    logger.info("database.pool.created")

    # Инициализация Redis
    await create_redis_pool()
    logger.info("redis.pool.created")

    # Инициализация Elasticsearch
    await create_es_client()
    logger.info("elasticsearch.client.created")

    yield  # приложение работает

    # Освобождение ресурсов
    await dispose_db_pool()
    await close_redis_pool()
    await close_es_client()
    logger.info("shutdown.complete")


def create_app() -> FastAPI:
    configure_logging(level=settings.log_level)
    configure_sentry()

    app = FastAPI(
        title="Auto Hub API",
        description="Единая цифровая платформа для автосервисов и автовладельцев",
        version="0.1.0",
        docs_url="/api/docs" if not settings.is_production else None,
        redoc_url="/api/redoc" if not settings.is_production else None,
        openapi_url="/api/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ── Middleware (порядок важен — первый применяется последним) ────
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts if settings.is_production else ["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    # ── Роутеры ──────────────────────────────────────────────────────
    app.include_router(api_router, prefix="/api")

    # WebSocket роутеры (монтируются без /api prefix — /ws/...)
    from app.ws.routes import router as ws_router
    app.include_router(ws_router)

    # ── Admin Panel ──────────────────────────────────────────────────
    from app.admin import setup_admin
    setup_admin(app)

    # ── Exception handlers ───────────────────────────────────────────
    from app.core.exceptions import register_exception_handlers
    register_exception_handlers(app)

    return app


app = create_app()


@app.get("/health", tags=["system"], include_in_schema=False)
async def health_check() -> dict:
    return {"status": "ok", "env": settings.app_env}


# Запуск напрямую: python -m app.main
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
