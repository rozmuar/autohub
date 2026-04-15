"""Elasticsearch клиент и базовые операции с индексами."""

from elasticsearch import AsyncElasticsearch

from app.config import settings

_es: AsyncElasticsearch | None = None

# Настройки общих индексов
INDEX_SETTINGS = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,  # увеличить в production
        "analysis": {
            "analyzer": {
                "russian_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "russian_stop", "russian_stemmer"],
                },
            },
            "filter": {
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_",
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian",
                },
            },
        },
    }
}

PARTNER_INDEX_MAPPING = {
    **INDEX_SETTINGS,
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "name": {"type": "text", "analyzer": "russian_analyzer"},
            "description": {"type": "text", "analyzer": "russian_analyzer"},
            "status": {"type": "keyword"},
            "is_verified": {"type": "boolean"},
            "location": {"type": "geo_point"},
            "rating": {"type": "float"},
            "reviews_count": {"type": "integer"},
            "categories": {"type": "keyword"},
            "service_ids": {"type": "keyword"},
            "has_promo": {"type": "boolean"},
            "city": {"type": "keyword"},
            "address": {"type": "text", "analyzer": "russian_analyzer"},
            "created_at": {"type": "date"},
        }
    },
}

SERVICES_INDEX_MAPPING = {
    **INDEX_SETTINGS,
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "partner_id": {"type": "keyword"},
            "name": {"type": "text", "analyzer": "russian_analyzer"},
            "category": {"type": "keyword"},
            "price_min": {"type": "float"},
            "price_max": {"type": "float"},
            "compatible_vehicle_ids": {"type": "keyword"},
            "duration_minutes": {"type": "integer"},
        }
    },
}

PRODUCTS_INDEX_MAPPING = {
    **INDEX_SETTINGS,
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "partner_id": {"type": "keyword"},
            "name": {"type": "text", "analyzer": "russian_analyzer"},
            "article": {"type": "keyword"},
            "oem_numbers": {"type": "keyword"},
            "brand": {"type": "keyword"},
            "category": {"type": "keyword"},
            "price": {"type": "float"},
            "in_stock": {"type": "boolean"},
            "compatible_vehicle_ids": {"type": "keyword"},
        }
    },
}


async def create_es_client() -> None:
    global _es  # noqa: PLW0603

    _es = AsyncElasticsearch(
        hosts=[settings.elasticsearch_url],
        basic_auth=(settings.elasticsearch_user, settings.elasticsearch_password)
        if settings.elasticsearch_password
        else None,
        retry_on_timeout=True,
        max_retries=3,
    )

    await _ensure_indices()


async def _ensure_indices() -> None:
    """Создаём индексы если они не существуют."""
    es = get_es()
    indices = {
        settings.es_index_partners: PARTNER_INDEX_MAPPING,
        settings.es_index_services: SERVICES_INDEX_MAPPING,
        settings.es_index_products: PRODUCTS_INDEX_MAPPING,
    }
    for index_name, mapping in indices.items():
        exists = await es.indices.exists(index=index_name)
        if not exists:
            await es.indices.create(
                index=index_name,
                settings=mapping.get("settings"),
                mappings=mapping.get("mappings"),
            )


async def close_es_client() -> None:
    global _es  # noqa: PLW0603
    if _es is not None:
        await _es.close()
        _es = None


def get_es() -> AsyncElasticsearch:
    if _es is None:
        raise RuntimeError("Elasticsearch client not initialized.")
    return _es
