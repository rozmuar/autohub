"""Сервис партнёров."""

import uuid
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    AlreadyExistsError,
    NotFoundError,
    PermissionDeniedError,
)
from app.models.partner import Partner, PartnerStatus, WorkSchedule
from app.models.user import UserRole
from app.schemas.partner import PartnerCreate, PartnerUpdate, WorkScheduleIn

logger = structlog.get_logger(__name__)


async def get_partner_by_id(db: AsyncSession, partner_id: uuid.UUID) -> Partner:
    result = await db.execute(
        select(Partner)
        .where(Partner.id == partner_id, Partner.deleted_at.is_(None))
        .options(selectinload(Partner.schedules))
    )
    partner = result.scalar_one_or_none()
    if not partner:
        raise NotFoundError("Партнёр не найден")
    return partner


async def get_my_partner(db: AsyncSession, user_id: uuid.UUID) -> Partner:
    result = await db.execute(
        select(Partner).where(Partner.owner_id == user_id, Partner.deleted_at.is_(None))
    )
    partner = result.scalar_one_or_none()
    if not partner:
        raise NotFoundError("Профиль партнёра не найден")
    return partner


async def create_partner(db: AsyncSession, user_id: uuid.UUID, data: PartnerCreate) -> Partner:
    # Один пользователь — один профиль партнёра
    existing = await db.execute(
        select(Partner).where(Partner.owner_id == user_id, Partner.deleted_at.is_(None))
    )
    if existing.scalar_one_or_none():
        raise AlreadyExistsError("Профиль партнёра уже существует")

    partner = Partner(
        owner_id=user_id,
        status=PartnerStatus.draft,
        **data.model_dump(),
    )
    db.add(partner)
    await db.flush()
    logger.info("partner.created", user_id=str(user_id), partner_id=str(partner.id))
    return partner


async def update_partner(
    db: AsyncSession, partner_id: uuid.UUID, user_id: uuid.UUID, data: PartnerUpdate,
    user_role: UserRole = UserRole.partner,
) -> Partner:
    partner = await get_partner_by_id(db, partner_id)

    if user_role not in (UserRole.admin, UserRole.moderator) and partner.owner_id != user_id:
        raise PermissionDeniedError("Нет доступа")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(partner, field, value)
    await db.flush()
    return partner


async def submit_for_verification(
    db: AsyncSession, partner_id: uuid.UUID, user_id: uuid.UUID
) -> Partner:
    partner = await get_my_partner(db, user_id)
    if partner.id != partner_id:
        raise PermissionDeniedError("Нет доступа")
    partner.status = PartnerStatus.pending_verification
    await db.flush()
    return partner


async def set_schedule(
    db: AsyncSession, partner_id: uuid.UUID, user_id: uuid.UUID, schedules: list[WorkScheduleIn]
) -> list[WorkSchedule]:
    partner = await get_my_partner(db, user_id)
    if partner.id != partner_id:
        raise PermissionDeniedError("Нет доступа")

    # Удаляем старое расписание
    existing = await db.execute(
        select(WorkSchedule).where(WorkSchedule.partner_id == partner_id)
    )
    for s in existing.scalars().all():
        await db.delete(s)
    await db.flush()

    new_schedules = []
    for sch in schedules:
        obj = WorkSchedule(partner_id=partner_id, **sch.model_dump())
        db.add(obj)
        new_schedules.append(obj)
    await db.flush()
    return new_schedules


async def update_location(
    db: AsyncSession,
    partner_id: uuid.UUID,
    user_id: uuid.UUID,
    latitude: float,
    longitude: float,
) -> Partner:
    partner = await get_my_partner(db, user_id)
    if partner.id != partner_id:
        raise PermissionDeniedError("Нет доступа")
    partner.latitude = latitude
    partner.longitude = longitude
    await db.flush()
    return partner
