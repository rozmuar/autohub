"""Эндпоинты каталога услуг и товаров."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas import MessageResponse
from app.schemas.catalog import (
    PartnerProductCreate,
    PartnerProductResponse,
    PartnerProductUpdate,
    PartnerServiceCreate,
    PartnerServiceResponse,
    PartnerServiceUpdate,
    ProductCategoryResponse,
    ServiceCategoryResponse,
)
from app.services import catalog as catalog_service

router = APIRouter(prefix="/catalog", tags=["catalog"])

# ── Категории услуг ──────────────────────────────────────────────────────────

@router.get("/services/tree", response_model=list[ServiceCategoryResponse])
async def get_service_tree(db: AsyncSession = Depends(get_db)):
    return await catalog_service.get_service_tree(db)


# ── Услуги партнёра ──────────────────────────────────────────────────────────

@router.get("/partners/{partner_id}/services", response_model=list[PartnerServiceResponse])
async def list_partner_services(
    partner_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await catalog_service.get_partner_services(db, partner_id)


@router.post(
    "/partners/{partner_id}/services",
    response_model=PartnerServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_service(
    partner_id: uuid.UUID,
    body: PartnerServiceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await catalog_service.create_service(db, partner_id, current_user.id, body)


@router.patch("/services/{service_id}", response_model=PartnerServiceResponse)
async def update_service(
    service_id: uuid.UUID,
    body: PartnerServiceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await catalog_service.update_service(db, service_id, current_user.id, body)


@router.delete("/services/{service_id}", response_model=MessageResponse)
async def delete_service(
    service_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await catalog_service.delete_service(db, service_id, current_user.id)
    return MessageResponse(message="Услуга удалена")


# ── Категории товаров ────────────────────────────────────────────────────────

@router.get("/products/tree", response_model=list[ProductCategoryResponse])
async def get_product_tree(db: AsyncSession = Depends(get_db)):
    return await catalog_service.get_product_tree(db)


# ── Товары партнёра ──────────────────────────────────────────────────────────

@router.get("/partners/{partner_id}/products", response_model=list[PartnerProductResponse])
async def list_partner_products(
    partner_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await catalog_service.get_partner_products(db, partner_id)


@router.post(
    "/partners/{partner_id}/products",
    response_model=PartnerProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    partner_id: uuid.UUID,
    body: PartnerProductCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await catalog_service.create_product(db, partner_id, current_user.id, body)


@router.patch("/products/{product_id}", response_model=PartnerProductResponse)
async def update_product(
    product_id: uuid.UUID,
    body: PartnerProductUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await catalog_service.update_product(db, product_id, current_user.id, body)


@router.delete("/products/{product_id}", response_model=MessageResponse)
async def delete_product(
    product_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await catalog_service.delete_product(db, product_id, current_user.id)
    return MessageResponse(message="Товар удалён")
