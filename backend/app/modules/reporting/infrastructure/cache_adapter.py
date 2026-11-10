"""Graceful Redis cache-aside adapter for scoped dashboard reporting (TRD §11.5)."""

from __future__ import annotations

from app.core.redis import RedisClientManager


class RedisReportingCache:
    """Delegate scoped reporting cache reads/writes safely with PG fallback."""

    def __init__(self, redis_manager: RedisClientManager) -> None:
        self._redis = redis_manager

    async def get_json(self, key: str) -> str | None:
        return await self._redis.get_cached_json(key)

    async def set_json(self, key: str, value: str, ttl_seconds: int) -> None:
        await self._redis.set_cached_json(key, value, ttl_seconds)
