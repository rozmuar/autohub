"""Модели автомобилей и гаража."""

import uuid

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class CarBrand(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "car_brands"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str | None] = mapped_column(String(100))
    logo_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    models: Mapped[list["CarModel"]] = relationship(back_populates="brand")


class CarModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "car_models"

    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("car_brands.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    body_type: Mapped[str | None] = mapped_column(String(50))  # sedan, suv, hatchback...
    year_from: Mapped[int | None] = mapped_column(Integer)
    year_to: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("brand_id", "name", name="uq_car_model_brand_name"),
        Index("ix_car_models_brand_id", "brand_id"),
    )

    brand: Mapped["CarBrand"] = relationship(back_populates="models")
    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="car_model")


class Vehicle(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "vehicles"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    car_model_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("car_models.id", ondelete="SET NULL"), nullable=True
    )

    # Ручной ввод
    brand_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    vin: Mapped[str | None] = mapped_column(String(17), nullable=True)
    plate_number: Mapped[str | None] = mapped_column(String(20))

    # Технические характеристики
    engine_type: Mapped[str | None] = mapped_column(String(50))   # petrol|diesel|hybrid|electric
    engine_volume: Mapped[str | None] = mapped_column(String(10))  # 1.6, 2.0...
    transmission: Mapped[str | None] = mapped_column(String(20))   # manual|auto|cvt|robot
    drive_type: Mapped[str | None] = mapped_column(String(10))     # fwd|rwd|awd|4wd
    body_type: Mapped[str | None] = mapped_column(String(50))
    mileage: Mapped[int | None] = mapped_column(Integer)

    # Декодированные данные из VIN
    vin_decoded: Mapped[bool] = mapped_column(Boolean, default=False)

    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    nickname: Mapped[str | None] = mapped_column(String(100))

    __table_args__ = (
        Index("ix_vehicles_owner_id", "owner_id"),
        Index("ix_vehicles_vin", "vin"),
    )

    owner: Mapped["User"] = relationship(back_populates="vehicles")  # type: ignore[name-defined]  # noqa: F821
    car_model: Mapped["CarModel | None"] = relationship(back_populates="vehicles")
