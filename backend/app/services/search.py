"""Сервис поиска через Elasticsearch + прямые запросы к БД."""

from typing import Any

import structlog
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import CacheService
from app.models.partner import Partner, PartnerStatus
from app.schemas.search import (
    MapPoint,
    MapPointsResponse,
    PartnerSearchResult,
    SearchRequest,
    SearchResponse,
)

logger = structlog.get_logger(__name__)
_search_cache = CacheService(prefix="search", ttl=300)
_map_cache = CacheService(prefix="map", ttl=600)


def _build_query(req: SearchRequest) -> dict[str, Any]:
    must: list[dict] = []
    filter_: list[dict] = []
    should: list[dict] = []

    if req.q:
        must.append({
            "multi_match": {
                "query": req.q,
                "fields": ["name^3", "description", "subcategory^2"],
                "type": "best_fields",
                "fuzziness": "AUTO",
            }
        })
    else:
        must.append({"match_all": {}})

    filter_.append({"term": {"status": "active"}})

    if req.latitude is not None and req.longitude is not None:
        filter_.append({
            "geo_distance": {
                "distance": f"{req.radius_km}km",
                "location": {"lat": req.latitude, "lon": req.longitude},
            }
        })

    if req.city:
        filter_.append({"term": {"city.keyword": req.city}})
    if req.region:
        filter_.append({"term": {"region.keyword": req.region}})
    if req.rating_min is not None:
        filter_.append({"range": {"rating": {"gte": req.rating_min}}})
    if req.has_promo:
        filter_.append({"term": {"has_promo": True}})

    sort_map = {
        "price_asc": [{"price_min": {"order": "asc"}}],
        "price_desc": [{"price_min": {"order": "desc"}}],
        "rating": [{"rating": {"order": "desc"}}],
        "distance": [{"_geo_distance": {
            "location": {"lat": req.latitude or 0, "lon": req.longitude or 0},
            "order": "asc",
        }}] if req.latitude else [],
    }
    sort = sort_map.get(req.sort_by, [{"_score": {"order": "desc"}}, {"rating": {"order": "desc"}}])

    return {
        "query": {"bool": {"must": must, "filter": filter_, "should": should}},
        "sort": sort,
        "from": (req.page - 1) * req.size,
        "size": req.size,
        "_source": [
            "id", "name", "description", "city", "address",
            "logo_url", "rating", "reviews_count", "has_promo", "categories",
            "latitude", "longitude", "working_hours", "phone",
            "yamap_reviews_count", "website", "subscription_plan",
        ],
    }


async def search_partners(req: SearchRequest, db: AsyncSession | None = None) -> SearchResponse:
    cache_key = f"partners:{req.model_dump_json()}"
    cached = await _search_cache.get(cache_key)
    if cached:
        import json
        data = json.loads(cached)
        return SearchResponse(**data)

    try:
        from app.search import get_es
        es = get_es()
        body = _build_query(req)
        resp = await es.search(index="partners", body=body)
        hits = resp["hits"]["hits"]
        total = resp["hits"]["total"]["value"]
        items = []
        for hit in hits:
            src = hit["_source"]
            distance_km = None
            if "sort" in hit and req.latitude is not None:
                try:
                    distance_km = round(hit["sort"][0] / 1000, 2)
                except (IndexError, TypeError):
                    pass
            items.append(PartnerSearchResult(
                id=src.get("id", hit["_id"]),
                name=src.get("name", ""),
                description=src.get("description"),
                city=src.get("city"),
                address=src.get("address"),
                logo_url=src.get("logo_url"),
                rating=src.get("rating", 0.0),
                reviews_count=src.get("reviews_count", 0),
                yamap_reviews_count=src.get("yamap_reviews_count", 0),
                distance_km=distance_km,
                has_promo=src.get("has_promo", False),
                categories=src.get("categories", []),
                latitude=src.get("latitude"),
                longitude=src.get("longitude"),
                working_hours=src.get("working_hours"),
                phone=src.get("phone"),
                website=src.get("website"),
                subscription_plan=src.get("subscription_plan", "free"),
            ))
        result = SearchResponse(items=items, total=total, page=req.page, size=req.size)
        # Если ES вернул 0 и есть DB — пробуем DB
        if total == 0 and db is not None:
            return await _search_db(req, db)
        import json
        await _search_cache.set(cache_key, result.model_dump_json())
        return result
    except Exception as e:
        logger.warning("search.es_error", error=str(e))

    if db is not None:
        return await _search_db(req, db)
    return SearchResponse(items=[], total=0, page=req.page, size=req.size)


