"""Схемы каталога услуг и товаров."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ServiceCategoryResponse(BaseModel):
    id: uuid.UUID
    parent_id: uuid.UUID | None
    name: str
    slug: str
    icon_url: str | None
    sort_order: int
    children: list["ServiceCategoryResponse"] = []

    model_config = ConfigDict(from_attributes=True)


ServiceCategoryResponse.model_rebuild()


class PartnerServiceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category_id: uuid.UUID | None = None
    price_min: float = Field(..., gt=0)
    price_max: float | None = Field(None, gt=0)
    duration_minutes: int = Field(default=60, ge=5, le=1440)
    compatible_brands: list[str] | None = None


class PartnerServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: uuid.UUID | None = None
    price_min: float | None = Field(None, gt=0)
    price_max: float | None = None
    duration_minutes: int | None = Field(None, ge=5, le=1440)
    is_active: bool | None = None
    compatible_brands: list[str] | None = None


class PartnerServiceResponse(BaseModel):
    id: uuid.UUID
    partner_id: uuid.UUID
    name: str
    description: str | None
    category_id: uuid.UUID | None
    price_min: float
    price_max: float | None
    duration_minutes: int
    is_active: bool
    compatible_brands: list[str] | None

    model_config = ConfigDict(from_attributes=True)


class ProductCategoryResponse(BaseModel):
    id: uuid.UUID
    parent_id: uuid.UUID | None
    name: str
    slug: str
    icon_url: str | None
    sort_order: int
    children: list["ProductCategoryResponse"] = []

    model_config = ConfigDict(from_attributes=True)


ProductCategoryResponse.model_rebuild()


class PartnerProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category_id: uuid.UUID | None = None
    article: str | None = None
    oem_numbers: list[str] | None = None
    brand: str | None = None
    price: float = Field(..., gt=0)
    stock_count: int = Field(default=0, ge=0)
    compatible_brands: list[str] | None = None


class PartnerProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: uuid.UUID | None = None
    article: str | None = None
    oem_numbers: list[str] | None = None
    brand: str | None = None
    price: float | None = Field(None, gt=0)
    stock_count: int | None = Field(None, ge=0)
    is_active: bool | None = None
    compatible_brands: list[str] | None = None


class PartnerProductResponse(BaseModel):
    id: uuid.UUID
    partner_id: uuid.UUID
    name: str
    description: str | None
    category_id: uuid.UUID | None
    article: str | None
    oem_numbers: list[str] | None
    brand: str | None
    price: float
    stock_count: int
    is_active: bool
    image_url: str | None
    compatible_brands: list[str] | None

    model_config = ConfigDict(from_attributes=True)
