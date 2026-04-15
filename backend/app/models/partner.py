"""Модели партнёров, расписания и документов."""

import enum
import uuid
from datetime import time

from sqlalchemy import (
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class PartnerStatus(str, enum.Enum):
    draft = "draft"
    pending_verification = "pending_verification"
    active = "active"
    rejected = "rejected"
    suspended = "suspended"


class PartnerType(str, enum.Enum):
    legal = "legal"        # ООО / АО
    individual = "individual"  # ИП
    self_employed = "self_employed"  # Самозанятый


class Partner(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "partners"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    partner_type: Mapped[PartnerType] = mapped_column(Enum(PartnerType), nullable=False)
    status: Mapped[PartnerStatus] = mapped_column(
        Enum(PartnerStatus), default=PartnerStatus.draft, nullable=False
    )

    # Контакты
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(String(500))
    telegram: Mapped[str | None] = mapped_column(String(100))

    # Реквизиты
    inn: Mapped[str | None] = mapped_column(String(12))
    ogrn: Mapped[str | None] = mapped_column(String(15))
    legal_name: Mapped[str | None] = mapped_column(String(500))
    bank_account: Mapped[str | None] = mapped_column(String(20))
    bank_bik: Mapped[str | None] = mapped_column(String(9))

    # Адрес
    city: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(String(500))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)

    # Медиа
    logo_url: Mapped[str | None] = mapped_column(String(500))
    cover_url: Mapped[str | None] = mapped_column(String(500))

    # Рейтинг (денормализованный для быстрого поиска)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0)

    # Количество постов/мастеров
    slots_count: Mapped[int] = mapped_column(Integer, default=1)

    # Импорт из Яндекс.Карт (yamap.csv)
    yamap_id: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)
    working_hours: Mapped[str | None] = mapped_column(String(300))
    payment_methods: Mapped[str | None] = mapped_column(Text)
    whatsapp: Mapped[str | None] = mapped_column(String(100))
    vkontakte: Mapped[str | None] = mapped_column(String(300))
    region: Mapped[str | None] = mapped_column(String(150))
    subcategory: Mapped[str | None] = mapped_column(String(500))
    is_imported: Mapped[bool] = mapped_column(Boolean, default=False)
    yamap_reviews_count: Mapped[int] = mapped_column(Integer, default=0)

    # Подписка: free / basic / premium
    subscription_plan: Mapped[str] = mapped_column(String(20), default="free", nullable=False)

    # Комиссия платформы (%)
    commission_rate: Mapped[float] = mapped_column(Float, default=10.0)

    # Модерация
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    verified_at: Mapped[str | None] = mapped_column(String(50))

    __table_args__ = (
        Index("ix_partners_owner_id", "owner_id"),
        Index("ix_partners_status", "status"),
        Index("ix_partners_inn", "inn"),
        Index("ix_partners_yamap_id", "yamap_id"),
        Index("ix_partners_region", "region"),
    )

    # Relationships
    schedules: Mapped[list["WorkSchedule"]] = relationship(
        back_populates="partner", cascade="all, delete-orphan"
    )
    documents: Mapped[list["PartnerDocument"]] = relationship(
        back_populates="partner", cascade="all, delete-orphan"
    )
    services: Mapped[list["PartnerService"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="partner", cascade="all, delete-orphan"
    )
    products: Mapped[list["PartnerProduct"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="partner", cascade="all, delete-orphan"
    )
    slots: Mapped[list["Slot"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="partner", cascade="all, delete-orphan"
    )
    favorited_by: Mapped[list["FavoritePartner"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="partner"
    )


class WorkSchedule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "work_schedules"

    partner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), nullable=False
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Mon, 6=Sun
    open_time: Mapped[time | None] = mapped_column(Time)
    close_time: Mapped[time | None] = mapped_column(Time)
    is_day_off: Mapped[bool] = mapped_column(Boolean, default=False)
    break_start: Mapped[time | None] = mapped_column(Time)
    break_end: Mapped[time | None] = mapped_column(Time)

    __table_args__ = (
        UniqueConstraint("partner_id", "day_of_week", name="uq_work_schedule_partner_day"),
        Index("ix_work_schedules_partner_id", "partner_id"),
    )

    partner: Mapped["Partner"] = relationship(back_populates="schedules")


class PartnerDocument(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "partner_documents"

    partner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), nullable=False
    )
    doc_type: Mapped[str] = mapped_column(String(50), nullable=False)  # inn|ogrn|license|other
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(255))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (Index("ix_partner_documents_partner_id", "partner_id"),)

    partner: Mapped["Partner"] = relationship(back_populates="documents")
