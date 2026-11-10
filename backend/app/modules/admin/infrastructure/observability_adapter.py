"""Infrastructure observability adapter feeding /api/v1/admin/system-health."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.database import ping_database
from app.core.observability import ObservabilityTracker
from app.core.redis import RedisClientManager
from app.modules.admin.domain.entities import (
    ObservabilityErrorItemEntity,
    SystemObservabilityEntity,
)
from app.modules.admin.domain.rules import compute_cache_hit_ratio_percent


class CoreSystemObservabilityAdapter:
    """Collect live PG/Redis health, cache hit ratio & 24h 5xx correlation telemetry."""

    def __init__(
        self,
        *,
        service_name: str,
        db_engine: AsyncEngine,
        redis_manager: RedisClientManager,
        tracker: ObservabilityTracker,
    ) -> None:
        self._service_name = service_name
        self._db_engine = db_engine
        self._redis = redis_manager
        self._tracker = tracker

    async def collect_summary(self) -> SystemObservabilityEntity:
        pg_ok, redis_ok = await asyncio.gather(
            ping_database(self._db_engine),
            self._redis.ping(),
        )
        metrics = self._redis.metrics
        ratio = compute_cache_hit_ratio_percent(hits=metrics.hits, misses=metrics.misses)
        total_24h, errors_5xx_24h, recent = self._tracker.snapshot_24h()
        return SystemObservabilityEntity(
            health_status="ok" if (pg_ok and redis_ok) else "degraded",
            service_name=self._service_name,
            checked_at=datetime.now(UTC),
            postgresql_status="up" if pg_ok else "down",
            redis_status="up" if redis_ok else "down",
            redis_cache_hit_ratio_percent=ratio,
            total_requests_24h=total_24h,
            server_errors_5xx_24h=errors_5xx_24h,
            recent_error_correlations=tuple(
                ObservabilityErrorItemEntity(
                    request_id=e.request_id,
                    trace_id=e.trace_id,
                    route=e.route,
                    status_code=e.status_code,
                    error_code=e.error_code,
                    module=e.module,
                    occurred_at=e.occurred_at,
                )
                for e in recent
            ),
        )
