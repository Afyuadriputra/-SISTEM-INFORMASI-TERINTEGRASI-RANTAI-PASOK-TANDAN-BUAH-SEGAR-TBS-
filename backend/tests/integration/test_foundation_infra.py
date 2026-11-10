"""Real PostgreSQL, Alembic, and Redis integration tests for B0 Project Foundation."""

from __future__ import annotations

import httpx
import pytest
from app.core.config import Settings
from app.core.database import build_async_engine, dispose_database, ping_database
from app.core.exceptions import AppError
from app.core.redis import RedisClientManager
from app.main import create_app
from sqlalchemy import text


@pytest.mark.asyncio
async def test_real_postgresql_connectivity_and_pool_disposal(test_db_url: str | None) -> None:
    assert test_db_url, (
        "TEST_DATABASE_URL must be configured for real PostgreSQL B0 integration test"
    )
    cfg = Settings()
    engine = build_async_engine(cfg, dsn_override=test_db_url)
    try:
        assert await ping_database(engine) is True
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT current_database()"))
            db_name = res.scalar_one()
            assert db_name
    finally:
        await dispose_database(engine)


@pytest.mark.asyncio
async def test_real_redis_connectivity_and_fail_closed_security(test_redis_url: str | None) -> None:
    assert test_redis_url, "REDIS_URL or TEST_REDIS_URL must be configured for real Redis B0 test"
    cfg = Settings()
    manager = RedisClientManager(cfg, url_override=test_redis_url)
    try:
        assert await manager.ping() is True
        await manager.set_cached_json("b0:test:probe", '{"ok":true}', ttl_seconds=10)
        assert await manager.get_cached_json("b0:test:probe") == '{"ok":true}'
        await manager.invalidate_keys("b0:test:probe")
        assert await manager.get_cached_json("b0:test:probe") is None
        client = await manager.require_security_operation("b0_session_probe")
        assert client is not None
    finally:
        await manager.close()

    dead_manager = RedisClientManager(cfg, url_override="redis://127.0.0.1:6399/0")
    try:
        with pytest.raises(AppError) as exc_info:
            await dead_manager.require_security_operation("b0_fail_closed_probe")
        assert exc_info.value.code.value == "SYS_DEPENDENCY_UNAVAILABLE"
    finally:
        await dead_manager.close()


@pytest.mark.asyncio
async def test_health_ready_returns_200_against_real_postgres_and_redis(
    test_db_url: str | None, test_redis_url: str | None
) -> None:
    assert test_db_url and test_redis_url, (
        "Both TEST_DATABASE_URL and REDIS_URL/TEST_REDIS_URL are required for /health/ready integration test"
    )
    app = create_app(
        settings=Settings(LOG_JSON=False),
        db_dsn_override=test_db_url,
        redis_url_override=test_redis_url,
    )
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/health/ready")
            assert resp.status_code == 200
            payload = resp.json()
            assert payload["success"] is True
            assert payload["data"]["status"] == "ok"
            assert payload["data"]["dependencies"] == {"postgresql": "up", "redis": "up"}
