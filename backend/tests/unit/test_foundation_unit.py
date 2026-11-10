"""Unit tests for B0 core foundation (settings, error catalog parity, logging redaction, probes)."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from pathlib import Path
from unittest.mock import AsyncMock

import httpx
import pytest
import yaml
from app.core.config import Settings
from app.core.exceptions import ERROR_CATALOG_DEFAULTS, AppError, ErrorCode
from app.core.logging import JsonFormatter, redact_mapping, sanitize_text
from app.core.security import normalize_or_generate_request_id
from app.main import create_app
from fastapi import APIRouter
from pydantic import BaseModel, SecretStr


def test_settings_validation_and_secret_redaction() -> None:
    cfg = Settings(
        DATABASE_URL=SecretStr("postgresql://user_x:super_secret_pw@localhost:5432/db_x"),
        REDIS_URL=SecretStr("redis://:redis_secret@localhost:6379/0"),
        SESSION_SECRET=SecretStr("super-long-dev-secret-string-for-tests-1234"),
    )
    assert cfg.async_database_url.startswith("postgresql+psycopg://")
    assert "super_secret_pw" not in repr(cfg)
    assert "redis_secret" not in repr(cfg)

    with pytest.raises(ValueError, match="Wildcard CORS"):
        Settings(CORS_ALLOWED_ORIGINS=["*"])

    with pytest.raises(ValueError, match="PostgreSQL DSN"):
        Settings(DATABASE_URL=SecretStr("sqlite+aiosqlite:///./bad.db"))


def test_error_code_enum_matches_canonical_catalog(contracts_dir: Path) -> None:
    catalog = yaml.safe_load((contracts_dir / "error-catalog.yaml").read_text(encoding="utf-8"))
    catalog_map = {item["code"]: item for item in catalog["errors"]}

    assert {c.value for c in ErrorCode} == set(catalog_map.keys())
    assert set(ERROR_CATALOG_DEFAULTS.keys()) == set(ErrorCode)

    for code_member in ErrorCode:
        http_status, msg = ERROR_CATALOG_DEFAULTS[code_member]
        cat_item = catalog_map[code_member.value]
        assert http_status == cat_item["http_status"]
        assert msg == cat_item["client_safe_message"]


def test_structured_logging_redacts_secrets_and_credentials() -> None:
    dirty_dsn = "postgresql+psycopg://admin:TopSecret99@10.0.0.5:5432/prod"
    assert "[REDACTED]" in sanitize_text(dirty_dsn)
    assert "TopSecret99" not in sanitize_text(dirty_dsn)

    redacted = redact_mapping(
        {
            "password": "secret",
            "cookie": "ts_agroniaga_session=abc",
            "nested": {"x-csrf-token": "csrf123", "dsn": dirty_dsn},
            "safe": "hello",
        }
    )
    assert redacted["password"] == "[REDACTED]"
    assert redacted["cookie"] == "[REDACTED]"
    assert redacted["nested"]["x-csrf-token"] == "[REDACTED]"
    assert redacted["nested"]["dsn"] == "[REDACTED]"
    assert redacted["safe"] == "hello"

    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="failed connecting postgresql://u:pw@db:5432/test",
        args=(),
        exc_info=None,
    )
    record.structured = {"token": "raw-token", "status_code": 200}
    parsed = json.loads(formatter.format(record))
    assert "pw" not in parsed["message"]
    assert parsed["token"] == "[REDACTED]"
    assert parsed["status_code"] == 200


def test_request_id_normalization_enforces_openapi_pattern() -> None:
    pattern = re.compile(r"^req_[A-Za-z0-9._-]+$")
    assert normalize_or_generate_request_id("req_valid_123") == "req_valid_123"
    generated = normalize_or_generate_request_id("bad header with spaces")
    assert pattern.match(generated)
    assert len(generated) >= 6


@pytest.mark.asyncio
async def test_liveness_request_id_error_handlers_and_ready_503() -> None:
    app = create_app(
        settings=Settings(LOG_JSON=False, REQUEST_TIMEOUT_SECONDS=1),
    )

    test_router = APIRouter(prefix="/_test")

    class BodyModel(BaseModel):
        amount: int

    @test_router.post("/validate")
    async def check_validation(payload: BodyModel) -> dict[str, int]:
        return {"amount": payload.amount}

    @test_router.get("/controlled-error")
    async def trigger_controlled_error() -> None:
        raise AppError(ErrorCode.FIN_POLICY_UNCONFIRMED, details={"model": "UNCONFIRMED"})

    @test_router.get("/unhandled-error")
    async def trigger_unhandled() -> None:
        raise RuntimeError("postgresql://secret_user:secret_pass@internal-host:5432/db crashed")

    @test_router.get("/slow")
    async def trigger_timeout() -> dict[str, str]:
        await asyncio.sleep(2.0)
        return {"ok": "never"}

    app.include_router(test_router)

    async with app.router.lifespan_context(app):
        # Replace network ping with deterministic async mocks to test route/handler contracts cleanly
        app.state.redis_manager.ping = AsyncMock(return_value=False)

        transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            # 1. /health/live + X-Request-ID propagation
            live = await client.get("/health/live", headers={"X-Request-ID": "req_b0_unit_live"})
            assert live.status_code == 200
            assert live.headers["X-Request-ID"] == "req_b0_unit_live"
            assert live.headers["X-Content-Type-Options"] == "nosniff"
            assert live.headers["X-Frame-Options"] == "DENY"
            assert live.headers["Cache-Control"] == "no-store"
            live_body = live.json()
            assert live_body["success"] is True
            assert live_body["data"]["status"] == "ok"
            assert live_body["data"]["checked_at"].endswith("Z")
            assert live_body["request_id"] == "req_b0_unit_live"

            # 2. /health/ready degraded -> 503 SYS_DEPENDENCY_UNAVAILABLE without DSN leak
            with pytest.MonkeyPatch.context() as mp:
                mp.setattr("app.core.health.ping_database", AsyncMock(return_value=True))
                ready = await client.get("/health/ready")
            assert ready.status_code == 503
            rjson = ready.json()
            assert rjson["success"] is False
            assert rjson["error"]["code"] == "SYS_DEPENDENCY_UNAVAILABLE"
            assert rjson["error"]["details"] == {"postgresql": "up", "redis": "down"}
            assert "secret" not in ready.text

            # 3. 422 Pydantic validation mapped to ErrorResponse
            val_err = await client.post("/_test/validate", json={})
            assert val_err.status_code == 422
            vjson = val_err.json()
            assert vjson["success"] is False
            assert vjson["error"]["code"] == "VAL_REQUIRED_FIELD"
            assert isinstance(vjson["error"]["details"], list)
            assert vjson["request_id"].startswith("req_")

            # 4. Controlled AppError mapped to exact status + ErrorResponse
            app_err = await client.get("/_test/controlled-error")
            assert app_err.status_code == 409
            assert app_err.json()["error"]["code"] == "FIN_POLICY_UNCONFIRMED"

            # 5. Unhandled RuntimeError -> 500 SYS_INTERNAL_ERROR with zero stacktrace/DSN leak
            unhandled = await client.get("/_test/unhandled-error")
            assert unhandled.status_code == 500
            ujson = unhandled.json()
            assert ujson["error"]["code"] == "SYS_INTERNAL_ERROR"
            assert "secret_pass" not in unhandled.text
            assert "RuntimeError" not in unhandled.text

            # 6. Bounded timeout middleware -> 504 SYS_REQUEST_TIMEOUT
            timed_out = await client.get("/_test/slow")
            assert timed_out.status_code == 504
            assert timed_out.json()["error"]["code"] == "SYS_REQUEST_TIMEOUT"
