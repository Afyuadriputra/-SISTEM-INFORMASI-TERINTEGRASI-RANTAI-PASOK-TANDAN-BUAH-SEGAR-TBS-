"""Async Redis client lifecycle, bounded pooling, telemetry counters, and fail-closed guards."""

from __future__ import annotations

import time
from collections.abc import Awaitable
from dataclasses import dataclass
from typing import cast

from redis.asyncio import ConnectionPool, Redis
from redis.exceptions import RedisError

from app.core.config import Settings
from app.core.exceptions import AppError, ErrorCode
from app.core.logging import get_logger

logger = get_logger("app.core.redis")


@dataclass
class CacheMetrics:
    """In-process telemetry counters exposed safely for observability (TRD §11.5)."""

    hits: int = 0
    misses: int = 0
    errors: int = 0
    invalidations: int = 0


class RedisClientManager:
    """Own single bounded async Redis connection pool across application lifespan."""

    def __init__(self, settings: Settings, *, url_override: str | None = None) -> None:
        url = url_override if url_override is not None else settings.REDIS_URL.get_secret_value()
        self._pool = ConnectionPool.from_url(
            url,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            socket_connect_timeout=settings.REDIS_CONNECT_TIMEOUT_SECONDS,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT_SECONDS,
            decode_responses=True,
        )
        self._client = Redis(connection_pool=self._pool)
        self.metrics = CacheMetrics()

    @property
    def client(self) -> Redis:
        return self._client

    async def ping(self) -> bool:
        """Check live Redis responsiveness without raising into health endpoints."""
        started = time.perf_counter()
        try:
            pong = await cast(Awaitable[bool], self._client.ping())
            return bool(pong)
        except Exception as exc:
            self.metrics.errors += 1
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            logger.error(
                "redis_readiness_failed",
                extra={
                    "structured": {
                        "event": "dependency_check_failed",
                        "dependency": "redis",
                        "error_class": exc.__class__.__name__,
                        "duration_ms": elapsed_ms,
                    }
                },
            )
            return False

    async def get_cached_json(self, key: str) -> str | None:
        """Read non-critical cache entry; degrade gracefully to cache miss on Redis failure."""
        try:
            value = await self._client.get(key)
            if value is None:
                self.metrics.misses += 1
            else:
                self.metrics.hits += 1
            return value
        except RedisError as exc:
            self.metrics.errors += 1
            logger.warning(
                "redis_cache_read_degraded",
                extra={
                    "structured": {
                        "event": "cache_read_fallback",
                        "cache_key": key,
                        "error_class": exc.__class__.__name__,
                    }
                },
            )
            return None

    async def set_cached_json(self, key: str, value: str, ttl_seconds: int) -> None:
        """Store non-critical cached payload with bounded TTL; tolerate transient failure."""
        try:
            await self._client.set(key, value, ex=ttl_seconds)
        except RedisError as exc:
            self.metrics.errors += 1
            logger.warning(
                "redis_cache_write_degraded",
                extra={
                    "structured": {
                        "event": "cache_write_skipped",
                        "cache_key": key,
                        "error_class": exc.__class__.__name__,
                    }
                },
            )

    async def invalidate_keys(self, *keys: str) -> None:
        """Invalidate versioned cache keys strictly post-commit (TRD §11.4)."""
        if not keys:
            return
        try:
            await self._client.delete(*keys)
            self.metrics.invalidations += len(keys)
        except RedisError as exc:
            self.metrics.errors += 1
            logger.warning(
                "redis_cache_invalidation_degraded",
                extra={
                    "structured": {
                        "event": "cache_invalidation_failed",
                        "key_count": len(keys),
                        "error_class": exc.__class__.__name__,
                    }
                },
            )

    async def require_security_operation(self, operation_name: str) -> Redis:
        """Enforce fail-closed guarantee when Redis backs session or rate-limit security."""
        if not await self.ping():
            logger.error(
                "redis_security_fail_closed",
                extra={
                    "structured": {
                        "event": "security_fail_closed",
                        "operation": operation_name,
                    }
                },
            )
            raise AppError(ErrorCode.SYS_DEPENDENCY_UNAVAILABLE)
        return self._client

    async def close(self) -> None:
        """Release all Redis connections cleanly on shutdown."""
        await self._client.aclose()
        await self._pool.disconnect()
