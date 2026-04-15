"""Эндпоинты заказов."""

import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.order import (
    OrderAmountApprovalRequest,
    OrderAmountUpdateRequest,
    OrderCreate,
    OrderResponse,
    OrderStatusUpdateRequest,
)
from app.services import order as order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    body: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await order_service.create_order(body, current_user.id, db)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await order_service.get_order(order_id, current_user.id, db)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_status(
    order_id: uuid.UUID,
    body: OrderStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await order_service.update_status(order_id, body.status, current_user.id, body.comment, db)


@router.patch("/{order_id}/amount", response_model=OrderResponse)
async def propose_amount_change(
    order_id: uuid.UUID,
    body: OrderAmountUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from decimal import Decimal
    return await order_service.propose_amount_change(order_id, current_user.id, Decimal(str(body.new_amount)), db)


@router.post("/{order_id}/amount/approve", response_model=OrderResponse)
async def approve_amount(
    order_id: uuid.UUID,
    body: OrderAmountApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await order_service.approve_amount_change(order_id, current_user.id, body.approved, db)
