"""Сервис каталога: услуги и товары партнёра."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.catalog import (
    PartnerProduct,
    PartnerService,
    ProductCategory,
    ServiceCategory,
)
from app.schemas.catalog import (
    PartnerProductCreate,
    PartnerProductUpdate,
    PartnerServiceCreate,
    PartnerServiceUpdate,
)


async def get_service_tree(db: AsyncSession) -> list[ServiceCategory]:
    result = await db.execute(
        select(ServiceCategory)
        .where(ServiceCategory.parent_id.is_(None), ServiceCategory.is_active.is_(True))
        .order_by(ServiceCategory.sort_order)
    )
    return list(result.scalars().all())


async def get_product_tree(db: AsyncSession) -> list[ProductCategory]:
    result = await db.execute(
        select(ProductCategory)
        .where(ProductCategory.parent_id.is_(None), ProductCategory.is_active.is_(True))
        .order_by(ProductCategory.sort_order)
    )
    return list(result.scalars().all())


# ── Services ──────────────────────────────────────────────────────────────────

async def get_partner_services(
    db: AsyncSession, partner_id: uuid.UUID, include_inactive: bool = False
) -> list[PartnerService]:
    q = select(PartnerService).where(
        PartnerService.partner_id == partner_id,
        PartnerService.deleted_at.is_(None),
    )
    if not include_inactive:
        q = q.where(PartnerService.is_active.is_(True))
    result = await db.execute(q.order_by(PartnerService.created_at))
    return list(result.scalars().all())


async def create_service(
    db: AsyncSession, partner_id: uuid.UUID, data: PartnerServiceCreate
) -> PartnerService:
    service = PartnerService(partner_id=partner_id, **data.model_dump())
    db.add(service)
    await db.flush()
    return service


async def update_service(
    db: AsyncSession,
    service_id: uuid.UUID,
    partner_id: uuid.UUID,
    data: PartnerServiceUpdate,
) -> PartnerService:
    service = await _get_service(db, service_id, partner_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(service, field, value)
    await db.flush()
    return service


async def delete_service(
    db: AsyncSession, service_id: uuid.UUID, partner_id: uuid.UUID
) -> None:
    from datetime import datetime, timezone
    service = await _get_service(db, service_id, partner_id)
    service.deleted_at = datetime.now(timezone.utc)
    await db.flush()


async def _get_service(
    db: AsyncSession, service_id: uuid.UUID, partner_id: uuid.UUID
) -> PartnerService:
    result = await db.execute(
        select(PartnerService).where(
            PartnerService.id == service_id,
            PartnerService.deleted_at.is_(None),
        )
    )
    service = result.scalar_one_or_none()
    if not service:
        raise NotFoundError("Услуга не найдена")
    if service.partner_id != partner_id:
        raise PermissionDeniedError("Нет доступа")
    return service


# ── Products ──────────────────────────────────────────────────────────────────

async def get_partner_products(
    db: AsyncSession, partner_id: uuid.UUID, include_inactive: bool = False
) -> list[PartnerProduct]:
    q = select(PartnerProduct).where(
        PartnerProduct.partner_id == partner_id,
        PartnerProduct.deleted_at.is_(None),
    )
    if not include_inactive:
        q = q.where(PartnerProduct.is_active.is_(True))
    result = await db.execute(q.order_by(PartnerProduct.created_at))
    return list(result.scalars().all())


async def create_product(
    db: AsyncSession, partner_id: uuid.UUID, data: PartnerProductCreate
) -> PartnerProduct:
    product = PartnerProduct(partner_id=partner_id, **data.model_dump())
    db.add(product)
    await db.flush()
    return product


async def update_product(
    db: AsyncSession,
    product_id: uuid.UUID,
    partner_id: uuid.UUID,
    data: PartnerProductUpdate,
) -> PartnerProduct:
    product = await _get_product(db, product_id, partner_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(product, field, value)
    await db.flush()
    return product


async def delete_product(
    db: AsyncSession, product_id: uuid.UUID, partner_id: uuid.UUID
) -> None:
    from datetime import datetime, timezone
    product = await _get_product(db, product_id, partner_id)
    product.deleted_at = datetime.now(timezone.utc)
    await db.flush()


async def _get_product(
    db: AsyncSession, product_id: uuid.UUID, partner_id: uuid.UUID
) -> PartnerProduct:
    result = await db.execute(
        select(PartnerProduct).where(
            PartnerProduct.id == product_id,
            PartnerProduct.deleted_at.is_(None),
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise NotFoundError("Товар не найден")
    if product.partner_id != partner_id:
        raise PermissionDeniedError("Нет доступа")
    return product
