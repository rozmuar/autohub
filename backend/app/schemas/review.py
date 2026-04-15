"""Схемы отзывов."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.review import ReviewStatus


class ReviewCreate(BaseModel):
    order_id: uuid.UUID
    rating: int = Field(..., ge=1, le=5)
    text: str | None = Field(None, max_length=3000)


class ReviewUpdate(BaseModel):
    text: str | None = Field(None, max_length=3000)


class ReviewReply(BaseModel):
    partner_reply: str = Field(..., min_length=1, max_length=2000)


class ReviewModerate(BaseModel):
    action: str  # "approve" | "reject"
    rejection_reason: str | None = None


class ReviewFlagCreate(BaseModel):
    reason: str = Field(..., min_length=5, max_length=255)


class ReviewResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    author_id: uuid.UUID
    partner_id: uuid.UUID
    rating: int
    text: str | None
    status: ReviewStatus
    partner_reply: str | None
    partner_replied_at: datetime | None
    helpful_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PartnerRatingSummary(BaseModel):
    partner_id: uuid.UUID
    average_rating: float
    reviews_count: int
    rating_distribution: dict[int, int]   # {5: 20, 4: 10, ...}
