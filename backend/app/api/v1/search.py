"""Эндпоинты поиска."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.search import AutocompleteResponse, MapPointsResponse, SearchRequest, SearchResponse
from app.services import search as search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/partners", response_model=SearchResponse)
async def search_partners(
    req: SearchRequest = Depends(),
    db: AsyncSession = Depends(get_db),
):
    return await search_service.search_partners(req, db)


@router.get("/map-points", response_model=MapPointsResponse)
async def get_map_points(
    city: str | None = Query(None, description="Фильтр по городу"),
    region: str | None = Query(None, description="Фильтр по региону"),
    q: str | None = Query(None, description="Текстовый поиск по названию"),
    db: AsyncSession = Depends(get_db),
):
    """Все активные точки с координатами для карты (до 3000)."""
    return await search_service.get_map_points(db, city=city, region=region, q=q)


@router.get("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete(q: str = "", db: AsyncSession = Depends(get_db)):
    suggestions = await search_service.autocomplete(q)
    return AutocompleteResponse(suggestions=suggestions)
