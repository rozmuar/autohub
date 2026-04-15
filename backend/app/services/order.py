"""Сервис заказов."""

import uuid
from decimal import Decimal, ROUND_HALF_UP

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError, NotFoundError
from app.models.order import Order, OrderItem, OrderStatus, OrderStatusHistory, OrderType
from app.schemas.order import OrderCreate, OrderResponse

logger = structlog.get_logger(__name__)

# Допустимые переходы состояний
_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.created: {OrderStatus.pending_payment, OrderStatus.cancelled},
    OrderStatus.pending_payment: {OrderStatus.confirmed, OrderStatus.cancelled},
    OrderStatus.confirmed: {OrderStatus.in_progress, OrderStatus.cancelled},
    OrderStatus.in_progress: {OrderStatus.completed, OrderStatus.disputed},
    OrderStatus.completed: {OrderStatus.paid, OrderStatus.disputed},
    OrderStatus.paid: {OrderStatus.closed},
    OrderStatus.cancelled: set(),
    OrderStatus.disputed: {OrderStatus.closed},
    OrderStatus.closed: set(),
}

_MAX_AMOUNT_CHANGE_PCT = Decimal("0.15")


def _generate_order_number() -> str:
    import random, string
    return "ORD-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


async def create_order(
    data: OrderCreate,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> OrderResponse:
    """Создаёт заказ с позициями."""
    amount = Decimal("0")
    items = []
    for item_data in data.items:
        price = Decimal(str(item_data.price))
        qty = item_data.quantity
        total = price * qty
        amount += total
        items.append(OrderItem(
            service_id=item_data.service_id,
            product_id=item_data.product_id,
            item_type=item_data.item_type,
            name=item_data.name,
            quantity=qty,
            price=float(price),
            total=float(total),
        ))

    amount = amount.quantize(Decimal("0.01"))

    order_type = (
        OrderType.service if all(i.item_type == "service" for i in items)
        else OrderType.product if all(i.item_type == "product" for i in items)
        else OrderType.mixed
    )

    order = Order(
        user_id=user_id,
        partner_id=data.partner_id,
        booking_id=data.booking_id,
        order_number=_generate_order_number(),
        order_type=order_type,
        amount_original=amount,
        amount_final=amount,
        comment=data.comment,
        status=OrderStatus.created,
    )
    db.add(order)
    await db.flush()

    for item in items:
        item.order_id = order.id
        db.add(item)

    await db.commit()
    await db.refresh(order)
    return OrderResponse.model_validate(order)


async def get_order(order_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> OrderResponse:
    q = await db.execute(select(Order).where(Order.id == order_id))
    order = q.scalar_one_or_none()
    if not order:
        raise NotFoundError("Заказ не найден")
    if order.user_id != user_id and not await _is_partner_owner(order.partner_id, user_id, db):
        raise BusinessError("Нет доступа")
    return OrderResponse.model_validate(order)


async def update_status(
    order_id: uuid.UUID,
    new_status: OrderStatus,
    changed_by_id: uuid.UUID,
    comment: str | None,
    db: AsyncSession,
) -> OrderResponse:
    q = await db.execute(select(Order).where(Order.id == order_id))
    order = q.scalar_one_or_none()
    if not order:
        raise NotFoundError("Заказ не найден")

    allowed = _TRANSITIONS.get(order.status, set())
    if new_status not in allowed:
        raise BusinessError(
            f"Переход {order.status.value} → {new_status.value} недопустим"
        )

    old_status = order.status
    order.status = new_status

    history = OrderStatusHistory(
        order_id=order.id,
        from_status=old_status,
        to_status=new_status,
        changed_by_id=changed_by_id,
        comment=comment,
    )
    db.add(history)
    await db.commit()
    await db.refresh(order)
    return OrderResponse.model_validate(order)


async def propose_amount_change(
    order_id: uuid.UUID,
    user_id: uuid.UUID,
    new_amount: Decimal,
    db: AsyncSession,
) -> OrderResponse:
    """
    Партнёр предлагает изменить сумму.
    Если <= 15% — авто-одобрение.
    Если > 15% — требуется подтверждение клиента.
    """
    q = await db.execute(select(Order).where(Order.id == order_id))
    order = q.scalar_one_or_none()
    if not order:
        raise NotFoundError("Заказ не найден")
    if not await _is_partner_owner(order.partner_id, user_id, db):
        raise BusinessError("Нет доступа")
    if not order.partner_can_change_amount:
        raise BusinessError("Изменение суммы недоступно для этого заказа")

    original = order.amount_original
    diff_pct = abs(new_amount - original) / original

    if diff_pct <= _MAX_AMOUNT_CHANGE_PCT:
        order.amount_final = new_amount.quantize(Decimal("0.01"))
        order.amount_change_requires_approval = False
        order.amount_change_approved = True
    else:
        order.amount_final = new_amount.quantize(Decimal("0.01"))
        order.amount_change_requires_approval = True
        order.amount_change_approved = False

    await db.commit()
    await db.refresh(order)
    return OrderResponse.model_validate(order)


async def approve_amount_change(
    order_id: uuid.UUID,
    user_id: uuid.UUID,
    approved: bool,
    db: AsyncSession,
) -> OrderResponse:
    q = await db.execute(select(Order).where(Order.id == order_id))
    order = q.scalar_one_or_none()
    if not order:
        raise NotFoundError("Заказ не найден")
    if order.user_id != user_id:
        raise BusinessError("Нет доступа")
    if not order.amount_change_requires_approval:
        raise BusinessError("Подтверждение не требуется")

    if approved:
        order.amount_change_approved = True
    else:
        # Откатываем сумму к оригинальной
        order.amount_final = order.amount_original
        order.amount_change_requires_approval = False
        order.amount_change_approved = False

    await db.commit()
    await db.refresh(order)
    return OrderResponse.model_validate(order)


async def _is_partner_owner(partner_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> bool:
    from app.models.partner import Partner
    q = await db.execute(
        select(Partner).where(Partner.id == partner_id, Partner.owner_id == user_id)
    )
    return q.scalar_one_or_none() is not None
