"""Сервис аналитики для партнёров и платформы."""

import uuid
from datetime import date, datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus
from app.models.partner import Partner
from app.models.user import User
from app.schemas.analytics import ConversionStats, PartnerDashboard, PlatformStats, RevenuePoint

logger = structlog.get_logger(__name__)


async def get_partner_dashboard(
    partner_id: uuid.UUID,
    date_from: date,
    date_to: date,
    db: AsyncSession,
) -> PartnerDashboard:
    """Дашборд партнёра: выручка, кол-во заказов, средний чек, динамика."""
    dt_from = datetime.combine(date_from, datetime.min.time())
    dt_to = datetime.combine(date_to, datetime.max.time())

    completed_statuses = [OrderStatus.closed, OrderStatus.completed]

    q = await db.execute(
        select(
            func.coalesce(func.sum(Order.final_amount), 0).label("revenue"),
            func.count(Order.id).label("order_count"),
            func.coalesce(func.avg(Order.final_amount), 0).label("avg_check"),
        ).where(
            Order.partner_id == partner_id,
            Order.status.in_(completed_statuses),
            Order.created_at >= dt_from,
            Order.created_at <= dt_to,
        )
    )
    row = q.one()

    # Динамика по дням
    daily_q = await db.execute(
        select(
            func.date_trunc("day", Order.created_at).label("day"),
            func.coalesce(func.sum(Order.final_amount), 0).label("revenue"),
            func.count(Order.id).label("order_count"),
        )
        .where(
            Order.partner_id == partner_id,
            Order.status.in_(completed_statuses),
            Order.created_at >= dt_from,
            Order.created_at <= dt_to,
        )
        .group_by(func.date_trunc("day", Order.created_at))
        .order_by(func.date_trunc("day", Order.created_at))
    )
    chart = [
        RevenuePoint(
            date=r.day.date(),
            revenue=float(r.revenue),
            order_count=r.order_count,
        )
        for r in daily_q.all()
    ]

    return PartnerDashboard(
        partner_id=partner_id,
        date_from=date_from,
        date_to=date_to,
        total_revenue=float(row.revenue),
        order_count=row.order_count,
        average_check=float(row.avg_check),
        chart=chart,
    )


async def get_conversion_stats(
    partner_id: uuid.UUID,
    date_from: date,
    date_to: date,
    db: AsyncSession,
) -> ConversionStats:
    """Статистика конверсий (просмотры ↦ заказы). Просмотры не трекируются — заглушка."""
    dt_from = datetime.combine(date_from, datetime.min.time())
    dt_to = datetime.combine(date_to, datetime.max.time())

    orders_q = await db.execute(
        select(func.count(Order.id)).where(
            Order.partner_id == partner_id,
            Order.created_at >= dt_from,
            Order.created_at <= dt_to,
        )
    )
    total_orders = orders_q.scalar_one() or 0

    return ConversionStats(
        partner_id=partner_id,
        date_from=date_from,
        date_to=date_to,
        profile_views=0,   # TODO: implement view tracking
        orders_created=total_orders,
        conversion_rate=0.0,
    )


async def get_platform_stats(
    date_from: date,
    date_to: date,
    db: AsyncSession,
) -> PlatformStats:
    """Статистика всей платформы (только для администраторов)."""
    dt_from = datetime.combine(date_from, datetime.min.time())
    dt_to = datetime.combine(date_to, datetime.max.time())

    gmv_q = await db.execute(
        select(func.coalesce(func.sum(Order.final_amount), 0)).where(
            Order.status.in_([OrderStatus.closed, OrderStatus.completed]),
            Order.created_at >= dt_from,
            Order.created_at <= dt_to,
        )
    )

    orders_q = await db.execute(
        select(func.count(Order.id)).where(
            Order.created_at >= dt_from,
            Order.created_at <= dt_to,
        )
    )

    new_users_q = await db.execute(
        select(func.count(User.id)).where(
            User.created_at >= dt_from,
            User.created_at <= dt_to,
        )
    )

    active_partners_q = await db.execute(
        select(func.count(Partner.id)).where(Partner.is_active.is_(True))
    )

    return PlatformStats(
        date_from=date_from,
        date_to=date_to,
        gmv=float(gmv_q.scalar_one()),
        total_orders=orders_q.scalar_one() or 0,
        new_users=new_users_q.scalar_one() or 0,
        active_partners=active_partners_q.scalar_one() or 0,
    )