async def _search_db(req: SearchRequest, db: AsyncSession) -> SearchResponse:
    from sqlalchemy import func, or_
    conditions = [
        Partner.status == PartnerStatus.active,
        Partner.deleted_at.is_(None),
    ]
    if req.city:
        conditions.append(Partner.city == req.city)
    if req.region:
        conditions.append(Partner.region == req.region)
    if req.rating_min is not None:
        conditions.append(Partner.rating >= req.rating_min)
    if req.q:
        q = f"%{req.q}%"
        conditions.append(or_(
            Partner.name.ilike(q),
            Partner.description.ilike(q),
            Partner.subcategory.ilike(q),
        ))

    count_r = await db.execute(select(func.count()).select_from(Partner).where(and_(*conditions)))
    total = count_r.scalar_one()

    stmt = (
        select(Partner)
        .where(and_(*conditions))
        .order_by(Partner.rating.desc())
        .offset((req.page - 1) * req.size)
        .limit(req.size)
    )
    partners = (await db.execute(stmt)).scalars().all()

    items = [
        PartnerSearchResult(
            id=p.id, name=p.name, description=p.description,
            city=p.city, address=p.address, logo_url=p.logo_url,
            rating=p.rating, reviews_count=p.reviews_count,
            yamap_reviews_count=p.yamap_reviews_count,
            latitude=p.latitude, longitude=p.longitude,
            working_hours=p.working_hours, phone=p.phone,
            website=p.website, subscription_plan=p.subscription_plan,
        )
        for p in partners
    ]
    return SearchResponse(items=items, total=total, page=req.page, size=req.size)


async def get_map_points(
    db: AsyncSession,
    city: str | None = None,
    region: str | None = None,
    q: str | None = None,
) -> MapPointsResponse:
    cache_key = f"map:{city}:{region}:{q}"
    cached = await _map_cache.get(cache_key)
    if cached:
        import json
        data = json.loads(cached)
        return MapPointsResponse(**data)

    from sqlalchemy import or_
    conditions = [
        Partner.status == PartnerStatus.active,
        Partner.deleted_at.is_(None),
        Partner.latitude.isnot(None),
        Partner.longitude.isnot(None),
    ]
    if city:
        conditions.append(Partner.city == city)
    if region:
        conditions.append(Partner.region == region)
    if q:
        qp = f"%{q}%"
        conditions.append(or_(Partner.name.ilike(qp), Partner.subcategory.ilike(qp)))

    stmt = (
        select(
            Partner.id, Partner.name, Partner.address, Partner.city,
            Partner.latitude, Partner.longitude, Partner.rating,
            Partner.reviews_count, Partner.yamap_reviews_count,
            Partner.logo_url, Partner.working_hours, Partner.phone,
            Partner.subscription_plan,
        )
        .where(and_(*conditions))
        .limit(3000)
    )
    records = (await db.execute(stmt)).fetchall()

    items = [
        MapPoint(
            id=r.id, name=r.name, address=r.address, city=r.city,
            latitude=r.latitude, longitude=r.longitude,
            rating=r.rating,
            reviews_count=r.yamap_reviews_count or r.reviews_count,
            logo_url=r.logo_url, working_hours=r.working_hours,
            phone=r.phone, subscription_plan=r.subscription_plan or "free",
        )
        for r in records
    ]
    result = MapPointsResponse(items=items, total=len(items))
    import json
    await _map_cache.set(cache_key, result.model_dump_json())
    return result


async def autocomplete(q: str) -> list[str]:
    from app.search import get_es
    try:
        es = get_es()
        resp = await es.search(
            index="partners",
            body={
                "suggest": {
                    "name_suggest": {
                        "prefix": q,
                        "completion": {"field": "name_suggest", "size": 5},
                    }
                },
                "size": 0,
            },
        )
        suggestions = resp.get("suggest", {}).get("name_suggest", [{}])[0].get("options", [])
        return [s["text"] for s in suggestions]
    except Exception:
        return []


async def index_partner_document(partner_id: str, doc: dict[str, Any]) -> None:
    from app.search import get_es
    try:
        es = get_es()
        await es.index(index="partners", id=partner_id, document=doc)
    except Exception as e:
        logger.error("search.index_error", partner_id=partner_id, error=str(e))