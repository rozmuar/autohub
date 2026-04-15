"""Модели отзывов."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
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


class ReviewStatus(str, enum.Enum):
    pending = "pending"         # Ожидает модерации
    published = "published"     # Опубликован
    rejected = "rejected"       # Отклонён модератором
    hidden = "hidden"           # Скрыт (жалоба)


class Review(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "reviews"

    # Связи
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=False, unique=True   # Один отзыв на заказ
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    partner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), nullable=False
    )

    # Оценка от 1 до 5
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str | None] = mapped_column(Text)
    photos: Mapped[str | None] = mapped_column(String(2000))  # JSON-список URL через запятую

    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus), default=ReviewStatus.pending, nullable=False
    )

    # Ответ партнёра
    partner_reply: Mapped[str | None] = mapped_column(Text)
    partner_replied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Модерация
    moderated_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    moderated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(Text)

    # Полезность (лайки)
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating"),
        Index("ix_reviews_partner_id", "partner_id"),
        Index("ix_reviews_author_id", "author_id"),
        Index("ix_reviews_status", "status"),
    )

    flags: Mapped[list["ReviewFlag"]] = relationship(
        back_populates="review", cascade="all, delete-orphan"
    )


class ReviewFlag(Base, UUIDMixin, TimestampMixin):
    """Жалоба на отзыв."""

    __tablename__ = "review_flags"

    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False
    )
    reported_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint("review_id", "reported_by_id", name="uq_review_flag"),
        Index("ix_review_flags_review_id", "review_id"),
    )

    review: Mapped["Review"] = relationship(back_populates="flags")


class ReviewHelpful(Base, UUIDMixin, TimestampMixin):
    """Отметка «полезный отзыв»."""

    __tablename__ = "review_helpfuls"

    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("review_id", "user_id", name="uq_review_helpful"),
        Index("ix_review_helpfuls_review_id", "review_id"),
    )
