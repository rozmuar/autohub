"""Схемы пользователя."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    avatar_url: str | None = None


class UserUpdate(UserBase):
    notify_sms: bool | None = None
    notify_email: bool | None = None
    notify_push: bool | None = None
    notify_telegram: bool | None = None


class UserResponse(UserBase):
    id: uuid.UUID
    phone: str | None = None
    role: UserRole
    is_active: bool
    is_phone_verified: bool
    is_email_verified: bool
    notify_sms: bool
    notify_email: bool
    notify_push: bool
    notify_telegram: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserShortResponse(BaseModel):
    id: uuid.UUID
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    phone: str | None = None

    model_config = ConfigDict(from_attributes=True)
