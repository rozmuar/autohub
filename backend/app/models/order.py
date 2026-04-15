"""Модели заказов и истории изменений."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class OrderStatus(str, enum.Enum):
    created = "created"
    pending_payment = "pending_payment"
    confirmed = "confirmed"
    in_progress = "in_progress"
    completed = "completed"
    paid = "paid"
    closed = "closed"
    cancelled = "cancelled"
    disputed = "disputed"


class OrderType(str, enum.Enum):
    service = "service"
    product = "product"
    mixed = "mixed"


class Order(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "orders"

    booking_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True, unique=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    partner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id", ondelete="RESTRICT"), nullable=False
    )

    order_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    order_type: Mapped[OrderType] = mapped_column(Enum(OrderType), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.created, nullable=False
    )

    # Сумма
    amount_original: Mapped[float] = mapped_column(Float, nullable=False)
    amount_final: Mapped[float] = mapped_column(Float, nullable=False)
    amount_paid: Mapped[float] = mapped_column(Float, default=0.0)
    commission_amount: Mapped[float] = mapped_column(Float, default=0.0)

    # Правило +15%
    partner_can_change_amount: Mapped[bool] = mapped_column(Boolean, default=True)
    amount_change_requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    amount_change_approved: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Промокод
    promo_code: Mapped[str | None] = mapped_column(String(50))
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0)

    # Документы
    work_order_pdf_url: Mapped[str | None] = mapped_column(String(500))

    # Комментарии
    client_comment: Mapped[str | None] = mapped_column(Text)
    partner_comment: Mapped[str | None] = mapped_column(Text)
    cancel_reason: Mapped[str | None] = mapped_column(Text)

    # Дата завершения
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_orders_user_id", "user_id"),
        Index("ix_orders_partner_id", "partner_id"),
        Index("ix_orders_status", "status"),
        Index("ix_orders_order_number", "order_number"),
    )

    booking: Mapped["Booking | None"] = relationship(back_populates="order")  # type: ignore[name-defined]  # noqa: F821
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    status_history: Mapped[list["OrderStatusHistory"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    payment: Mapped["Payment | None"] = relationship(back_populates="order")  # type: ignore[name-defined]  # noqa: F821


class OrderItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "order_items"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    service_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("partner_services.id", ondelete="SET NULL"),
        nullable=True,
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("partner_products.id", ondelete="SET NULL"),
        nullable=True,
    )

    item_type: Mapped[str] = mapped_column(String(20), nullable=False)  # service|product
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (Index("ix_order_items_order_id", "order_id"),)

    order: Mapped["Order"] = relationship(back_populates="items")


class OrderStatusHistory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "order_status_history"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    from_status: Mapped[str | None] = mapped_column(String(50))
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    comment: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (Index("ix_order_status_history_order_id", "order_id"),)

    order: Mapped["Order"] = relationship(back_populates="status_history")
