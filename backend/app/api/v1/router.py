"""Корневой API v1 роутер."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.vehicles import router as vehicles_router
from app.api.v1.partners import router as partners_router
from app.api.v1.catalog import router as catalog_router
from app.api.v1.search import router as search_router
from app.api.v1.bookings import router as bookings_router
from app.api.v1.orders import router as orders_router
from app.api.v1.payments import router as payments_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.emergency import router as emergency_router
from app.api.v1.chat import router as chat_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.content import router as content_router

api_router = APIRouter()


@api_router.get("/v1/ping", tags=["system"])
async def ping() -> dict:
    return {"pong": True}


_prefix = "/v1"
api_router.include_router(auth_router, prefix=_prefix)
api_router.include_router(users_router, prefix=_prefix)
api_router.include_router(vehicles_router, prefix=_prefix)
api_router.include_router(partners_router, prefix=_prefix)
api_router.include_router(catalog_router, prefix=_prefix)
api_router.include_router(search_router, prefix=_prefix)
api_router.include_router(bookings_router, prefix=_prefix)
api_router.include_router(orders_router, prefix=_prefix)
api_router.include_router(payments_router, prefix=_prefix)
api_router.include_router(notifications_router, prefix=_prefix)
# Phase 2
api_router.include_router(emergency_router, prefix=_prefix)
api_router.include_router(chat_router, prefix=_prefix)
api_router.include_router(reviews_router, prefix=_prefix)
api_router.include_router(analytics_router, prefix=_prefix)
api_router.include_router(content_router, prefix=_prefix)
