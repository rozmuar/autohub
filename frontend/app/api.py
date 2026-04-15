"""API client configuration — URL и заголовки для Backend."""

import os

BACKEND_URL = os.environ.get("BACKEND_URL") or os.environ.get("API_URL", "http://localhost:8000")
API_V1 = f"{BACKEND_URL}/api/v1"
WS_BASE = os.environ.get("WS_URL", "ws://localhost:8000")

# Яндекс.Карты API ключ — получить на https://developer.tech.yandex.ru/
YANDEX_MAPS_KEY = os.environ.get("YANDEX_MAPS_KEY", "")


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}

