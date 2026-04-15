"""Модели каталога: категории, услуги, товары."""

import uuid

from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class ServiceCategory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "service_categories"

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("service_categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    icon_url: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (Index("ix_service_categories_parent_id", "parent_id"),)

    parent: Mapped["ServiceCategory | None"] = relationship(
        back_populates="children", remote_side="ServiceCategory.id"
    )
    children: Mapped[list["ServiceCategory"]] = relationship(back_populates="parent")
    services: Mapped[list["PartnerService"]] = relationship(back_populates="category")


class PartnerService(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "partner_services"

    partner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("service_categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    price_min: Mapped[float] = mapped_column(Float, nullable=False)
    price_max: Mapped[float | None] = mapped_column(Float)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Совместимые авто (хранятся как список brand_names или car_model_ids)
    compatible_brands: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    __table_args__ = (
        Index("ix_partner_services_partner_id", "partner_id"),
        Index("ix_partner_services_category_id", "category_id"),
    )

    partner: Mapped["Partner"] = relationship(back_populates="services")  # type: ignore[name-defined]  # noqa: F821
    category: Mapped["ServiceCategory | None"] = relationship(back_populates="services")


class ProductCategory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "product_categories"

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("product_categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    icon_url: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (Index("ix_product_categories_parent_id", "parent_id"),)

    parent: Mapped["ProductCategory | None"] = relationship(
        back_populates="children", remote_side="ProductCategory.id"
    )
    children: Mapped[list["ProductCategory"]] = relationship(back_populates="parent")
    products: Mapped[list["PartnerProduct"]] = relationship(back_populates="category")


class PartnerProduct(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "partner_products"

    partner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("product_categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    article: Mapped[str | None] = mapped_column(String(100))
    oem_numbers: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    image_url: Mapped[str | None] = mapped_column(String(500))

    # Совместимые авто
    compatible_brands: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    __table_args__ = (
        Index("ix_partner_products_partner_id", "partner_id"),
        Index("ix_partner_products_article", "article"),
    )

    partner: Mapped["Partner"] = relationship(back_populates="products")  # type: ignore[name-defined]  # noqa: F821
    category: Mapped["ProductCategory | None"] = relationship(back_populates="products")
