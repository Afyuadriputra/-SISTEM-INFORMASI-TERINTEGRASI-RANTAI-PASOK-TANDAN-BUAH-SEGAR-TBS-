"""Redis cache invalidator for public mill directory changes after database commit."""

from __future__ import annotations

from uuid import UUID

from redis.exceptions import RedisError

from app.core.logging import get_logger
from app.core.redis import RedisClientManager

logger = get_logger("app.master_data.cache")


class RedisPublicDirectoryInvalidator:
    """Best-effort post-commit invalidation of public:mills:v1:* cache entries."""

    def __init__(self, redis_manager: RedisClientManager) -> None:
        self._redis = redis_manager

    async def invalidate_public_mills(self, mill_id: UUID | None = None) -> None:
        keys: list[str] = []
        try:
            async for key in self._redis.client.scan_iter(match="public:mills:v1:*", count=100):
                keys.append(str(key))
            if mill_id is not None:
                keys.append(f"public:mills:v1:detail:{mill_id}")
            if keys:
                await self._redis.invalidate_keys(*set(keys))
        except RedisError as exc:
            self._redis.metrics.errors += 1
            logger.warning(
                "public_mill_cache_invalidation_degraded",
                extra={"structured": {"error_class": exc.__class__.__name__}},
            )
