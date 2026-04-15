"""Эндпоинты платежей."""

import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.payment import PaymentMethod
from app.models.user import User
from app.schemas.payment import (
    PaymentCreateRequest,
    PaymentResponse,
    PromoCodeCheckRequest,
    PromoCodeCheckResponse,
)
from app.services import payment as payment_service

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    body: PaymentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await payment_service.create_payment(
        order_id=body.order_id,
        method=body.method,
        user_id=current_user.id,
        db=db,
        is_prepayment=body.is_prepayment,
    )


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def payment_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_yookassa_signature: str = Header(default=""),
):
    raw = await request.body()
    await payment_service.handle_webhook(raw, x_yookassa_signature, db)
    return {"ok": True}


@router.post("/promo/check", response_model=PromoCodeCheckResponse)
async def check_promo(
    body: PromoCodeCheckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from decimal import Decimal
    return await payment_service.check_promo(body.code, Decimal(str(body.order_amount)), current_user.id, db)
