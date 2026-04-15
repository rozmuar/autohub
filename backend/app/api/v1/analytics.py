"""API маршруты аналитики."""

from datetime import date

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.analytics import ConversionStats, PartnerDashboard, PlatformStats
from app.services import analytics as svc

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/partner/{partner_id}/dashboard", response_model=PartnerDashboard)
async def partner_dashboard(
    partner_id: uuid.UUID,
    date_from: date = Query(...),
    date_to: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Дашборд партнёра: выручка, заказы, средний чек."""
    # Партнёр видит только свой дашборд; администратор — любой
    if str(current_user.id) != str(partner_id) and not getattr(current_user, "is_staff", False):
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    return await svc.get_partner_dashboard(partner_id, date_from, date_to, db)


@router.get("/partner/{partner_id}/conversion", response_model=ConversionStats)
async def partner_conversion(
    partner_id: uuid.UUID,
    date_from: date = Query(...),
    date_to: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if str(current_user.id) != str(partner_id) and not getattr(current_user, "is_staff", False):
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    return await svc.get_conversion_stats(partner_id, date_from, date_to, db)


@router.get("/platform", response_model=PlatformStats)
async def platform_stats(
    date_from: date = Query(...),
    date_to: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Сводные показатели платформы (только для администраторов)."""
    if not getattr(current_user, "is_staff", False):
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    return await svc.get_platform_stats(date_from, date_to, db)
