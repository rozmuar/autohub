"""Сервис платежей (ЮKassa + промокоды)."""

import hashlib
import hmac
import json
import uuid
from decimal import Decimal

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import BusinessError, NotFoundError
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentMethod, PaymentStatus, PromoCode
from app.schemas.payment import PaymentResponse, PromoCodeCheckResponse

logger = structlog.get_logger(__name__)
settings = get_settings()


async def create_payment(
    order_id: uuid.UUID,
    method: PaymentMethod,
    user_id: uuid.UUID,
    db: AsyncSession,
    is_prepayment: bool = False,
) -> PaymentResponse:
    """Создаёт платёж через ЮKassa и возвращает confirmation_url."""
    order_q = await db.execute(select(Order).where(Order.id == order_id))
    order = order_q.scalar_one_or_none()
    if not order:
        raise NotFoundError("Заказ не найден")
    if order.user_id != user_id:
        raise BusinessError("Нет доступа")

    existing_q = await db.execute(select(Payment).where(Payment.order_id == order_id))
    if existing_q.scalar_one_or_none():
        raise BusinessError("Платёж для этого заказа уже существует")

    idempotency_key = str(uuid.uuid4())
    amount = order.amount_final

    payment = Payment(
        order_id=order_id,
        user_id=user_id,
        amount=float(amount),
        method=method,
        status=PaymentStatus.pending,
        is_prepayment=is_prepayment,
        yookassa_idempotency_key=idempotency_key,
    )

    # Интеграция с реальной ЮKassa (если настроена)
    yookassa_payment_id, confirmation_url = await _call_yookassa(
        amount=amount,
        method=method,
        order_number=order.order_number,
        idempotency_key=idempotency_key,
    )
    payment.yookassa_payment_id = yookassa_payment_id
    payment.confirmation_url = confirmation_url

    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return PaymentResponse.model_validate(payment)


async def _call_yookassa(
    amount: Decimal,
    method: PaymentMethod,
    order_number: str,
    idempotency_key: str,
) -> tuple[str | None, str | None]:
    """Вызывает ЮKassa API. В dev возвращает заглушку."""
    shop_id = getattr(settings, "yookassa_shop_id", None)
    secret_key = getattr(settings, "yookassa_secret_key", None)

    if not shop_id or not secret_key:
        # dev-режим: возвращаем заглушку
        fake_id = f"dev_{uuid.uuid4().hex[:8]}"
        return fake_id, f"https://yookassa.ru/checkout/payments/{fake_id}"

    try:
        import httpx
        payload = {
            "amount": {"value": str(amount.quantize(Decimal("0.01"))), "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": "https://autohub.ru/payment/result"},
            "capture": True,
            "description": f"Заказ {order_number}",
            "metadata": {"order_number": order_number},
        }
        if method == PaymentMethod.sbp:
            payload["payment_method_data"] = {"type": "sbp"}
        elif method == PaymentMethod.card:
            payload["payment_method_data"] = {"type": "bank_card"}

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.yookassa.ru/v3/payments",
                json=payload,
                auth=(shop_id, secret_key),
                headers={"Idempotence-Key": idempotency_key},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["id"], data["confirmation"]["confirmation_url"]
    except Exception as e:
        logger.error("yookassa.create_payment_error", error=str(e))
        raise BusinessError("Ошибка при создании платежа. Попробуйте позже.") from e


async def handle_webhook(
    raw_body: bytes,
    signature: str,
    db: AsyncSession,
) -> None:
    """Обрабатывает вебхук от ЮKassa с проверкой подписи."""
    secret_key = getattr(settings, "yookassa_secret_key", None)
    if secret_key:
        expected = hmac.new(secret_key.encode(), raw_body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise BusinessError("Неверная подпись вебхука")

    payload = json.loads(raw_body)
    event = payload.get("event")
    obj = payload.get("object", {})
    yookassa_payment_id = obj.get("id")
    if not yookassa_payment_id:
        return

    payment_q = await db.execute(
        select(Payment).where(Payment.yookassa_payment_id == yookassa_payment_id)
    )
    payment = payment_q.scalar_one_or_none()
    if not payment:
        logger.warning("webhook.payment_not_found", id=yookassa_payment_id)
        return

    status_map = {
        "payment.succeeded": PaymentStatus.succeeded,
        "payment.canceled": PaymentStatus.cancelled,
        "payment.waiting_for_capture": PaymentStatus.waiting_for_capture,
        "refund.succeeded": PaymentStatus.refunded,
    }
    new_status = status_map.get(event)
    if new_status:
        payment.status = new_status
        receipt_url = obj.get("receipt_registration", {}).get("pdf")
        if receipt_url:
            payment.receipt_url = receipt_url

        # Обновляем заказ
        if new_status == PaymentStatus.succeeded:
            order_q = await db.execute(select(Order).where(Order.id == payment.order_id))
            order = order_q.scalar_one_or_none()
            if order and order.status == OrderStatus.pending_payment:
                order.status = OrderStatus.confirmed

    await db.commit()


async def check_promo(
    code: str,
    amount: Decimal,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> PromoCodeCheckResponse:
    """Проверяет промокод и возвращает размер скидки."""
    from datetime import datetime
    now = datetime.utcnow()
    q = await db.execute(
        select(PromoCode).where(
            PromoCode.code == code,
            PromoCode.is_active.is_(True),
        )
    )
    promo = q.scalar_one_or_none()
    if not promo:
        return PromoCodeCheckResponse(is_valid=False, error="Промокод не найден")
    if promo.valid_from and promo.valid_from > now:
        return PromoCodeCheckResponse(is_valid=False, error="Промокод ещё не активен")
    if promo.valid_until and promo.valid_until < now:
        return PromoCodeCheckResponse(is_valid=False, error="Срок действия промокода истёк")
    if promo.max_uses and promo.uses_count >= promo.max_uses:
        return PromoCodeCheckResponse(is_valid=False, error="Промокод исчерпан")
    if promo.min_order_amount and amount < promo.min_order_amount:
        return PromoCodeCheckResponse(
            is_valid=False,
            error=f"Минимальная сумма заказа {promo.min_order_amount} ₽",
        )

    if promo.discount_type == "percent":
        discount = (amount * promo.discount_value / 100).quantize(Decimal("0.01"))
    else:
        discount = min(promo.discount_value, amount)

    return PromoCodeCheckResponse(
        is_valid=True,
        discount_amount=float(discount),
        discount_type=promo.discount_type,
        discount_value=promo.discount_value,
    )
