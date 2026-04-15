"""Сервис аутентификации: OTP, JWT, OAuth."""

import hashlib
import random
import secrets
import string
from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import CacheService
from app.config import settings
from app.core.exceptions import (
    AlreadyExistsError,
    AuthError,
    InvalidTokenError,
    NotFoundError,
    RateLimitError,
    TokenExpiredError,
    ValidationError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import OTPCode, User, UserRole, UserSession
from app.schemas.auth import RegisterRequest, TokenResponse

logger = structlog.get_logger(__name__)

_otp_cache = CacheService(prefix="otp", ttl=300)  # 5 мин
_brute_cache = CacheService(prefix="brute", ttl=900)  # 15 мин

OTP_MAX_ATTEMPTS = 5
BRUTE_MAX_ATTEMPTS = 10
SLOT_RESERVE_SECONDS = 300


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _generate_otp(length: int = 4) -> str:
    return "".join(random.choices(string.digits, k=length))


async def send_otp(db: AsyncSession, phone: str, purpose: str) -> dict:
    """Генерирует и отправляет OTP (в dev — возвращает код напрямую)."""
    # Rate limit: не чаще 1 раза в минуту
    rate_key = f"rate:{phone}:{purpose}"
    if await _otp_cache.exists(rate_key):
        raise RateLimitError("Повторная отправка через 60 секунд")

    code = "0000" if settings.is_development else _generate_otp(4)
    code_hash = _hash_code(code)

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
    otp = OTPCode(
        phone=phone,
        code_hash=code_hash,
        purpose=purpose,
        expires_at=expires_at,
    )
    db.add(otp)
    await db.flush()

    # Ставим rate-limit ключ на 60 секунд
    await _otp_cache.set(rate_key, "1", ttl=60)

    # В dev — возвращаем код напрямую; в prod — отправляем SMS
    if settings.is_development:
        logger.info("otp.generated", phone=phone, purpose=purpose, code=code)
        return {"dev_code": code, "expires_in": 300}

    # TODO фаза 1: вызвать tasks.notifications.send_sms
    logger.info("otp.sent", phone=phone, purpose=purpose)
    return {"expires_in": 300}


async def verify_otp(db: AsyncSession, phone: str, code: str, purpose: str, *, mark_used: bool = True) -> OTPCode:
    """Проверяет OTP код. Выбрасывает исключение при ошибке."""
    brute_key = f"{phone}:{purpose}"
    attempts = await _brute_cache.get(brute_key)
    if attempts and int(attempts) >= OTP_MAX_ATTEMPTS:
        raise RateLimitError("Слишком много попыток. Запросите новый код.")

    result = await db.execute(
        select(OTPCode)
        .where(
            OTPCode.phone == phone,
            OTPCode.purpose == purpose,
            OTPCode.is_used.is_(False),
        )
        .order_by(OTPCode.created_at.desc())
        .limit(1)
    )
    otp = result.scalar_one_or_none()

    if not otp:
        raise AuthError("Код не найден. Запросите новый.")

    if otp.expires_at < datetime.now(timezone.utc):
        raise TokenExpiredError("Код истёк. Запросите новый.")

    if otp.code_hash != _hash_code(code):
        otp.attempts += 1
        new_count = int(attempts or 0) + 1
        await _brute_cache.set(brute_key, str(new_count), ttl=900)
        raise AuthError("Неверный код")

    if mark_used:
        otp.is_used = True
    await _brute_cache.delete(brute_key)
    return otp


async def register_user(db: AsyncSession, data: RegisterRequest) -> tuple[User, TokenResponse]:
    """Регистрация нового пользователя."""
    # Проверяем OTP (purpose login — единый флоу)
    await verify_otp(db, data.phone, data.code, "login")

    # Проверяем существование
    existing = await db.execute(select(User).where(User.phone == data.phone))
    if existing.scalar_one_or_none():
        raise AlreadyExistsError("Пользователь с таким телефоном уже существует")

    user = User(
        phone=data.phone,
        first_name=data.first_name,
        last_name=data.last_name,
        hashed_password=hash_password(data.password) if data.password else None,
        role=UserRole.client,
        is_phone_verified=True,
    )
    db.add(user)
    await db.flush()

    tokens = await _create_session(db, user, ip_address=None)
    logger.info("user.registered", user_id=str(user.id), phone=user.phone)
    return user, tokens


async def login_with_password(
    db: AsyncSession, phone: str, password: str, ip_address: str | None = None
) -> tuple[User, TokenResponse]:
    """Вход по телефону + паролю."""
    # Защита от брутфорса
    brute_key = f"login:{ip_address or phone}"
    attempts = await _brute_cache.get(brute_key)
    if attempts and int(attempts) >= BRUTE_MAX_ATTEMPTS:
        raise RateLimitError("Слишком много попыток входа. Попробуйте через 15 минут.")

    result = await db.execute(select(User).where(User.phone == phone, User.deleted_at.is_(None)))
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
        count = int(attempts or 0) + 1
        await _brute_cache.set(brute_key, str(count), ttl=900)
        raise AuthError("Неверный телефон или пароль")

    if not user.is_active:
        raise AuthError("Аккаунт заблокирован")

    await _brute_cache.delete(brute_key)
    tokens = await _create_session(db, user, ip_address=ip_address)
    return user, tokens


async def login_with_otp(
    db: AsyncSession, phone: str, code: str, ip_address: str | None = None
) -> tuple[User, TokenResponse]:
    """Вход по OTP (без пароля)."""
    await verify_otp(db, phone, code, "login")

    result = await db.execute(select(User).where(User.phone == phone, User.deleted_at.is_(None)))
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundError("Пользователь не найден. Зарегистрируйтесь.")
    if not user.is_active:
        raise AuthError("Аккаунт заблокирован")

    tokens = await _create_session(db, user, ip_address=ip_address)
    return user, tokens


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> TokenResponse:
    """Ротация refresh токена."""
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except (TokenExpiredError, InvalidTokenError):
        raise AuthError("Недействительный refresh токен")

    token_hash = _hash_code(refresh_token)
    result = await db.execute(
        select(UserSession).where(
            UserSession.refresh_token_hash == token_hash,
            UserSession.is_active.is_(True),
            UserSession.expires_at > datetime.now(timezone.utc),
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise AuthError("Сессия не найдена или истекла")

    # Инвалидируем старую сессию
    session.is_active = False
    await db.flush()

    # Получаем пользователя
    user = await db.get(User, payload["sub"])
    if not user or not user.is_active:
        raise AuthError("Пользователь не активен")

    return await _create_session(db, user)


async def logout(db: AsyncSession, refresh_token: str) -> None:
    """Инвалидирует конкретную сессию."""
    token_hash = _hash_code(refresh_token)
    result = await db.execute(
        select(UserSession).where(UserSession.refresh_token_hash == token_hash)
    )
    session = result.scalar_one_or_none()
    if session:
        session.is_active = False


async def logout_all(db: AsyncSession, user_id: str) -> None:
    """Инвалидирует все сессии пользователя."""
    result = await db.execute(
        select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.is_active.is_(True),
        )
    )
    for session in result.scalars().all():
        session.is_active = False


async def _create_session(
    db: AsyncSession,
    user: User,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> TokenResponse:
    payload = {
        "sub": str(user.id),
        "role": user.role.value,
        "phone": user.phone,
    }
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
    session = UserSession(
        user_id=user.id,
        refresh_token_hash=_hash_code(refresh_token),
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expires_at,
    )
    db.add(session)
    await db.flush()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )
