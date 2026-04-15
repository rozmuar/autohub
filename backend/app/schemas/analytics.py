"""Схемы аналитики."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class DateRangeRequest(BaseModel):
    date_from: date
    date_to: date


class RevenuePoint(BaseModel):
    date: date
    revenue: float
    orders_count: int


class PartnerDashboard(BaseModel):
    partner_id: uuid.UUID
    period_from: date
    period_to: date

    total_revenue: float
    total_orders: int
    average_check: float
    completed_orders: int
    cancelled_orders: int

    revenue_chart: list[RevenuePoint] = []
    top_services: list[dict] = []    # [{name, revenue, count}]
    top_products: list[dict] = []


class ConversionStats(BaseModel):
    partner_id: uuid.UUID
    profile_views: int
    search_appearances: int
    orders_created: int
    conversion_rate: float


class PlatformStats(BaseModel):
    date_from: date
    date_to: date
    total_gmv: float
    total_orders: int
    total_users: int
    new_users: int
    active_partners: int
    new_partners: int
    average_order_value: float
