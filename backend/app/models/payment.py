"""Модели платежей, выплат и промокодов."""

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
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    waiting_for_capture = "waiting_for_capture"
    succeeded = "succeeded"
    cancelled = "cancelled"
    refunded = "refunded"
    partially_refunded = "partially_refunded"


class PaymentMethod(str, enum.Enum):
    card = "card"
    sbp = "sbp"          # СБП QR
    cash = "cash"        # Оплата на месте
    wallet = "wallet"


class PayoutStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    succeeded = "succeeded"
    failed = "failed"


class Payment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "payments"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    # ЮKassa
    yookassa_payment_id: Mapped[str | None] = mapped_column(String(50), unique=True)
    yookassa_idempotency_key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), default=PaymentStatus.pending, nullable=False
    )
    method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod), default=PaymentMethod.card, nullable=False
    )

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RUB")

    # Предоплата или полная
    is_prepayment: Mapped[bool] = mapped_column(Boolean, default=False)
    prepayment_percent: Mapped[int] = mapped_column(Integer, default=100)

    # Подтверждение
    confirmation_url: Mapped[str | None] = mapped_column(String(1000))
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Возврат
    refund_amount: Mapped[float] = mapped_column(Float, default=0.0)
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # 54-ФЗ чек
    receipt_url: Mapped[str | None] = mapped_column(String(500))

    __table_args__ = (
        Index("ix_payments_order_id", "order_id"),
        Index("ix_payments_status", "status"),
        Index("ix_payments_yookassa_payment_id", "yookassa_payment_id"),
    )

    order: Mapped["Order"] = relationship(back_populates="payment")  # type: ignore[name-defined]  # noqa: F821
    payout: Mapped["Payout | None"] = relationship(back_populates="payment")


class Payout(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "payouts"

    payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("payments.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    partner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id", ondelete="RESTRICT"), nullable=False
    )

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    commission_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[PayoutStatus] = mapped_column(
        Enum(PayoutStatus), default=PayoutStatus.pending, nullable=False
    )

    yookassa_payout_id: Mapped[str | None] = mapped_column(String(50), unique=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (Index("ix_payouts_partner_id", "partner_id"),)

    payment: Mapped["Payment"] = relationship(back_populates="payout")


class PromoCode(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "promo_codes"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    discount_type: Mapped[str] = mapped_column(String(20), nullable=False)  # percent|fixed
    discount_value: Mapped[float] = mapped_column(Float, nullable=False)
    max_discount_amount: Mapped[float | None] = mapped_column(Float)

    min_order_amount: Mapped[float] = mapped_column(Float, default=0.0)
    max_uses: Mapped[int | None] = mapped_column(Integer)
    uses_count: Mapped[int] = mapped_column(Integer, default=0)
    max_uses_per_user: Mapped[int] = mapped_column(Integer, default=1)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (Index("ix_promo_codes_code", "code"),)
