"""Утилиты безопасности: хэширование паролей, JWT, зависимости FastAPI."""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

from app.config import settings
from app.core.exceptions import InvalidTokenError, TokenExpiredError

# ─── Пароли ──────────────────────────────────────────────────────
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


# ─── JWT ──────────────────────────────────────────────────────────

def create_access_token(payload: dict[str, Any]) -> str:
    data = payload.copy()
    data["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    data["type"] = "access"
    return jwt.encode(data, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(payload: dict[str, Any]) -> str:
    data = payload.copy()
    data["exp"] = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )
    data["type"] = "refresh"
    return jwt.encode(data, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    """Декодирует JWT и проверяет тип. Выбрасывает AppError при ошибке."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError as e:
        raise TokenExpiredError() from e
    except jwt.InvalidTokenError as e:
        raise InvalidTokenError() from e

    if payload.get("type") != expected_type:
        raise InvalidTokenError(f"Expected token type '{expected_type}'")

    return payload


# ─── FastAPI зависимости ──────────────────────────────────────────

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict[str, Any]:
    """Проверяет Bearer-токен и возвращает payload. Используется как Depends."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return decode_token(credentials.credentials, expected_type="access")


async def get_optional_user_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict[str, Any] | None:
    """Опциональная аутентификация — не выбрасывает ошибку если токена нет."""
    if credentials is None:
        return None
    try:
        return decode_token(credentials.credentials, expected_type="access")
    except (TokenExpiredError, InvalidTokenError):
        return None


async def get_current_user(
    payload: dict[str, Any] = Depends(get_current_user_payload),
):
    """Зависимость FastAPI: извлекает объект User из БД по JWT."""
    from sqlalchemy import select
    from app.database import get_db
    from app.models.user import User

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
        )
    # Используем get_db dependency напрямую (только в контексте FastAPI)
    # Здесь мы подключаемся через Depends(get_db) — внедрить БД в get_current_user
    # через двойной Depends невозможно напрямую, поэтому создаём сессию вручную.
    from app.database import _session_factory
    if _session_factory is None:
        raise HTTPException(status_code=503, detail="DB not ready")
    async with _session_factory() as session:
        q = await session.execute(select(User).where(User.id == user_id))
        user = q.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или заблокирован",
        )
    return user


async def get_current_user_ws(token: str, db) -> "User | None":
    """Аутентификация для WebSocket через query-параметр token.
    Возвращает None при ошибке (чтобы закрыть соединение с кодом 4001).
    """
    from sqlalchemy import select
    from app.models.user import User

    try:
        payload = decode_token(token, expected_type="access")
    except Exception:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    q = await db.execute(select(User).where(User.id == user_id))
    user = q.scalar_one_or_none()
    if not user or not user.is_active:
        return None
    return user
