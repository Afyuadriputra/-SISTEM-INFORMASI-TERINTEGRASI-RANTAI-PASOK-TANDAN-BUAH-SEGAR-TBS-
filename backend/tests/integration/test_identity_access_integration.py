"""Integration tests for Authentication, Sessions, CSRF, RBAC, and Audit Logs (B1)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID, uuid4

import httpx
import pytest
from app.core.config import Settings
from app.core.database import build_async_engine, build_session_factory, dispose_database
from app.main import create_app
from app.modules.identity_access.domain.entities import (
    AuthenticatedPrincipal,
    RoleCode,
    ScopeType,
)
from app.modules.identity_access.domain.rules import assert_farmer_scope
from app.modules.identity_access.infrastructure.models import (
    AuthSessionModel,
    UserAccessScopeModel,
    UserAccountModel,
    UserRoleGrantModel,
    deterministic_role_id,
    seed_rbac_catalog,
)
from app.modules.identity_access.infrastructure.security_adapters import Argon2PasswordHasher
from app.modules.identity_access.presentation.dependencies import require_access
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy import select, text


@pytest.fixture
async def b1_env(test_db_url: str | None, test_redis_url: str | None) -> AsyncIterator[dict]:
    """Provide isolated app client + session factory + clean Postgres/Redis test DB per test."""
    assert test_db_url and test_redis_url
    assert test_redis_url.endswith("/1"), "Integration tests must target isolated Redis DB /1"

    cfg = Settings(
        LOG_JSON=False,
        LOGIN_RATE_LIMIT_MAX_ATTEMPTS=4,
        LOGIN_IP_RATE_LIMIT_MAX_ATTEMPTS=20,
        LOGIN_RATE_LIMIT_WINDOW_SECONDS=60,
    )
    engine = build_async_engine(cfg, dsn_override=test_db_url)
    session_factory = build_session_factory(engine)
    redis_client = Redis.from_url(test_redis_url, decode_responses=True)

    async with session_factory() as session:
        async with session.begin():
            await session.execute(
                text(
                    "TRUNCATE TABLE audit_events, auth_sessions, user_access_scopes, "
                    "user_role_grants, user_accounts, farms, cooperative_memberships, "
                    "farmers, cooperatives, mills, mill_companies, perumda_offices, "
                    "vehicles, drivers, parties RESTART IDENTITY CASCADE"
                )
            )
            await seed_rbac_catalog(session)
    await redis_client.flushdb()

    app = create_app(
        settings=cfg,
        db_dsn_override=test_db_url,
        redis_url_override=test_redis_url,
    )
    async with app.router.lifespan_context(app):
        yield {
            "app": app,
            "cfg": cfg,
            "session_factory": session_factory,
            "redis": redis_client,
        }

    await redis_client.flushdb()
    await redis_client.aclose()
    await dispose_database(engine)


async def _ensure_scope_target_rows(
    session,
    *,
    now: datetime,
    farmer_id: UUID | None = None,
    cooperative_id: UUID | None = None,
    mill_id: UUID | None = None,
) -> None:
    from app.modules.master_data.infrastructure.models import (
        CooperativeModel,
        FarmerModel,
        MillCompanyModel,
        MillModel,
        PartyModel,
    )

    suffix = uuid4().hex[:8]
    if farmer_id is not None:
        if (
            await session.execute(select(FarmerModel).where(FarmerModel.id == farmer_id))
        ).scalar_one_or_none() is None:
            pid = uuid4()
            session.add(
                PartyModel(
                    id=pid,
                    party_type="FARMER",
                    display_name=f"Farmer {suffix}",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()
            session.add(
                FarmerModel(
                    id=farmer_id,
                    party_id=pid,
                    farmer_code=f"PET-{suffix}",
                    full_name=f"Farmer {suffix}",
                    contact_phone="0800000001",
                    identity_reference=None,
                    status="ACTIVE",
                    version=1,
                    created_at=now,
                    updated_at=now,
                )
            )
    if cooperative_id is not None:
        if (
            await session.execute(
                select(CooperativeModel).where(CooperativeModel.id == cooperative_id)
            )
        ).scalar_one_or_none() is None:
            pid = uuid4()
            session.add(
                PartyModel(
                    id=pid,
                    party_type="COOPERATIVE",
                    display_name=f"Coop {suffix}",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()
            session.add(
                CooperativeModel(
                    id=cooperative_id,
                    party_id=pid,
                    cooperative_code=f"KOP-{suffix}",
                    cooperative_name=f"Koperasi {suffix}",
                    address="Jl. Raya Pelalawan",
                    contact_phone="0761000001",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
    if mill_id is not None:
        if (
            await session.execute(select(MillModel).where(MillModel.id == mill_id))
        ).scalar_one_or_none() is None:
            pid, mcid = uuid4(), uuid4()
            session.add(
                PartyModel(
                    id=pid,
                    party_type="MILL_COMPANY",
                    display_name=f"MillCo {suffix}",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()
            session.add(
                MillCompanyModel(
                    id=mcid,
                    party_id=pid,
                    company_code=f"MC-{suffix}",
                    company_name=f"PT PKS {suffix}",
                    contact_phone="0761000002",
                    address="Jl. PKS",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()
            session.add(
                MillModel(
                    id=mill_id,
                    mill_company_id=mcid,
                    mill_code=f"PKS-{suffix}",
                    mill_name=f"PKS {suffix}",
                    address="Pelalawan",
                    district="Pangkalan Kerinci",
                    regency="Pelalawan",
                    province="Riau",
                    latitude=None,
                    longitude=None,
                    contact_phone=None,
                    partnership_status="ACTIVE",
                    is_public=False,
                    location_verified_at=None,
                    version=1,
                    created_at=now,
                    updated_at=now,
                )
            )
    await session.flush()


async def _insert_user(
    session_factory,
    *,
    username: str,
    password: str,
    role: RoleCode,
    scope: ScopeType,
    status: str = "ACTIVE",
    farmer_id=None,
    cooperative_id=None,
    mill_id=None,
) -> UserAccountModel:
    hasher = Argon2PasswordHasher()
    pw_hash = await hasher.hash_password(password)
    now = datetime.now(UTC)
    uid = uuid4()
    async with session_factory() as session:
        async with session.begin():
            await _ensure_scope_target_rows(
                session,
                now=now,
                farmer_id=farmer_id,
                cooperative_id=cooperative_id,
                mill_id=mill_id,
            )
            user = UserAccountModel(
                id=uid,
                username=username,
                email=f"{username}@test.local",
                display_name=f"User {username}",
                password_hash=pw_hash,
                linked_party_id=None,
                status=status,
                failed_login_count=0,
                last_login_at=None,
                created_at=now,
                updated_at=now,
            )
            session.add(user)
            session.add(
                UserRoleGrantModel(
                    id=uuid4(),
                    user_id=uid,
                    role_id=deterministic_role_id(role.value),
                    granted_by=None,
                    granted_at=now,
                    revoked_at=None,
                )
            )
            session.add(
                UserAccessScopeModel(
                    id=uuid4(),
                    user_id=uid,
                    scope_type=scope.value,
                    farmer_id=farmer_id,
                    cooperative_id=cooperative_id,
                    mill_id=mill_id,
                    granted_by=None,
                    created_at=now,
                    revoked_at=None,
                )
            )
    return user


@pytest.mark.asyncio
async def test_login_me_logout_session_rotation_and_security_invariants(b1_env: dict) -> None:
    app = b1_env["app"]
    sf = b1_env["session_factory"]
    cfg: Settings = b1_env["cfg"]

    coop_id = uuid4()
    await _insert_user(
        sf,
        username="kop_op_01",
        password="StrongPassword#2026",
        role=RoleCode.COOPERATIVE_OPERATOR,
        scope=ScopeType.COOPERATIVE,
        cooperative_id=coop_id,
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        unauth = await client.get("/api/v1/auth/me")
        assert unauth.status_code == 401
        assert unauth.json()["error"]["code"] == "AUTH_REQUIRED"

        pre_csrf = await client.get("/api/v1/auth/csrf")
        assert pre_csrf.status_code == 200
        pre_token = pre_csrf.json()["data"]["csrf_token"]

        bad_login = await client.post(
            "/api/v1/auth/login",
            json={"username": "kop_op_01", "password": "WrongPassword999"},
        )
        assert bad_login.status_code == 401
        assert bad_login.json()["error"]["code"] == "AUTH_INVALID_CREDENTIALS"

        unknown_login = await client.post(
            "/api/v1/auth/login",
            json={"username": "no_such_account", "password": "WrongPassword999"},
        )
        assert unknown_login.status_code == 401
        assert unknown_login.json() == {
            **bad_login.json(),
            "request_id": unknown_login.json()["request_id"],
        }

        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "kop_op_01", "password": "StrongPassword#2026"},
        )
        assert login_resp.status_code == 200
        set_cookie_header = login_resp.headers.get("set-cookie", "")
        assert "HttpOnly" in set_cookie_header
        assert "SameSite=lax" in set_cookie_header
        first_token = client.cookies.get(cfg.SESSION_COOKIE_NAME)
        assert first_token

        body_text = login_resp.text
        assert "$argon2" not in body_text
        assert first_token not in body_text
        assert login_resp.json()["data"]["roles"] == ["COOPERATIVE_OPERATOR"]
        assert login_resp.json()["data"]["non_approver_admin"] is False

        me_resp = await client.get("/api/v1/auth/me")
        assert me_resp.status_code == 200
        assert me_resp.json()["data"]["username"] == "kop_op_01"

        # Pre-auth CSRF token must not pass for authenticated mutations (session rotation).
        bad_logout = await client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": pre_token})
        assert bad_logout.status_code == 403
        assert bad_logout.json()["error"]["code"] == "AUTH_CSRF_INVALID"

        # Session fixation test: re-login rotates session ID and revokes first_token.
        relogin_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "kop_op_01", "password": "StrongPassword#2026"},
        )
        assert relogin_resp.status_code == 200
        second_token = client.cookies.get(cfg.SESSION_COOKIE_NAME)
        assert second_token and second_token != first_token

        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            cookies={cfg.SESSION_COOKIE_NAME: first_token},
        ) as stale_client:
            stale_resp = await stale_client.get("/api/v1/auth/me")
        assert stale_resp.status_code == 401
        assert stale_resp.json()["error"]["code"] == "AUTH_SESSION_EXPIRED"

        # Origin mismatch rejection on state-changing request.
        csrf_resp = await client.get("/api/v1/auth/csrf")
        csrf_token = csrf_resp.json()["data"]["csrf_token"]
        evil_origin = await client.post(
            "/api/v1/auth/logout",
            headers={"X-CSRF-Token": csrf_token, "Origin": "https://attacker.example"},
        )
        assert evil_origin.status_code == 403
        assert evil_origin.json()["error"]["code"] == "AUTH_CSRF_INVALID"

        # Valid CSRF logout revokes session cleanly.
        logout_resp = await client.post(
            "/api/v1/auth/logout",
            headers={"X-CSRF-Token": csrf_token},
        )
        assert logout_resp.status_code == 200
        assert logout_resp.json()["data"] == {"logged_out": True, "redirect_to": "/login"}

        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            cookies={cfg.SESSION_COOKIE_NAME: second_token},
        ) as dead_client:
            after_logout = await dead_client.get("/api/v1/auth/me")
        assert after_logout.status_code == 401
        assert after_logout.json()["error"]["code"] == "AUTH_SESSION_EXPIRED"


@pytest.mark.asyncio
async def test_inactive_account_expired_session_and_append_only_audit_log(b1_env: dict) -> None:
    app = b1_env["app"]
    sf = b1_env["session_factory"]

    await _insert_user(
        sf,
        username="locked_farmer",
        password="ValidFarmerPass#1",
        role=RoleCode.FARMER,
        scope=ScopeType.FARMER,
        status="INACTIVE",
        farmer_id=uuid4(),
    )
    active_user = await _insert_user(
        sf,
        username="active_farmer",
        password="ValidFarmerPass#1",
        role=RoleCode.FARMER,
        scope=ScopeType.FARMER,
        farmer_id=uuid4(),
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        inactive_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "locked_farmer", "password": "ValidFarmerPass#1"},
        )
        assert inactive_resp.status_code == 401
        assert inactive_resp.json()["error"]["code"] == "AUTH_INVALID_CREDENTIALS"

        ok_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "active_farmer", "password": "ValidFarmerPass#1"},
        )
        assert ok_resp.status_code == 200

        # Expire DB session row directly and verify /auth/me rejects expired session.
        async with sf() as session:
            async with session.begin():
                row = (
                    await session.execute(
                        select(AuthSessionModel).where(AuthSessionModel.user_id == active_user.id)
                    )
                ).scalar_one()
                row.expires_at = datetime.now(UTC) - timedelta(seconds=10)

        expired_resp = await client.get("/api/v1/auth/me")
        assert expired_resp.status_code == 401
        assert expired_resp.json()["error"]["code"] == "AUTH_SESSION_EXPIRED"

        # Verify PostgreSQL append-only protection blocks direct DELETE on audit_events.
        async with sf() as session:
            with pytest.raises(Exception, match="append-only"):
                async with session.begin():
                    await session.execute(text("DELETE FROM audit_events"))


@pytest.mark.asyncio
async def test_admin_user_management_privilege_escalation_and_instant_revocation(
    b1_env: dict,
) -> None:
    app = b1_env["app"]
    sf = b1_env["session_factory"]

    await _insert_user(
        sf,
        username="sys_admin_01",
        password="AdminStrongPass#2026",
        role=RoleCode.SYSTEM_ADMIN,
        scope=ScopeType.PERUMDA_GLOBAL,
    )
    mill_id = uuid4()
    async with sf() as session:
        async with session.begin():
            await _ensure_scope_target_rows(session, now=datetime.now(UTC), mill_id=mill_id)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as admin_client:
        login = await admin_client.post(
            "/api/v1/auth/login",
            json={"username": "sys_admin_01", "password": "AdminStrongPass#2026"},
        )
        assert login.status_code == 200
        assert login.json()["data"]["non_approver_admin"] is True
        csrf = (await admin_client.get("/api/v1/auth/csrf")).json()["data"]["csrf_token"]

        create_resp = await admin_client.post(
            "/api/v1/admin/users",
            headers={"X-CSRF-Token": csrf},
            json={
                "username": "pks_op_01",
                "email": "pks01@example.invalid",
                "password": "MillOperatorPass#123",
                "role_code": "MILL_OPERATOR",
                "scope_type": "MILL",
                "mill_id": str(mill_id),
            },
        )
        assert create_resp.status_code == 201
        created_id = create_resp.json()["data"]["id"]

        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as mill_client:
            mill_login = await mill_client.post(
                "/api/v1/auth/login",
                json={"username": "pks_op_01", "password": "MillOperatorPass#123"},
            )
            assert mill_login.status_code == 200

            # Privilege escalation attempt: MILL_OPERATOR calling /api/v1/admin/users -> 403.
            escalate = await mill_client.get("/api/v1/admin/users")
            assert escalate.status_code == 403
            assert escalate.json()["error"]["code"] == "AUTH_ACCESS_DENIED"

            # Admin disables mill operator -> active session revoked immediately in PG + Redis.
            disable_resp = await admin_client.patch(
                f"/api/v1/admin/users/{created_id}",
                headers={"X-CSRF-Token": csrf},
                json={"status": "INACTIVE", "reason": "Rotasi petugas PKS selesai"},
            )
            assert disable_resp.status_code == 200
            assert disable_resp.json()["data"]["status"] == "INACTIVE"

            after_disable = await mill_client.get("/api/v1/auth/me")
            assert after_disable.status_code == 401
            assert after_disable.json()["error"]["code"] == "AUTH_SESSION_EXPIRED"


@pytest.mark.asyncio
async def test_http_cross_scope_guard_and_br_sys_002_approver_block(b1_env: dict) -> None:
    app = b1_env["app"]
    sf = b1_env["session_factory"]

    farmer_a, farmer_b = uuid4(), uuid4()
    await _insert_user(
        sf,
        username="scope_farmer_a",
        password="FarmerPass#2026",
        role=RoleCode.FARMER,
        scope=ScopeType.FARMER,
        farmer_id=farmer_a,
    )
    await _insert_user(
        sf,
        username="scope_admin_01",
        password="AdminPass#2026",
        role=RoleCode.SYSTEM_ADMIN,
        scope=ScopeType.PERUMDA_GLOBAL,
    )

    @app.get("/_test/farmers/{farmer_id}")
    async def _scoped_farmer_probe(
        farmer_id: str,
        principal: Annotated[
            AuthenticatedPrincipal,
            Depends(
                require_access(
                    allowed_roles=(RoleCode.FARMER,),
                    required_permissions=("farmers.read",),
                )
            ),
        ],
    ) -> dict[str, str]:
        assert_farmer_scope(principal, UUID(farmer_id))
        return {"farmer_id": farmer_id}

    @app.post("/_test/payments/{invoice_id}/approve")
    async def _approver_probe(
        invoice_id: str,
        _principal: Annotated[
            AuthenticatedPrincipal,
            Depends(
                require_access(
                    allowed_roles=(RoleCode.DIRECTOR,),
                    required_permissions=("payments.approve",),
                )
            ),
        ],
    ) -> dict[str, str]:
        return {"invoice_id": invoice_id}

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as farmer_c:
        await farmer_c.post(
            "/api/v1/auth/login",
            json={"username": "scope_farmer_a", "password": "FarmerPass#2026"},
        )
        own_ok = await farmer_c.get(f"/_test/farmers/{farmer_a}")
        assert own_ok.status_code == 200
        cross_denied = await farmer_c.get(f"/_test/farmers/{farmer_b}")
        assert cross_denied.status_code == 403
        assert cross_denied.json()["error"]["code"] == "AUTH_SCOPE_FORBIDDEN"

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as admin_c:
        await admin_c.post(
            "/api/v1/auth/login",
            json={"username": "scope_admin_01", "password": "AdminPass#2026"},
        )
        csrf = (await admin_c.get("/api/v1/auth/csrf")).json()["data"]["csrf_token"]
        approver_blocked = await admin_c.post(
            f"/_test/payments/{uuid4()}/approve",
            headers={"X-CSRF-Token": csrf},
        )
        assert approver_blocked.status_code == 403
        assert approver_blocked.json()["error"]["code"] == "AUTH_OPERATION_FORBIDDEN"


@pytest.mark.asyncio
async def test_login_rate_limiting_and_redis_fail_closed_security(
    b1_env: dict, test_db_url: str | None
) -> None:
    app = b1_env["app"]
    sf = b1_env["session_factory"]

    await _insert_user(
        sf,
        username="rate_target",
        password="TargetPassword#2026",
        role=RoleCode.DIRECTOR,
        scope=ScopeType.PERUMDA_GLOBAL,
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        for _ in range(4):
            bad = await client.post(
                "/api/v1/auth/login",
                json={"username": "rate_target", "password": "WrongPassword#123"},
            )
            assert bad.status_code == 401

        blocked = await client.post(
            "/api/v1/auth/login",
            json={"username": "rate_target", "password": "TargetPassword#2026"},
        )
        assert blocked.status_code == 429
        assert blocked.json()["error"]["code"] == "AUTH_TOO_MANY_REQUESTS"
        assert int(blocked.headers["Retry-After"]) >= 1

    # Fail-closed check: authentication & session checks must return 503 when Redis is unavailable.
    down_app = create_app(
        settings=Settings(LOG_JSON=False),
        db_dsn_override=test_db_url,
        redis_url_override="redis://127.0.0.1:6399/1",
    )
    async with down_app.router.lifespan_context(down_app):
        down_transport = httpx.ASGITransport(app=down_app)
        async with httpx.AsyncClient(
            transport=down_transport,
            base_url="http://testserver",
            cookies={b1_env["cfg"].SESSION_COOKIE_NAME: "anytoken"},
        ) as c:
            down_login = await c.post(
                "/api/v1/auth/login",
                json={"username": "rate_target", "password": "TargetPassword#2026"},
            )
            assert down_login.status_code == 503
            assert down_login.json()["error"]["code"] == "SYS_DEPENDENCY_UNAVAILABLE"

            down_me = await c.get("/api/v1/auth/me")
            assert down_me.status_code == 503
            assert down_me.json()["error"]["code"] == "SYS_DEPENDENCY_UNAVAILABLE"
