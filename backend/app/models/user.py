"""Модели пользователей, ролей и сессий."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class UserRole(str, enum.Enum):
    client = "client"
    partner = "partner"
    expert = "expert"
    moderator = "moderator"
    admin = "admin"


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)

    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500))

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.client, nullable=False
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # 2FA
    is_2fa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # OAuth
    vk_id: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    yandex_id: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    esia_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)

    # Настройки уведомлений (JSON-like через строку флагов)
    notify_sms: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_email: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_push: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_telegram: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        Index("ix_users_phone", "phone"),
        Index("ix_users_email", "email"),
        Index("ix_users_role", "role"),
    )

    # Relationships
    sessions: Mapped[list["UserSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    otp_codes: Mapped[list["OTPCode"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    vehicles: Mapped[list["Vehicle"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="owner", cascade="all, delete-orphan"
    )
    favorites: Mapped[list["FavoritePartner"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        parts = filter(None, [self.first_name, self.last_name])
        return " ".join(parts) or "Пользователь"


class UserSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    refresh_token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    device_fingerprint: Mapped[str | None] = mapped_column(String(255))
    user_agent: Mapped[str | None] = mapped_column(String(500))
    ip_address: Mapped[str | None] = mapped_column(String(45))  # IPv6 max
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        Index("ix_user_sessions_user_id", "user_id"),
        Index("ix_user_sessions_refresh_token_hash", "refresh_token_hash"),
    )

    user: Mapped["User"] = relationship(back_populates="sessions")


class OTPCode(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "otp_codes"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    purpose: Mapped[str] = mapped_column(String(50), nullable=False)  # register|login|reset|2fa
    attempts: Mapped[int] = mapped_column(default=0)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (Index("ix_otp_codes_phone_purpose", "phone", "purpose"),)

    user: Mapped["User | None"] = relationship(back_populates="otp_codes")


class FavoritePartner(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "favorite_partners"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    partner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "partner_id", name="uq_favorite_partners"),
        Index("ix_favorite_partners_user_id", "user_id"),
    )

    user: Mapped["User"] = relationship(back_populates="favorites")
    partner: Mapped["Partner"] = relationship(back_populates="favorited_by")  # type: ignore[name-defined]  # noqa: F821
