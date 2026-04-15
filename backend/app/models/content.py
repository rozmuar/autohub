"""Модели контента: новости, акции, блог."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class ContentType(str, enum.Enum):
    news = "news"
    promo = "promo"
    blog = "blog"


class Article(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "articles"

    content_type: Mapped[ContentType] = mapped_column(Enum(ContentType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    excerpt: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    cover_image: Mapped[str | None] = mapped_column(String(500))
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    views_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Поля акций
    promo_valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    promo_discount_pct: Mapped[int | None] = mapped_column(Integer)

    # Поля блога
    author_name: Mapped[str | None] = mapped_column(String(100))
    tags: Mapped[str | None] = mapped_column(String(500))  # через запятую

    __table_args__ = (
        Index("ix_articles_content_type_published", "content_type", "is_published"),
    )
