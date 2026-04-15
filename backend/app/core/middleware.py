"""Middleware: Request ID, логирование запросов."""

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Присваивает каждому запросу уникальный X-Request-ID."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Структурированное логирование входящих запросов."""

    SKIP_PATHS = {"/health", "/metrics", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        request_id = getattr(request.state, "request_id", "-")

        # Сбор контекста без PII
        log = logger.bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=self._get_client_ip(request),
        )

        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start) * 1000, 1)

            log_fn = log.warning if response.status_code >= 400 else log.info
            log_fn(
                "http.request",
                status=response.status_code,
                duration_ms=duration_ms,
            )
            return response

        except Exception as exc:
            duration_ms = round((time.perf_counter() - start) * 1000, 1)
            log.error("http.request.error", error=str(exc), duration_ms=duration_ms)
            raise

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        # Доверяем только первому IP из X-Forwarded-For (от nginx)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
