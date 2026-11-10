"""Graceful Redis cache-aside adapter for non-critical public reads (TRD §11)."""

from __future__ import annotations

from app.core.redis import RedisClientManager


class RedisPublicPortalCache:
    """Thin adapter delegating public reads/writes to core RedisClientManager safely."""

    def __init__(self, redis_manager: RedisClientManager) -> None:
        self._redis = redis_manager

    async def get_json(self, key: str) -> str | None:
        return await self._redis.get_cached_json(key)

    async def set_json(self, key: str, value: str, ttl_seconds: int) -> None:
        await self._redis.set_cached_json(key, value, ttl_seconds)
