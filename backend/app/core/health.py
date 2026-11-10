"""Liveness and readiness probes aligned to TRD §25.1 and contracts/openapi.v1.yaml."""

from __future__ import annotations

import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import Settings, get_settings
from app.core.database import ping_database
from app.core.errors import build_error_json_response
from app.core.exceptions import ErrorCode
from app.core.logging import request_id_ctx, utc_now_iso
from app.core.redis import RedisClientManager
from app.core.schemas import HealthDependencies, HealthEnvelope, HealthStatus

router = APIRouter(prefix="/health", tags=["Infrastructure"])


def get_db_engine(request: Request) -> AsyncEngine:
    return request.app.state.db_engine


def get_redis_manager(request: Request) -> RedisClientManager:
    return request.app.state.redis_manager


type SettingsDep = Annotated[Settings, Depends(get_settings)]
type DbEngineDep = Annotated[AsyncEngine, Depends(get_db_engine)]
type RedisManagerDep = Annotated[RedisClientManager, Depends(get_redis_manager)]


@router.get(
    "/live",
    operation_id="getLivenessHealth",
    summary="Liveness probe aplikasi",
    response_model=HealthEnvelope,
)
async def get_liveness_health(settings: SettingsDep) -> HealthEnvelope:
    """Confirm application event loop is running without touching backing stores."""
    return HealthEnvelope(
        data=HealthStatus(
            status="ok",
            service=settings.APP_NAME,
            checked_at=utc_now_iso(),
            dependencies=None,
        ),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@router.get(
    "/ready",
    operation_id="getReadinessHealth",
    summary="Readiness probe PostgreSQL & Redis",
    response_model=HealthEnvelope,
)
async def get_readiness_health(
    settings: SettingsDep,
    db_engine: DbEngineDep,
    redis_manager: RedisManagerDep,
) -> Response:
    """Verify mandatory PostgreSQL and Redis readiness without leaking credentials."""
    pg_ok, redis_ok = await asyncio.gather(
        ping_database(db_engine),
        redis_manager.ping(),
    )
    deps = HealthDependencies(
        postgresql="up" if pg_ok else "down",
        redis="up" if redis_ok else "down",
    )
    if pg_ok and redis_ok:
        envelope = HealthEnvelope(
            data=HealthStatus(
                status="ok",
                service=settings.APP_NAME,
                checked_at=utc_now_iso(),
                dependencies=deps,
            ),
            meta=None,
            request_id=request_id_ctx.get(),
        )
        return JSONResponse(
            status_code=200,
            content=envelope.model_dump(mode="json"),
        )

    return build_error_json_response(
        code=ErrorCode.SYS_DEPENDENCY_UNAVAILABLE,
        status_code=503,
        message=(
            "Layanan sistem sedang mengalami gangguan sementara. "
            "Silakan coba lagi beberapa saat atau laporkan kode referensi."
        ),
        details=deps.model_dump(mode="json"),
    )
