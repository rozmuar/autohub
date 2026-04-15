"""Схемы партнёров."""

import uuid
from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.partner import PartnerStatus, PartnerType


class WorkScheduleIn(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    open_time: time | None = None
    close_time: time | None = None
    is_day_off: bool = False
    break_start: time | None = None
    break_end: time | None = None


class WorkScheduleResponse(WorkScheduleIn):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


class PartnerCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    partner_type: PartnerType
    phone: str = Field(..., min_length=10, max_length=20)
    email: EmailStr | None = None
    inn: str | None = Field(None, min_length=10, max_length=12)
    city: str | None = None
    address: str | None = None
    slots_count: int = Field(default=1, ge=1, le=100)


class PartnerUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    website: str | None = None
    telegram: str | None = None
    inn: str | None = None
    ogrn: str | None = None
    legal_name: str | None = None
    bank_account: str | None = None
    bank_bik: str | None = None
    city: str | None = None
    address: str | None = None
    slots_count: int | None = Field(None, ge=1, le=100)


class PartnerResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    partner_type: PartnerType
    status: PartnerStatus
    phone: str
    email: str | None
    website: str | None
    city: str | None
    address: str | None
    latitude: float | None
    longitude: float | None
    logo_url: str | None
    cover_url: str | None
    rating: float
    reviews_count: int
    yamap_reviews_count: int = 0
    slots_count: int
    created_at: datetime
    # Новые поля
    region: str | None = None
    working_hours: str | None = None
    payment_methods: str | None = None
    whatsapp: str | None = None
    vkontakte: str | None = None
    subcategory: str | None = None
    is_imported: bool = False
    subscription_plan: str = "free"

    model_config = ConfigDict(from_attributes=True)


class PartnerShortResponse(BaseModel):
    id: uuid.UUID
    name: str
    city: str | None
    address: str | None
    logo_url: str | None
    rating: float
    reviews_count: int
    status: PartnerStatus

    model_config = ConfigDict(from_attributes=True)
