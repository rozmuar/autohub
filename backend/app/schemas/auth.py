"""Схемы аутентификации."""

from pydantic import BaseModel, Field, field_validator
import re


class SendOTPRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)
    purpose: str = Field(default="login")  # login|register|reset|2fa

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        digits = re.sub(r"\D", "", v)
        if len(digits) not in (10, 11):
            raise ValueError("Некорректный номер телефона")
        if len(digits) == 10:
            return f"+7{digits}"
        if digits.startswith("8"):
            return f"+7{digits[1:]}"
        return f"+{digits}"


class VerifyOTPRequest(BaseModel):
    phone: str
    code: str = Field(..., min_length=4, max_length=6)
    purpose: str = Field(default="login")  # login|register|reset


class RegisterRequest(BaseModel):
    phone: str
    code: str = Field(..., min_length=4, max_length=6)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    password: str | None = Field(None, min_length=8, max_length=128)


class LoginRequest(BaseModel):
    phone: str
    password: str | None = Field(None, min_length=1)
    otp_code: str | None = Field(None, min_length=4, max_length=6)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # секунды


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class ResetPasswordRequest(BaseModel):
    phone: str
    code: str
    new_password: str = Field(..., min_length=8, max_length=128)
