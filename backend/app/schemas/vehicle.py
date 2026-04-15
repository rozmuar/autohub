"""Схемы транспортных средств."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VehicleCreate(BaseModel):
    brand_name: str = Field(..., min_length=1, max_length=100)
    model_name: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1900, le=2030)
    vin: str | None = Field(None, min_length=17, max_length=17)
    plate_number: str | None = None
    engine_type: str | None = None
    engine_volume: str | None = None
    transmission: str | None = None
    drive_type: str | None = None
    body_type: str | None = None
    mileage: int | None = None
    nickname: str | None = None
    is_primary: bool = False
    vin_decoded: bool = False


class VehicleUpdate(BaseModel):
    brand_name: str | None = None
    model_name: str | None = None
    year: int | None = Field(None, ge=1900, le=2030)
    vin: str | None = None
    plate_number: str | None = None
    engine_type: str | None = None
    engine_volume: str | None = None
    transmission: str | None = None
    drive_type: str | None = None
    body_type: str | None = None
    mileage: int | None = None
    nickname: str | None = None
    is_primary: bool | None = None


class VehicleResponse(BaseModel):
    id: uuid.UUID
    brand_name: str
    model_name: str
    year: int
    vin: str | None
    plate_number: str | None
    engine_type: str | None
    engine_volume: str | None
    transmission: str | None
    drive_type: str | None
    body_type: str | None
    mileage: int | None
    nickname: str | None
    is_primary: bool
    vin_decoded: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CarBrandResponse(BaseModel):
    id: uuid.UUID
    name: str
    name_en: str | None
    country: str | None
    logo_url: str | None

    model_config = ConfigDict(from_attributes=True)


class CarModelResponse(BaseModel):
    id: uuid.UUID
    name: str
    body_type: str | None
    year_from: int | None
    year_to: int | None

    model_config = ConfigDict(from_attributes=True)
