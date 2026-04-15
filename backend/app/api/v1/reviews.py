"""API маршруты отзывов."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import get_current_user
from app.models.review import ReviewStatus
from app.models.user import User
from app.schemas.review import (
    PartnerRatingSummary,
    ReviewCreate,
    ReviewFlagCreate,
    ReviewModerate,
    ReviewReply,
    ReviewResponse,
    ReviewUpdate,
)
from app.services import review as svc

router = APIRouter(tags=["reviews"])


@router.post("/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    return await svc.create_review(data.order_id, current_user.id, data, db)


@router.patch("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: uuid.UUID,
    data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    return await svc.update_review(review_id, current_user.id, data, db)


@router.get("/partners/{partner_id}/reviews", response_model=list[ReviewResponse])
async def get_partner_reviews(
    partner_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_session),
):
    return await svc.get_partner_reviews(partner_id, ReviewStatus.published, page, size, db)


@router.patch("/reviews/{review_id}/reply", response_model=ReviewResponse)
async def reply_to_review(
    review_id: uuid.UUID,
    data: ReviewReply,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    return await svc.reply_to_review(review_id, current_user.id, data, db)


@router.post("/reviews/{review_id}/flag", status_code=status.HTTP_204_NO_CONTENT)
async def flag_review(
    review_id: uuid.UUID,
    data: ReviewFlagCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    await svc.flag_review(review_id, current_user.id, data, db)


@router.post("/reviews/{review_id}/helpful")
async def toggle_helpful(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    count = await svc.toggle_helpful(review_id, current_user.id, db)
    return {"helpful_count": count}


@router.get("/partners/{partner_id}/rating", response_model=PartnerRatingSummary)
async def get_partner_rating(
    partner_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
):
    return await svc.get_rating_summary(partner_id, db)


# ── Маршруты модерации (только для администраторов) ────────────────────────

@router.patch("/admin/reviews/{review_id}/moderate", response_model=ReviewResponse)
async def moderate_review(
    review_id: uuid.UUID,
    data: ReviewModerate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Модерировать отзыв (требуется роль admin/moderator)."""
    if not getattr(current_user, "is_staff", False):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    return await svc.moderate_review(review_id, current_user.id, data, db)
