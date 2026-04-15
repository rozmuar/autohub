"""API маршруты контента: новости, акции, блог."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.models.content import ContentType
from app.schemas.content import ArticleDetail, ArticleListResponse
from app.services import content as svc

router = APIRouter(prefix="/content", tags=["content"])


@router.get("", response_model=ArticleListResponse)
async def list_articles(
    type: ContentType = Query(ContentType.news, description="Тип контента: news | promo | blog"),
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=50),
    db: AsyncSession = Depends(get_session),
):
    """Список опубликованных статей с пагинацией."""
    return await svc.list_articles(db, content_type=type, page=page, size=size)


@router.get("/{slug}", response_model=ArticleDetail)
async def get_article(
    slug: str,
    db: AsyncSession = Depends(get_session),
):
    """Получить статью по slug."""
    return await svc.get_article_by_slug(db, slug)
