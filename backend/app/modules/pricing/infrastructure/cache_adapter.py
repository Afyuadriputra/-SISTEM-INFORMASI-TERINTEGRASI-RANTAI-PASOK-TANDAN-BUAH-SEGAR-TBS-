"""Post-commit Redis cache invalidator for public prices and directory."""

from __future__ import annotations

from redis.exceptions import RedisError

from app.core.logging import get_logger
from app.core.redis import RedisClientManager

logger = get_logger("app.pricing.cache")


class RedisPublicPricingInvalidator:
    """Best-effort post-commit invalidation of public price/mill caches."""

    def __init__(self, redis_manager: RedisClientManager) -> None:
        self._redis = redis_manager

    async def _delete_pattern(self, pattern: str) -> None:
        try:
            keys = [str(k) async for k in self._redis.client.scan_iter(match=pattern, count=100)]
            if keys:
                await self._redis.invalidate_keys(*keys)
        except RedisError as exc:
            self._redis.metrics.errors += 1
            logger.warning(
                "public_pricing_cache_invalidation_degraded",
                extra={"structured": {"pattern": pattern, "error_class": exc.__class__.__name__}},
            )

    async def invalidate_public_prices(self) -> None:
        await self._delete_pattern("public:prices:v1:*")
        await self._delete_pattern("public:mills:v1:*")

    async def invalidate_public_disbun(self) -> None:
        await self._delete_pattern("public:disbun:v1:*")
