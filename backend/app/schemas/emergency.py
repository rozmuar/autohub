"""Схемы экстренной помощи."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.emergency import EmergencyStatus, EmergencyType


class EmergencyCreateRequest(BaseModel):
    emergency_type: EmergencyType
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    description: str | None = None
    address: str | None = None


class EmergencyResponseCreate(BaseModel):
    estimated_arrival_minutes: int = Field(..., ge=1, le=240)
    proposed_price: float | None = Field(None, gt=0)
    comment: str | None = None


class EmergencyResponseItem(BaseModel):
    id: uuid.UUID
    partner_id: uuid.UUID
    estimated_arrival_minutes: int
    proposed_price: float | None
    comment: str | None
    is_accepted: bool | None
    timed_out: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmergencyRequestResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    emergency_type: EmergencyType
    status: EmergencyStatus
    latitude: float
    longitude: float
    address: str | None
    description: str | None
    accepted_partner_id: uuid.UUID | None
    accepted_at: datetime | None
    estimated_arrival_minutes: int | None
    search_radius_km: int
    broadcast_count: int
    final_amount: float | None
    responses: list[EmergencyResponseItem] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PartnerLocationUpdate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    is_online: bool = True
