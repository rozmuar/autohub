"""Сервис управления профилем пользователя."""

import uuid

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.user import FavoritePartner, User
from app.schemas.user import UserUpdate

logger = structlog.get_logger(__name__)


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User:
    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("Пользователь не найден")
    return user


async def update_profile(db: AsyncSession, user_id: uuid.UUID, data: UserUpdate) -> User:
    user = await get_user_by_id(db, user_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    await db.flush()
    logger.info("user.profile_updated", user_id=str(user_id))
    return user


async def update_avatar(db: AsyncSession, user_id: uuid.UUID, avatar_url: str) -> User:
    user = await get_user_by_id(db, user_id)
    user.avatar_url = avatar_url
    await db.flush()
    return user


async def delete_account(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Soft-delete + анонимизация ПДн (152-ФЗ)."""
    from datetime import datetime, timezone
    user = await get_user_by_id(db, user_id)
    user.deleted_at = datetime.now(timezone.utc)
    user.first_name = "Удалённый"
    user.last_name = "Пользователь"
    user.email = None
    user.avatar_url = None
    user.vk_id = None
    user.yandex_id = None
    user.esia_id = None
    logger.info("user.account_deleted", user_id=str(user_id))


async def add_favorite(db: AsyncSession, user_id: uuid.UUID, partner_id: uuid.UUID) -> None:
    existing = await db.execute(
        select(FavoritePartner).where(
            FavoritePartner.user_id == user_id,
            FavoritePartner.partner_id == partner_id,
        )
    )
    if not existing.scalar_one_or_none():
        db.add(FavoritePartner(user_id=user_id, partner_id=partner_id))
        await db.flush()


async def remove_favorite(db: AsyncSession, user_id: uuid.UUID, partner_id: uuid.UUID) -> None:
    result = await db.execute(
        select(FavoritePartner).where(
            FavoritePartner.user_id == user_id,
            FavoritePartner.partner_id == partner_id,
        )
    )
    fav = result.scalar_one_or_none()
    if fav:
        await db.delete(fav)
        await db.flush()


async def get_favorites(db: AsyncSession, user_id: uuid.UUID) -> list[FavoritePartner]:
    result = await db.execute(
        select(FavoritePartner).where(FavoritePartner.user_id == user_id)
    )
    return list(result.scalars().all())
