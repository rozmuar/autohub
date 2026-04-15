"""Сервис контента: новости, акции, блог."""

import math

from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Article, ContentType
from app.schemas.content import ArticleDetail, ArticleListItem, ArticleListResponse


async def list_articles(
    db: AsyncSession,
    content_type: ContentType,
    page: int = 1,
    size: int = 12,
) -> ArticleListResponse:
    base_q = (
        select(Article)
        .where(Article.content_type == content_type, Article.is_published.is_(True))
        .order_by(Article.published_at.desc().nullslast(), Article.created_at.desc())
    )
    count_q = select(func.count()).select_from(
        select(Article.id)
        .where(Article.content_type == content_type, Article.is_published.is_(True))
        .subquery()
    )
    total: int = (await db.execute(count_q)).scalar_one()
    rows = (
        await db.execute(base_q.offset((page - 1) * size).limit(size))
    ).scalars().all()

    return ArticleListResponse(
        items=[ArticleListItem.model_validate(r) for r in rows],
        total=total,
        page=page,
        size=size,
        pages=max(1, math.ceil(total / size)),
    )


async def get_article_by_slug(db: AsyncSession, slug: str) -> ArticleDetail:
    row = (
        await db.execute(
            select(Article).where(Article.slug == slug, Article.is_published.is_(True))
        )
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Статья не найдена")

    # Инкремент просмотров
    await db.execute(
        update(Article).where(Article.id == row.id).values(views_count=Article.views_count + 1)
    )
    await db.commit()
    await db.refresh(row)

    return ArticleDetail.model_validate(row)
