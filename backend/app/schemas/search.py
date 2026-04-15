"""Схемы поиска."""

from pydantic import BaseModel, Field
import uuid


class SearchRequest(BaseModel):
    q: str | None = None
    category_slug: str | None = None
    city: str | None = None
    region: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    radius_km: float = Field(default=10.0, ge=0.5, le=100.0)
    price_min: float | None = None
    price_max: float | None = None
    rating_min: float | None = Field(None, ge=0.0, le=5.0)
    has_promo: bool | None = None
    sort_by: str = "relevance"  # relevance|price_asc|price_desc|rating|distance
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


class PartnerSearchResult(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    city: str | None
    address: str | None
    logo_url: str | None
    rating: float
    reviews_count: int
    yamap_reviews_count: int = 0
    distance_km: float | None = None
    min_price: float | None = None
    has_promo: bool = False
    categories: list[str] = []
    latitude: float | None = None
    longitude: float | None = None
    working_hours: str | None = None
    phone: str | None = None
    website: str | None = None
    subscription_plan: str = "free"


class SearchResponse(BaseModel):
    items: list[PartnerSearchResult]
    total: int
    page: int
    size: int


class MapPoint(BaseModel):
    id: uuid.UUID
    name: str
    address: str | None
    city: str | None
    latitude: float
    longitude: float
    rating: float
    reviews_count: int
    logo_url: str | None = None
    working_hours: str | None = None
    phone: str | None = None
    subscription_plan: str = "free"


class MapPointsResponse(BaseModel):
    items: list[MapPoint]
    total: int


class AutocompleteResponse(BaseModel):
    suggestions: list[str]
