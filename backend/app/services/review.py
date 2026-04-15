"""Сервис отзывов с модерацией и рейтингом партнёра."""

import uuid
from datetime import datetime

import structlog
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError, NotFoundError
from app.models.order import Order, OrderStatus
from app.models.partner import Partner
from app.models.review import Review, ReviewFlag, ReviewHelpful, ReviewStatus
from app.schemas.review import (
    PartnerRatingSummary,
    ReviewCreate,
    ReviewFlagCreate,
    ReviewModerate,
    ReviewReply,
    ReviewResponse,
    ReviewUpdate,
)

logger = structlog.get_logger(__name__)


async def create_review(
    order_id: uuid.UUID,
    author_id: uuid.UUID,
    data: ReviewCreate,
    db: AsyncSession,
) -> ReviewResponse:
    """Создаёт отзыв после закрытого заказа."""
    order_q = await db.execute(select(Order).where(Order.id == order_id))
    order = order_q.scalar_one_or_none()
    if not order:
        raise NotFoundError("Заказ не найден")
    if order.client_id != author_id:
        raise BusinessError("Вы не являетесь клиентом этого заказа")
    if order.status != OrderStatus.closed:
        raise BusinessError("Отзыв можно оставить только после закрытого заказа")

    # Один отзыв на заказ
    existing_q = await db.execute(select(Review).where(Review.order_id == order_id))
    if existing_q.scalar_one_or_none():
        raise BusinessError("Отзыв на этот заказ уже существует")

    review = Review(
        order_id=order_id,
        author_id=author_id,
        partner_id=order.partner_id,
        rating=data.rating,
        text=data.text,
        photos=data.photos or [],
        status=ReviewStatus.pending,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    logger.info("review_created", review_id=str(review.id))
    return ReviewResponse.model_validate(review)


async def get_partner_reviews(
    partner_id: uuid.UUID,
    status: ReviewStatus,
    page: int,
    size: int,
    db: AsyncSession,
) -> list[ReviewResponse]:
    q = (
        select(Review)
        .where(Review.partner_id == partner_id, Review.status == status)
        .order_by(Review.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(q)
    return [ReviewResponse.model_validate(r) for r in result.scalars().all()]


async def update_review(
    review_id: uuid.UUID,
    author_id: uuid.UUID,
    data: ReviewUpdate,
    db: AsyncSession,
) -> ReviewResponse:
    q = await db.execute(select(Review).where(Review.id == review_id))
    review = q.scalar_one_or_none()
    if not review:
        raise NotFoundError("Отзыв не найден")
    if review.author_id != author_id:
        raise BusinessError("Нет прав на редактирование")
    if review.status not in (ReviewStatus.pending, ReviewStatus.published):
        raise BusinessError("Нельзя редактировать модерированный отзыв")

    for field, val in data.model_dump(exclude_none=True).items():
        setattr(review, field, val)
    review.status = ReviewStatus.pending  # Требует повторной модерации
    await db.commit()
    await db.refresh(review)
    return ReviewResponse.model_validate(review)


async def reply_to_review(
    review_id: uuid.UUID,
    partner_id: uuid.UUID,
    data: ReviewReply,
    db: AsyncSession,
) -> ReviewResponse:
    q = await db.execute(select(Review).where(Review.id == review_id))
    review = q.scalar_one_or_none()
    if not review:
        raise NotFoundError("Отзыв не найден")
    if review.partner_id != partner_id:
        raise BusinessError("Это не ваш отзыв")
    if review.status != ReviewStatus.published:
        raise BusinessError("Нельзя отвечать на неопубликованный отзыв")

    review.partner_reply = data.text
    review.partner_replied_at = datetime.utcnow()
    await db.commit()
    await db.refresh(review)
    return ReviewResponse.model_validate(review)


async def moderate_review(
    review_id: uuid.UUID,
    moderator_id: uuid.UUID,
    data: ReviewModerate,
    db: AsyncSession,
) -> ReviewResponse:
    q = await db.execute(select(Review).where(Review.id == review_id))
    review = q.scalar_one_or_none()
    if not review:
        raise NotFoundError("Отзыв не найден")

    review.status = data.status
    review.moderated_by_id = moderator_id
    await db.commit()
    await db.refresh(review)

    if data.status == ReviewStatus.published:
        await _update_partner_rating(review.partner_id, db)
    return ReviewResponse.model_validate(review)


async def flag_review(
    review_id: uuid.UUID,
    user_id: uuid.UUID,
    data: ReviewFlagCreate,
    db: AsyncSession,
) -> None:
    q = await db.execute(select(Review).where(Review.id == review_id))
    if not q.scalar_one_or_none():
        raise NotFoundError("Отзыв не найден")

    # Уже пожаловался?
    existing_q = await db.execute(
        select(ReviewFlag).where(
            ReviewFlag.review_id == review_id,
            ReviewFlag.reported_by_id == user_id,
        )
    )
    if existing_q.scalar_one_or_none():
        raise BusinessError("Вы уже пожаловались на этот отзыв")

    flag = ReviewFlag(review_id=review_id, reported_by_id=user_id, reason=data.reason)
    db.add(flag)
    await db.commit()


async def toggle_helpful(
    review_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> int:
    """Ставит/снимает отметку «полезный». Возвращает новое количество."""
    q = await db.execute(
        select(ReviewHelpful).where(
            ReviewHelpful.review_id == review_id,
            ReviewHelpful.user_id == user_id,
        )
    )
    existing = q.scalar_one_or_none()

    if existing:
        await db.delete(existing)
        delta = -1
    else:
        db.add(ReviewHelpful(review_id=review_id, user_id=user_id))
        delta = 1

    await db.execute(
        update(Review)
        .where(Review.id == review_id)
        .values(helpful_count=Review.helpful_count + delta)
    )
    await db.commit()

    cnt_q = await db.execute(
        select(Review.helpful_count).where(Review.id == review_id)
    )
    return cnt_q.scalar_one()


async def get_rating_summary(
    partner_id: uuid.UUID, db: AsyncSession
) -> PartnerRatingSummary:
    """Возвращает сводку рейтинга партнёра."""
    q = await db.execute(
        select(
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("total"),
        ).where(
            Review.partner_id == partner_id,
            Review.status == ReviewStatus.published,
        )
    )
    row = q.one()
    avg = round(float(row.avg_rating or 0), 2)
    total = row.total or 0

    # Распределение 1-5
    dist_q = await db.execute(
        select(Review.rating, func.count(Review.id))
        .where(
            Review.partner_id == partner_id,
            Review.status == ReviewStatus.published,
        )
        .group_by(Review.rating)
    )
    distribution = {str(r): c for r, c in dist_q.all()}
    return PartnerRatingSummary(
        partner_id=partner_id,
        average_rating=avg,
        total_reviews=total,
        distribution={str(k): distribution.get(str(k), 0) for k in range(1, 6)},
    )


async def _update_partner_rating(partner_id: uuid.UUID, db: AsyncSession) -> None:
    """Пересчитывает и сохраняет средний рейтинг партнёра."""
    q = await db.execute(
        select(func.avg(Review.rating)).where(
            Review.partner_id == partner_id,
            Review.status == ReviewStatus.published,
        )
    )
    new_rating = q.scalar_one_or_none()
    if new_rating is not None:
        await db.execute(
            update(Partner)
            .where(Partner.id == partner_id)
            .values(rating=round(float(new_rating), 2))
        )
        await db.commit()
