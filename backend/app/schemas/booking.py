"""Схемы бронирования."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.booking import BookingStatus, SlotStatus


class SlotResponse(BaseModel):
    id: uuid.UUID
    start_time: datetime
    end_time: datetime
    status: SlotStatus

    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BaseModel):
    slot_id: uuid.UUID
    service_id: uuid.UUID | None = None
    vehicle_id: uuid.UUID | None = None
    client_comment: str | None = Field(None, max_length=1000)


class BookingUpdate(BaseModel):
    partner_comment: str | None = None
    status: BookingStatus | None = None
    cancel_reason: str | None = None


class BookingResponse(BaseModel):
    id: uuid.UUID
    slot_id: uuid.UUID
    user_id: uuid.UUID
    partner_id: uuid.UUID
    service_id: uuid.UUID | None
    vehicle_id: uuid.UUID | None
    status: BookingStatus
    client_comment: str | None
    partner_comment: str | None
    cancel_reason: str | None
    created_at: datetime
    slot: SlotResponse

    model_config = ConfigDict(from_attributes=True)


class SlotReserveRequest(BaseModel):
    slot_id: uuid.UUID


class SlotReserveResponse(BaseModel):
    slot_id: uuid.UUID
    reservation_key: str
    reserved_until: datetime
    ttl_seconds: int
