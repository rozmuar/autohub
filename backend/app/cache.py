"""Redis клиент — кэш, сессии, распределённые блокировки."""

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.config import settings

_redis: Redis | None = None


async def create_redis_pool() -> None:
    global _redis  # noqa: PLW0603
    _redis = await aioredis.from_url(
        str(settings.redis_url),
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
    )


async def close_redis_pool() -> None:
    global _redis  # noqa: PLW0603
    if _redis is not None:
        await _redis.aclose()
        _redis = None


def get_redis() -> Redis:
    if _redis is None:
        raise RuntimeError("Redis pool not initialized.")
    return _redis


class CacheService:
    """Высокоуровневый сервис кэширования поверх Redis."""

    def __init__(self, prefix: str = "", ttl: int | None = None) -> None:
        self.prefix = prefix
        self.default_ttl = ttl or settings.redis_cache_ttl

    def _key(self, key: str) -> str:
        return f"{self.prefix}:{key}" if self.prefix else key

    async def get(self, key: str) -> str | None:
        return await get_redis().get(self._key(key))

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        await get_redis().set(self._key(key), value, ex=ttl or self.default_ttl)

    async def delete(self, key: str) -> None:
        await get_redis().delete(self._key(key))

    async def exists(self, key: str) -> bool:
        return bool(await get_redis().exists(self._key(key)))

    async def expire(self, key: str, ttl: int) -> None:
        await get_redis().expire(self._key(key), ttl)


class DistributedLock:
    """Простая распределённая блокировка через Redis SETNX."""

    def __init__(self, name: str, timeout: int = 30) -> None:
        self.key = f"lock:{name}"
        self.timeout = timeout

    async def acquire(self, owner: str) -> bool:
        """Возвращает True если блокировка захвачена."""
        redis = get_redis()
        return bool(await redis.set(self.key, owner, nx=True, ex=self.timeout))

    async def release(self, owner: str) -> bool:
        """Освобождает блокировку, только если владелец совпадает."""
        redis = get_redis()
        current = await redis.get(self.key)
        if current == owner:
            await redis.delete(self.key)
            return True
        return False

    async def __aenter__(self) -> "DistributedLock":
        return self

    async def __aexit__(self, *_) -> None:
        pass
