"""Integration tests for Public Portal, Pricing SM-01, Redis cache fallback, and races (B3)."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import httpx
import pytest
from app.core.config import Settings
from app.core.database import build_async_engine, build_session_factory, dispose_database
from app.core.redis import RedisClientManager
from app.main import create_app
from app.modules.identity_access.domain.entities import RoleCode, ScopeType
from app.modules.identity_access.infrastructure.models import (
    UserAccessScopeModel,
    UserAccountModel,
    UserRoleGrantModel,
    deterministic_role_id,
    seed_rbac_catalog,
)
from app.modules.identity_access.infrastructure.security_adapters import Argon2PasswordHasher
from app.modules.master_data.infrastructure.models import (
    CooperativeModel,
    FarmerModel,
    MillCompanyModel,
    MillModel,
    PartyModel,
    PerumdaOfficeModel,
)
from app.modules.pricing.infrastructure.models import (
    deterministic_category_id,
    deterministic_source_id,
    seed_pricing_catalog,
)
from app.modules.public_portal.infrastructure.models import PublicNoticeModel
from redis.asyncio import Redis
from sqlalchemy import text


async def _login(
    transport: httpx.ASGITransport, *, username: str, password: str
) -> tuple[httpx.AsyncClient, str]:
    c = httpx.AsyncClient(transport=transport, base_url="http://testserver")
    resp = await c.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    csrf = (await c.get("/api/v1/auth/csrf")).json()["data"]["csrf_token"]
    return c, csrf


@pytest.fixture
async def b3_env(test_db_url: str | None, test_redis_url: str | None) -> AsyncIterator[dict]:
    assert test_db_url and test_redis_url
    assert test_redis_url.endswith("/1")

    cfg = Settings(LOG_JSON=False)
    engine = build_async_engine(cfg, dsn_override=test_db_url)
    sf = build_session_factory(engine)
    redis_client = Redis.from_url(test_redis_url, decode_responses=True)

    now = datetime.now(UTC)
    hasher = Argon2PasswordHasher()
    pw_hash = await hasher.hash_password("PricingPass#2026")

    public_mill_id, private_mill_id, unverified_coord_mill_id = uuid4(), uuid4(), uuid4()
    farmer_id = uuid4()

    async with sf() as session:
        async with session.begin():
            await session.execute(
                text(
                    "TRUNCATE TABLE audit_events, auth_sessions, user_access_scopes, "
                    "user_role_grants, user_accounts, price_verification_events, "
                    "mill_price_quotes, disbun_reference_prices, public_notices, public_pages, "
                    "farms, cooperative_memberships, farmers, cooperatives, mills, mill_companies, "
                    "perumda_offices, vehicles, drivers, parties RESTART IDENTITY CASCADE"
                )
            )
            await seed_rbac_catalog(session)
            await seed_pricing_catalog(session)

            # Seed Mill Company & 3 Mills (public verified, private, public unverified-coords).
            p_mc, mc_id = uuid4(), uuid4()
            session.add(
                PartyModel(
                    id=p_mc,
                    party_type="MILL_COMPANY",
                    display_name="PT Sawit Utama",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()
            session.add(
                MillCompanyModel(
                    id=mc_id,
                    party_id=p_mc,
                    company_code="MC-B3-01",
                    company_name="PT Sawit Utama Pelalawan",
                    contact_phone="0761000101",
                    address="Jl. Lintas Timur",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()

            session.add(
                MillModel(
                    id=public_mill_id,
                    mill_company_id=mc_id,
                    mill_code="PKS-PUB-01",
                    mill_name="PKS Pangkalan Kerinci",
                    address="Jl. Lintas Timur KM 58",
                    district="Pangkalan Kerinci",
                    regency="Pelalawan",
                    province="Riau",
                    latitude=0.402100,
                    longitude=101.860400,
                    contact_phone="0761-000-201",
                    partnership_status="ACTIVE",
                    is_public=True,
                    location_verified_at=now,
                    version=1,
                    created_at=now,
                    updated_at=now,
                )
            )
            session.add(
                MillModel(
                    id=private_mill_id,
                    mill_company_id=mc_id,
                    mill_code="PKS-PRIV-02",
                    mill_name="PKS Ukui Rahasia",
                    address="Jl. Ukui",
                    district="Ukui",
                    regency="Pelalawan",
                    province="Riau",
                    latitude=0.181200,
                    longitude=102.041100,
                    contact_phone="0761-999-999",
                    partnership_status="ACTIVE",
                    is_public=False,
                    location_verified_at=now,
                    version=1,
                    created_at=now,
                    updated_at=now,
                )
            )
            session.add(
                MillModel(
                    id=unverified_coord_mill_id,
                    mill_company_id=mc_id,
                    mill_code="PKS-NOCOORD-03",
                    mill_name="PKS Langgam Baru",
                    address="Desa Tambak",
                    district="Langgam",
                    regency="Pelalawan",
                    province="Riau",
                    latitude=None,
                    longitude=None,
                    contact_phone="0761-000-202",
                    partnership_status="ACTIVE",
                    is_public=True,
                    location_verified_at=None,
                    version=1,
                    created_at=now,
                    updated_at=now,
                )
            )

            # Seed Perumda Office & Public Notice (w/ XSS attempt).
            session.add(
                PerumdaOfficeModel(
                    id=uuid4(),
                    party_id=None,
                    office_name="Kantor Pusat Unit Agro Niaga",
                    address="Komplek Perkantoran Bhakti Praja Pelalawan",
                    latitude=0.391000,
                    longitude=101.855000,
                    public_contact="(0761) 494000",
                    is_public=True,
                    created_at=now,
                    updated_at=now,
                )
            )
            session.add(
                PublicNoticeModel(
                    id=uuid4(),
                    title="Update <b>Jadwal Harga</b><script>bad()</script>",
                    body="<p>Harga diperbarui setiap hari kerja.</p>",
                    start_at=now - timedelta(hours=1),
                    end_at=now + timedelta(days=3),
                    status="PUBLISHED",
                    created_by=None,
                    created_at=now,
                )
            )

            # Seed Farmer + Coop for scoped read boundary check.
            p_coop, coop_id, p_farmer = uuid4(), uuid4(), uuid4()
            session.add(
                PartyModel(
                    id=p_coop,
                    party_type="COOPERATIVE",
                    display_name="KUD Test",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            session.add(
                PartyModel(
                    id=p_farmer,
                    party_type="FARMER",
                    display_name="Farmer B3",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()
            session.add(
                CooperativeModel(
                    id=coop_id,
                    party_id=p_coop,
                    cooperative_code="KOP-B3",
                    cooperative_name="KUD Test",
                    address="Pelalawan",
                    contact_phone="0761001122",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            session.add(
                FarmerModel(
                    id=farmer_id,
                    party_id=p_farmer,
                    farmer_code="PET-B3",
                    full_name="Farmer B3",
                    contact_phone="08120000111",
                    identity_reference=None,
                    status="ACTIVE",
                    version=1,
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()

            actors = [
                ("ops_maker", RoleCode.PERUMDA_OPERATIONS, ScopeType.PERUMDA_GLOBAL, None),
                ("ops_checker", RoleCode.PERUMDA_OPERATIONS, ScopeType.PERUMDA_GLOBAL, None),
                ("farmer_b3", RoleCode.FARMER, ScopeType.FARMER, farmer_id),
            ]
            for uname, role_enum, scope_enum, fid in actors:
                uid = uuid4()
                session.add(
                    UserAccountModel(
                        id=uid,
                        username=uname,
                        email=f"{uname}@test.local",
                        display_name=uname,
                        password_hash=pw_hash,
                        linked_party_id=None,
                        status="ACTIVE",
                        failed_login_count=0,
                        last_login_at=None,
                        created_at=now,
                        updated_at=now,
                    )
                )
                session.add(
                    UserRoleGrantModel(
                        id=uuid4(),
                        user_id=uid,
                        role_id=deterministic_role_id(role_enum.value),
                        granted_by=None,
                        granted_at=now,
                        revoked_at=None,
                    )
                )
                session.add(
                    UserAccessScopeModel(
                        id=uuid4(),
                        user_id=uid,
                        scope_type=scope_enum.value,
                        farmer_id=fid,
                        cooperative_id=None,
                        mill_id=None,
                        granted_by=None,
                        created_at=now,
                        revoked_at=None,
                    )
                )

    await redis_client.flushdb()
    app = create_app(settings=cfg, db_dsn_override=test_db_url, redis_url_override=test_redis_url)
    async with app.router.lifespan_context(app):
        yield {
            "app": app,
            "cfg": cfg,
            "sf": sf,
            "redis": redis_client,
            "public_mill_id": public_mill_id,
            "private_mill_id": private_mill_id,
            "unverified_mill_id": unverified_coord_mill_id,
        }

    await redis_client.flushdb()
    await redis_client.aclose()
    await dispose_database(engine)


@pytest.mark.asyncio
async def test_pricing_sm01_sod01_public_privacy_cache_and_fallback(
    b3_env: dict, test_db_url: str | None
) -> None:
    app = b3_env["app"]
    public_mill_id: UUID = b3_env["public_mill_id"]
    private_mill_id: UUID = b3_env["private_mill_id"]
    unverified_mill_id: UUID = b3_env["unverified_mill_id"]
    transport = httpx.ASGITransport(app=app)

    src_mill = str(deterministic_source_id("MILL_OFFICIAL"))
    src_disbun = str(deterministic_source_id("DISBUN_RIAU"))
    cat_swadaya = str(deterministic_category_id("SWADAYA_STD"))
    cat_plasma = str(deterministic_category_id("PLASMA_KONTRAK"))
    cat_disbun = str(deterministic_category_id("DISBUN_10_20"))

    now = datetime.now(UTC)
    valid_from = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    valid_until = (now + timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ")
    expired_from = (now - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    expired_until = (now - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")

    anon = httpx.AsyncClient(transport=transport, base_url="http://testserver")
    maker, csrf_maker = await _login(transport, username="ops_maker", password="PricingPass#2026")
    checker, csrf_checker = await _login(
        transport, username="ops_checker", password="PricingPass#2026"
    )
    farmer, _ = await _login(transport, username="farmer_b3", password="PricingPass#2026")

    try:
        # Internal pricing endpoints require auth.
        assert (await anon.get("/api/v1/prices")).status_code == 401
        assert (await anon.get("/api/v1/prices/reference-meta")).status_code == 401

        # Public endpoints work without auth and return empty gracefully when none published.
        empty_pub = await anon.get("/api/v1/public/prices")
        assert empty_pub.status_code == 200
        assert empty_pub.json()["data"] == []

        # Create DISBUN reference price separately.
        disbun = await maker.post(
            "/api/v1/prices/disbun",
            headers={"X-CSRF-Token": csrf_maker},
            json={
                "price_source_id": src_disbun,
                "price_category_id": cat_disbun,
                "price_per_kg": "3120.50",
                "effective_from": valid_from,
                "effective_until": valid_until,
            },
        )
        assert disbun.status_code == 201
        assert len((await anon.get("/api/v1/public/disbun-prices")).json()["data"]) == 1

        # Create draft using DISBUN source must fail (BR-CMP-001).
        bad_src = await maker.post(
            "/api/v1/prices",
            headers={"X-CSRF-Token": csrf_maker},
            json={
                "mill_id": str(public_mill_id),
                "price_category_id": cat_swadaya,
                "source_id": src_disbun,
                "price_per_kg": "2900.00",
                "effective_from": valid_from,
            },
        )
        assert bad_src.status_code == 422

        # Maker creates active DRAFT quote, Farmer cannot view DRAFT!
        draft = await maker.post(
            "/api/v1/prices",
            headers={"X-CSRF-Token": csrf_maker},
            json={
                "mill_id": str(public_mill_id),
                "price_category_id": cat_swadaya,
                "source_id": src_mill,
                "price_per_kg": "2920.00",
                "effective_from": valid_from,
                "effective_until": valid_until,
                "notes": "Simulasi harga PKS",
            },
        )
        assert draft.status_code == 201
        qid = draft.json()["data"]["id"]

        assert (await farmer.get(f"/api/v1/prices/{qid}")).status_code == 403
        assert (await anon.get(f"/api/v1/public/prices/{qid}")).status_code == 404

        # Submit -> Verify (Maker==Checker rejected SOD-01!) -> Checker approves -> Publish!
        sub = await maker.post(f"/api/v1/prices/{qid}/submit", headers={"X-CSRF-Token": csrf_maker})
        assert sub.status_code == 200
        assert sub.json()["data"]["status"] == "PENDING_VERIFICATION"

        self_verify = await maker.post(
            f"/api/v1/prices/{qid}/verify",
            headers={"X-CSRF-Token": csrf_maker},
            json={"decision": "APPROVE"},
        )
        assert self_verify.status_code == 403
        assert self_verify.json()["error"]["code"] == "AUTH_CONFLICT_OF_DUTIES"

        # Publish before verification rejected.
        unver_pub = await maker.post(
            f"/api/v1/prices/{qid}/publish", headers={"X-CSRF-Token": csrf_maker}
        )
        assert unver_pub.status_code == 409
        assert unver_pub.json()["error"]["code"] == "PRICE_NOT_VERIFIED"

        ver = await checker.post(
            f"/api/v1/prices/{qid}/verify",
            headers={"X-CSRF-Token": csrf_checker},
            json={"decision": "APPROVE"},
        )
        assert ver.status_code == 200
        assert ver.json()["data"]["status"] == "VERIFIED"

        pub = await maker.post(
            f"/api/v1/prices/{qid}/publish", headers={"X-CSRF-Token": csrf_maker}
        )
        assert pub.status_code == 200
        assert pub.json()["data"]["status"] == "PUBLISHED"

        # Seed a PUBLISHED price for PRIVATE mill -> MUST NEVER appear on public portal!
        priv_draft = await maker.post(
            "/api/v1/prices",
            headers={"X-CSRF-Token": csrf_maker},
            json={
                "mill_id": str(private_mill_id),
                "price_category_id": cat_swadaya,
                "source_id": src_mill,
                "price_per_kg": "3500.00",
                "effective_from": valid_from,
                "effective_until": valid_until,
            },
        )
        priv_id = priv_draft.json()["data"]["id"]
        await maker.post(f"/api/v1/prices/{priv_id}/submit", headers={"X-CSRF-Token": csrf_maker})
        await checker.post(
            f"/api/v1/prices/{priv_id}/verify",
            headers={"X-CSRF-Token": csrf_checker},
            json={"decision": "APPROVE"},
        )
        await maker.post(f"/api/v1/prices/{priv_id}/publish", headers={"X-CSRF-Token": csrf_maker})

        # Seed an EXPIRED quote and a PLASMA_KONTRAK quote on public_mill_id.
        exp_draft = await maker.post(
            "/api/v1/prices",
            headers={"X-CSRF-Token": csrf_maker},
            json={
                "mill_id": str(public_mill_id),
                "price_category_id": cat_swadaya,
                "source_id": src_mill,
                "price_per_kg": "2750.00",
                "effective_from": expired_from,
                "effective_until": expired_until,
            },
        )
        eid = exp_draft.json()["data"]["id"]
        await maker.post(f"/api/v1/prices/{eid}/submit", headers={"X-CSRF-Token": csrf_maker})
        await checker.post(
            f"/api/v1/prices/{eid}/verify",
            headers={"X-CSRF-Token": csrf_checker},
            json={"decision": "APPROVE"},
        )
        await maker.post(f"/api/v1/prices/{eid}/publish", headers={"X-CSRF-Token": csrf_maker})

        plasma_draft = await maker.post(
            "/api/v1/prices",
            headers={"X-CSRF-Token": csrf_maker},
            json={
                "mill_id": str(public_mill_id),
                "price_category_id": cat_plasma,
                "source_id": src_mill,
                "price_per_kg": "3050.00",
                "effective_from": valid_from,
                "effective_until": valid_until,
            },
        )
        pid_q = plasma_draft.json()["data"]["id"]
        await maker.post(f"/api/v1/prices/{pid_q}/submit", headers={"X-CSRF-Token": csrf_maker})
        await checker.post(
            f"/api/v1/prices/{pid_q}/verify",
            headers={"X-CSRF-Token": csrf_checker},
            json={"decision": "APPROVE"},
        )
        await maker.post(f"/api/v1/prices/{pid_q}/publish", headers={"X-CSRF-Token": csrf_maker})

        # Flush & exercise Redis cache hit + miss telemetry cleanly.
        redis_mgr: RedisClientManager = app.state.redis_manager
        before_hits = redis_mgr.metrics.hits
        r1 = await anon.get("/api/v1/public/prices?category_code=SWADAYA_STD")
        assert r1.status_code == 200
        assert [row["id"] for row in r1.json()["data"]] == [
            qid
        ]  # Excludes expired & private & plasma!
        r2 = await anon.get("/api/v1/public/prices?category_code=SWADAYA_STD")
        assert r2.status_code == 200
        assert redis_mgr.metrics.hits >= before_hits + 1

        # include_expired=true returns expired quote with display_status="EXPIRED".
        with_exp = await anon.get(
            "/api/v1/public/prices?category_code=SWADAYA_STD&include_expired=true"
        )
        statuses = {x["id"]: x["display_status"] for x in with_exp.json()["data"]}
        assert statuses[qid] == "PUBLISHED"
        assert statuses[eid] == "EXPIRED"
        assert priv_id not in statuses

        # Private mill detail & private quote detail return 404.
        assert (await anon.get(f"/api/v1/public/prices/{priv_id}")).status_code == 404
        assert (await anon.get(f"/api/v1/public/mills/{private_mill_id}")).status_code == 404

        # Public mills exclude private mill and hide unverified coords cleanly.
        pub_mills = await anon.get("/api/v1/public/mills")
        mill_map = {m["id"]: m for m in pub_mills.json()["data"]}
        assert str(private_mill_id) not in mill_map
        assert mill_map[str(public_mill_id)]["has_verified_coordinates"] is True
        assert mill_map[str(unverified_mill_id)]["has_verified_coordinates"] is False
        assert mill_map[str(unverified_mill_id)]["latitude"] is None

        # Profile & XSS-sanitized notices.
        prof = await anon.get("/api/v1/public/profile")
        assert "Listrik dan Gas" in prof.json()["data"]["excluded_units_notice"]
        notices = await anon.get("/api/v1/public/notices")
        assert "<script>" not in notices.json()["data"][0]["title"]

        # Revoke active quote -> cache invalidated immediately!
        rev = await maker.post(
            f"/api/v1/prices/{qid}/revoke",
            headers={"X-CSRF-Token": csrf_maker},
            json={"reason": "Koreksi papan harga resmi sore hari"},
        )
        assert rev.status_code == 200
        assert rev.json()["data"]["status"] == "REVOKED"
        after_revoke = await anon.get("/api/v1/public/prices?category_code=SWADAYA_STD")
        assert after_revoke.json()["data"] == []

        # Redis failure fallback on public reads returns 200 OK seamlessly from PostgreSQL.
        down_app = create_app(
            settings=Settings(LOG_JSON=False),
            db_dsn_override=test_db_url,
            redis_url_override="redis://127.0.0.1:6399/1",
        )
        async with down_app.router.lifespan_context(down_app):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=down_app), base_url="http://testserver"
            ) as fallback_client:
                fb_mills = await fallback_client.get("/api/v1/public/mills")
                assert fb_mills.status_code == 200
                assert str(public_mill_id) in {m["id"] for m in fb_mills.json()["data"]}
    finally:
        await anon.aclose()
        await maker.aclose()
        await checker.aclose()
        await farmer.aclose()


@pytest.mark.asyncio
async def test_concurrent_price_publication_prevents_overlapping_periods(b3_env: dict) -> None:
    app = b3_env["app"]
    mill_id: UUID = b3_env["public_mill_id"]
    transport = httpx.ASGITransport(app=app)
    src_mill = str(deterministic_source_id("MILL_OFFICIAL"))
    cat_swadaya = str(deterministic_category_id("SWADAYA_STD"))

    now = datetime.now(UTC)
    v_from = (now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    v_until = (now + timedelta(hours=10)).strftime("%Y-%m-%dT%H:%M:%SZ")

    maker, csrf_m = await _login(transport, username="ops_maker", password="PricingPass#2026")
    checker, csrf_c = await _login(transport, username="ops_checker", password="PricingPass#2026")
    try:
        quote_ids: list[str] = []
        for price_str in ("2900.00", "2950.00"):
            d = await maker.post(
                "/api/v1/prices",
                headers={"X-CSRF-Token": csrf_m},
                json={
                    "mill_id": str(mill_id),
                    "price_category_id": cat_swadaya,
                    "source_id": src_mill,
                    "price_per_kg": price_str,
                    "effective_from": v_from,
                    "effective_until": v_until,
                },
            )
            qid = d.json()["data"]["id"]
            await maker.post(f"/api/v1/prices/{qid}/submit", headers={"X-CSRF-Token": csrf_m})
            await checker.post(
                f"/api/v1/prices/{qid}/verify",
                headers={"X-CSRF-Token": csrf_c},
                json={"decision": "APPROVE"},
            )
            quote_ids.append(qid)

        res1, res2 = await asyncio.gather(
            maker.post(f"/api/v1/prices/{quote_ids[0]}/publish", headers={"X-CSRF-Token": csrf_m}),
            maker.post(f"/api/v1/prices/{quote_ids[1]}/publish", headers={"X-CSRF-Token": csrf_m}),
        )
        codes = sorted([res1.status_code, res2.status_code])
        assert codes == [200, 409]
        conflict_resp = res1 if res1.status_code == 409 else res2
        assert conflict_resp.json()["error"]["code"] == "PRICE_OVERLAPPING_PERIOD"
        assert "conflicting_price_quote_id" in conflict_resp.json()["error"]["details"]
    finally:
        await maker.aclose()
        await checker.aclose()
