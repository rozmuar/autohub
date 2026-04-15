"""Схемы заказов."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus, OrderType


class OrderItemCreate(BaseModel):
    service_id: uuid.UUID | None = None
    product_id: uuid.UUID | None = None
    item_type: str  # service|product
    name: str
    quantity: int = Field(default=1, ge=1)
    price: float = Field(..., gt=0)


class OrderCreate(BaseModel):
    partner_id: uuid.UUID
    booking_id: uuid.UUID | None = None
    order_type: OrderType
    items: list[OrderItemCreate] = Field(..., min_length=1)
    promo_code: str | None = None
    client_comment: str | None = None


class OrderAmountUpdateRequest(BaseModel):
    """Партнёр изменяет итоговую сумму заказа."""
    new_amount: float = Field(..., gt=0)
    comment: str | None = None


class OrderAmountApprovalRequest(BaseModel):
    """Клиент одобряет/отклоняет изменение суммы."""
    approved: bool
    comment: str | None = None


class OrderStatusUpdateRequest(BaseModel):
    status: OrderStatus
    comment: str | None = None


class OrderItemResponse(BaseModel):
    id: uuid.UUID
    item_type: str
    name: str
    quantity: int
    price: float
    total: float

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: uuid.UUID
    order_number: str
    partner_id: uuid.UUID
    user_id: uuid.UUID
    booking_id: uuid.UUID | None
    order_type: OrderType
    status: OrderStatus
    amount_original: float
    amount_final: float
    amount_paid: float
    commission_amount: float
    discount_amount: float
    promo_code: str | None
    client_comment: str | None
    partner_comment: str | None
    cancel_reason: str | None
    amount_change_requires_approval: bool
    amount_change_approved: bool | None
    work_order_pdf_url: str | None
    items: list[OrderItemResponse] = []
    created_at: datetime
    completed_at: datetime | None
    closed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
