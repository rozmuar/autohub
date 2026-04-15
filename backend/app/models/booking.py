"""Модели слотов и бронирований."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class SlotStatus(str, enum.Enum):
    available = "available"
    reserved = "reserved"    # временно заблокирован (5 мин)
    booked = "booked"        # подтверждён
    completed = "completed"
    cancelled = "cancelled"


class BookingStatus(str, enum.Enum):
    pending = "pending"          # ожидает оплаты
    confirmed = "confirmed"      # оплачен и подтверждён
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"


class Slot(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "slots"

    partner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), nullable=False
    )
    service_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("partner_services.id", ondelete="SET NULL"),
        nullable=True,
    )

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[SlotStatus] = mapped_column(
        Enum(SlotStatus), default=SlotStatus.available, nullable=False
    )

    # Временное резервирование: ключ в Redis для lock
    reservation_key: Mapped[str | None] = mapped_column(String(100))
    reserved_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reserved_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (
        Index("ix_slots_partner_id", "partner_id"),
        Index("ix_slots_start_time", "start_time"),
        Index("ix_slots_status", "status"),
    )

    partner: Mapped["Partner"] = relationship(back_populates="slots")  # type: ignore[name-defined]  # noqa: F821
    booking: Mapped["Booking | None"] = relationship(back_populates="slot")


class Booking(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "bookings"

    slot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("slots.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    partner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id", ondelete="RESTRICT"), nullable=False
    )
    service_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("partner_services.id", ondelete="SET NULL"),
        nullable=True,
    )
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
    )

    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus), default=BookingStatus.pending, nullable=False
    )
    client_comment: Mapped[str | None] = mapped_column(Text)
    partner_comment: Mapped[str | None] = mapped_column(Text)
    cancel_reason: Mapped[str | None] = mapped_column(Text)

    # Напоминания отправлены?
    reminder_24h_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_2h_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        Index("ix_bookings_user_id", "user_id"),
        Index("ix_bookings_partner_id", "partner_id"),
        Index("ix_bookings_status", "status"),
    )

    slot: Mapped["Slot"] = relationship(back_populates="booking")
    order: Mapped["Order | None"] = relationship(back_populates="booking")  # type: ignore[name-defined]  # noqa: F821
