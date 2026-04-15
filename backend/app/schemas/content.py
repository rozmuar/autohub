"""Pydantic-схемы контента."""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.content import ContentType


class ArticleListItem(BaseModel):
    id: uuid.UUID
    content_type: ContentType
    title: str
    slug: str
    excerpt: str | None
    cover_image: str | None
    published_at: datetime | None
    views_count: int
    promo_valid_until: datetime | None
    promo_discount_pct: int | None
    author_name: str | None
    tags: str | None

    model_config = {"from_attributes": True}


class ArticleDetail(ArticleListItem):
    body: str
    created_at: datetime


class ArticleListResponse(BaseModel):
    items: list[ArticleListItem]
    total: int
    page: int
    size: int
    pages: int
