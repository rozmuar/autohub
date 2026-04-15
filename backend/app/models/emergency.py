"""Модели экстренной помощи."""

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


class EmergencyType(str, enum.Enum):
    tow_truck = "tow_truck"       # Эвакуатор
    jump_start = "jump_start"     # Прикурить
    fuel = "fuel"                 # Топливо
    tire = "tire"                 # Шиномонтаж на месте
    stuck = "stuck"               # Застрял
    other = "other"               # Прочее


class EmergencyStatus(str, enum.Enum):
    searching = "searching"       # Ищем партнёра
    partner_found = "partner_found"   # Партнёр найден, едет
    in_progress = "in_progress"   # Работа выполняется
    completed = "completed"       # Завершено
    cancelled = "cancelled"       # Отменено клиентом
    no_response = "no_response"   # Никто не откликнулся


class EmergencyRequest(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "emergency_requests"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    emergency_type: Mapped[EmergencyType] = mapped_column(
        Enum(EmergencyType), nullable=False
    )
    status: Mapped[EmergencyStatus] = mapped_column(
        Enum(EmergencyStatus), default=EmergencyStatus.searching, nullable=False
    )

    # Геолокация клиента
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str | None] = mapped_column(String(500))

    description: Mapped[str | None] = mapped_column(Text)

    # Принятый партнёр
    accepted_partner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id", ondelete="SET NULL"), nullable=True
    )
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    estimated_arrival_minutes: Mapped[int | None] = mapped_column(Integer)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Текущий радиус поиска (расширяется 15 → 30 км)
    search_radius_km: Mapped[int] = mapped_column(Integer, default=15)
    broadcast_count: Mapped[int] = mapped_column(Integer, default=0)

    # Итоговая сумма
    final_amount: Mapped[float | None] = mapped_column(Float)
    order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (
        Index("ix_emergency_requests_user_id", "user_id"),
        Index("ix_emergency_requests_status", "status"),
    )

    responses: Mapped[list["EmergencyResponse"]] = relationship(
        back_populates="request", cascade="all, delete-orphan"
    )


class EmergencyResponse(Base, UUIDMixin, TimestampMixin):
    """Отклик партнёра на экстренный запрос."""

    __tablename__ = "emergency_responses"

    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("emergency_requests.id", ondelete="CASCADE"), nullable=False
    )
    partner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), nullable=False
    )

    estimated_arrival_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    proposed_price: Mapped[float | None] = mapped_column(Float)
    comment: Mapped[str | None] = mapped_column(Text)

    # accepted — принят клиентом, rejected — отклонён, pending — ожидает
    is_accepted: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    # Истёк ли таймер (60 сек)
    timed_out: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        Index("ix_emergency_responses_request_id", "request_id"),
        Index("ix_emergency_responses_partner_id", "partner_id"),
    )

    request: Mapped["EmergencyRequest"] = relationship(back_populates="responses")


class PartnerLocation(Base, UUIDMixin, TimestampMixin):
    """Текущая геолокация партнёра (обновляется в real-time)."""

    __tablename__ = "partner_locations"

    partner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"),
        nullable=False, unique=True
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (Index("ix_partner_locations_partner_id", "partner_id"),)
