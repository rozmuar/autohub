"""Схемы платежей."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.payment import PaymentMethod, PaymentStatus


class PaymentCreateRequest(BaseModel):
    order_id: uuid.UUID
    method: PaymentMethod = PaymentMethod.card
    is_prepayment: bool = False
    prepayment_percent: int = Field(default=100, ge=20, le=100)
    return_url: str | None = None


class PaymentResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    status: PaymentStatus
    method: PaymentMethod
    amount: float
    currency: str
    confirmation_url: str | None
    yookassa_payment_id: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromoCodeCheckRequest(BaseModel):
    code: str
    order_amount: float = Field(..., gt=0)


class PromoCodeCheckResponse(BaseModel):
    is_valid: bool
    discount_type: str | None = None
    discount_value: float | None = None
    discount_amount: float | None = None
    error: str | None = None
