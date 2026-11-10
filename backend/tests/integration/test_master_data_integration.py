"""Integration tests for Master Data CRUD, FKs, scopes, optimistic locks, and cache."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import UUID, uuid4

import httpx
import pytest
from app.core.config import Settings
from app.core.database import build_async_engine, build_session_factory, dispose_database
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
    CooperativeMembershipModel,
    CooperativeModel,
    PartyModel,
)
from redis.asyncio import Redis
from sqlalchemy import select, text


async def _login_client(
    transport: httpx.ASGITransport, *, username: str, password: str
) -> tuple[httpx.AsyncClient, str]:
    client = httpx.AsyncClient(transport=transport, base_url="http://testserver")
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200
    csrf = (await client.get("/api/v1/auth/csrf")).json()["data"]["csrf_token"]
    return client, csrf


@pytest.fixture
async def b2_env(test_db_url: str | None, test_redis_url: str | None) -> AsyncIterator[dict]:
    assert test_db_url and test_redis_url
    assert test_redis_url.endswith("/1")

    cfg = Settings(LOG_JSON=False)
    engine = build_async_engine(cfg, dsn_override=test_db_url)
    sf = build_session_factory(engine)
    redis_client = Redis.from_url(test_redis_url, decode_responses=True)

    now = datetime.now(UTC)
    hasher = Argon2PasswordHasher()
    pw_hash = await hasher.hash_password("MasterPass#2026")

    coop1_id, coop2_id = uuid4(), uuid4()
    async with sf() as session:
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

            for idx, (cid, code, name) in enumerate(
                [
                    (coop1_id, "KOP-01", "KUD Sejahtera"),
                    (coop2_id, "KOP-02", "KUD Makmur"),
                ],
                start=1,
            ):
                pid = uuid4()
                session.add(
                    PartyModel(
                        id=pid,
                        party_type="COOPERATIVE",
                        display_name=name,
                        status="ACTIVE",
                        created_at=now,
                        updated_at=now,
                    )
                )
                await session.flush()
                session.add(
                    CooperativeModel(
                        id=cid,
                        party_id=pid,
                        cooperative_code=code,
                        cooperative_name=name,
                        address=f"Jl. Poros {idx}, Pelalawan",
                        contact_phone=f"0761000{idx}",
                        status="ACTIVE",
                        created_at=now,
                        updated_at=now,
                    )
                )

            users_spec = [
                ("perumda_ops_b2", RoleCode.PERUMDA_OPERATIONS, ScopeType.PERUMDA_GLOBAL, None),
                ("kop1_op_b2", RoleCode.COOPERATIVE_OPERATOR, ScopeType.COOPERATIVE, coop1_id),
                ("kop2_op_b2", RoleCode.COOPERATIVE_OPERATOR, ScopeType.COOPERATIVE, coop2_id),
            ]
            for uname, role_enum, scope_enum, c_target in users_spec:
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
                        farmer_id=None,
                        cooperative_id=c_target,
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
            "sf": sf,
            "redis": redis_client,
            "coop1_id": coop1_id,
            "coop2_id": coop2_id,
            "pw_hash": pw_hash,
        }

    await redis_client.flushdb()
    await redis_client.aclose()
    await dispose_database(engine)


@pytest.mark.asyncio
async def test_farmers_farms_cross_coop_scope_deactivation_and_version_conflict(
    b2_env: dict,
) -> None:
    app = b2_env["app"]
    sf = b2_env["sf"]
    coop1_id: UUID = b2_env["coop1_id"]
    coop2_id: UUID = b2_env["coop2_id"]
    transport = httpx.ASGITransport(app=app)

    kop1, csrf1 = await _login_client(transport, username="kop1_op_b2", password="MasterPass#2026")
    kop2, csrf2 = await _login_client(transport, username="kop2_op_b2", password="MasterPass#2026")
    ops, csrf_ops = await _login_client(
        transport, username="perumda_ops_b2", password="MasterPass#2026"
    )
    try:
        # Cross-coop creation denied.
        bad_scope = await kop1.post(
            "/api/v1/farmers",
            headers={"X-CSRF-Token": csrf1},
            json={
                "farmer_code": "PET-X01",
                "full_name": "Petani Koperasi Sebelah",
                "contact_phone": "0811111111",
                "cooperative_id": str(coop2_id),
            },
        )
        assert bad_scope.status_code == 403
        assert bad_scope.json()["error"]["code"] == "AUTH_SCOPE_FORBIDDEN"

        # Valid farmer creation in coop1.
        create_f = await kop1.post(
            "/api/v1/farmers",
            headers={"X-CSRF-Token": csrf1},
            json={
                "farmer_code": "PET-001",
                "full_name": "Hendra Wijaya",
                "contact_phone": "081234567890",
                "cooperative_id": str(coop1_id),
                "membership_number": "KOP1-2026-01",
            },
        )
        assert create_f.status_code == 201
        farmer = create_f.json()["data"]
        farmer_id = farmer["id"]
        assert farmer["version"] == 1

        # Duplicate farmer_code -> 409 MD_DUPLICATE_CODE.
        dup_f = await kop1.post(
            "/api/v1/farmers",
            headers={"X-CSRF-Token": csrf1},
            json={
                "farmer_code": "PET-001",
                "full_name": "Duplikat",
                "contact_phone": "081234567891",
                "cooperative_id": str(coop1_id),
            },
        )
        assert dup_f.status_code == 409
        assert dup_f.json()["error"]["code"] == "MD_DUPLICATE_CODE"

        # Cross-coop read and farm creation denied.
        assert (await kop2.get(f"/api/v1/farmers/{farmer_id}")).status_code == 403
        assert (await kop2.get("/api/v1/farmers")).json()["data"] == []

        # Create farm with invalid unpaired coordinate -> 422 VAL_INVALID_COORDINATES.
        bad_coord = await kop1.post(
            "/api/v1/farms",
            headers={"X-CSRF-Token": csrf1},
            json={
                "farmer_id": farmer_id,
                "farm_code": "KBN-001",
                "farm_name": "Kebun Blok A",
                "area_hectares": "2.5000",
                "village": "Desa Makmur",
                "district": "Pangkalan Kerinci",
                "latitude": "0.381200",
            },
        )
        assert bad_coord.status_code == 422
        assert bad_coord.json()["error"]["code"] == "VAL_INVALID_COORDINATES"

        # Valid farm creation.
        farm_resp = await kop1.post(
            "/api/v1/farms",
            headers={"X-CSRF-Token": csrf1},
            json={
                "farmer_id": farmer_id,
                "farm_code": "KBN-001",
                "farm_name": "Kebun Blok A",
                "area_hectares": "2.5000",
                "planting_year": 2014,
                "stdb_number": "STDB-01",
                "village": "Desa Makmur",
                "district": "Pangkalan Kerinci",
                "latitude": "0.381200",
                "longitude": "101.842100",
            },
        )
        assert farm_resp.status_code == 201
        farm_data = farm_resp.json()["data"]
        assert farm_data["is_public_location"] is False
        assert farm_data["verification_status"] == "VERIFIED"

        # Optimistic locking: valid update increments version, stale version returns 409.
        ok_upd = await kop1.patch(
            f"/api/v1/farms/{farm_data['id']}",
            headers={"X-CSRF-Token": csrf1},
            json={"farm_name": "Kebun Blok A Replanting", "version": 1},
        )
        assert ok_upd.status_code == 200
        assert ok_upd.json()["data"]["version"] == 2
        assert ok_upd.json()["data"]["latitude"] == "0.381200"

        stale_upd = await kop1.patch(
            f"/api/v1/farms/{farm_data['id']}",
            headers={"X-CSRF-Token": csrf1},
            json={"farm_name": "Lost Update", "version": 1},
        )
        assert stale_upd.status_code == 409
        assert stale_upd.json()["error"]["code"] == "MD_STALE_RECORD_VERSION"
        assert stale_upd.json()["error"]["details"] == {
            "expected_version": 1,
            "current_version": 2,
        }

        # Soft deactivation preserves historical membership & farm records cleanly.
        deact = await ops.patch(
            f"/api/v1/farmers/{farmer_id}",
            headers={"X-CSRF-Token": csrf_ops},
            json={"status": "INACTIVE", "reason": "Petani pindah koperasi", "version": 1},
        )
        assert deact.status_code == 200
        assert deact.json()["data"]["status"] == "INACTIVE"
        assert deact.json()["data"]["version"] == 2

        async with sf() as session:
            membership_count = len(
                (
                    await session.execute(
                        select(CooperativeMembershipModel).where(
                            CooperativeMembershipModel.farmer_id == UUID(farmer_id)
                        )
                    )
                )
                .scalars()
                .all()
            )
            assert membership_count == 1
    finally:
        await kop1.aclose()
        await kop2.aclose()
        await ops.aclose()


@pytest.mark.asyncio
async def test_mills_cross_mill_scope_cache_invalidation_vehicles_and_drivers(
    b2_env: dict,
) -> None:
    app = b2_env["app"]
    sf = b2_env["sf"]
    redis_client: Redis = b2_env["redis"]
    pw_hash: str = b2_env["pw_hash"]
    transport = httpx.ASGITransport(app=app)

    ops, csrf_ops = await _login_client(
        transport, username="perumda_ops_b2", password="MasterPass#2026"
    )
    try:
        comp = await ops.post(
            "/api/v1/mill-companies",
            headers={"X-CSRF-Token": csrf_ops},
            json={
                "company_code": "MC-SWU-01",
                "company_name": "PT Sawit Utama",
                "contact_phone": "0761000101",
                "address": "Jl. Lintas Timur KM 58",
            },
        )
        assert comp.status_code == 201
        comp_id = comp.json()["data"]["id"]

        # Seed public mill cache sentinel BEFORE creating public mill.
        await redis_client.set("public:mills:v1:list", '{"stale":true}', ex=120)

        mill1 = await ops.post(
            "/api/v1/mills",
            headers={"X-CSRF-Token": csrf_ops},
            json={
                "mill_company_id": comp_id,
                "mill_code": "PKS-01",
                "mill_name": "PKS Kerinci",
                "address": "Jl. Lintas Timur",
                "district": "Pangkalan Kerinci",
                "regency": "Pelalawan",
                "province": "Riau",
                "latitude": "0.402100",
                "longitude": "101.860400",
                "partnership_status": "ACTIVE",
                "is_public": True,
            },
        )
        assert mill1.status_code == 201
        m1_id = mill1.json()["data"]["id"]
        assert mill1.json()["data"]["has_verified_coordinates"] is True
        # Post-commit public mill cache invalidation removed stale key!
        assert await redis_client.get("public:mills:v1:list") is None

        mill2 = await ops.post(
            "/api/v1/mills",
            headers={"X-CSRF-Token": csrf_ops},
            json={
                "mill_company_id": comp_id,
                "mill_code": "PKS-02",
                "mill_name": "PKS Ukui",
                "address": "Jl. Lintas Ukui",
                "district": "Ukui",
                "regency": "Pelalawan",
                "province": "Riau",
                "partnership_status": "ACTIVE",
                "is_public": False,
            },
        )
        assert mill2.status_code == 201
        m2_id = mill2.json()["data"]["id"]
        assert mill2.json()["data"]["has_verified_coordinates"] is False

        # Provision MILL_OPERATOR scoped exclusively to mill1.
        now = datetime.now(UTC)
        mill_op_id = uuid4()
        async with sf() as session:
            async with session.begin():
                session.add(
                    UserAccountModel(
                        id=mill_op_id,
                        username="mill1_op_b2",
                        email="m1@test.local",
                        display_name="Mill 1 Op",
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
                        user_id=mill_op_id,
                        role_id=deterministic_role_id(RoleCode.MILL_OPERATOR.value),
                        granted_by=None,
                        granted_at=now,
                        revoked_at=None,
                    )
                )
                session.add(
                    UserAccessScopeModel(
                        id=uuid4(),
                        user_id=mill_op_id,
                        scope_type=ScopeType.MILL.value,
                        farmer_id=None,
                        cooperative_id=None,
                        mill_id=UUID(m1_id),
                        granted_by=None,
                        created_at=now,
                        revoked_at=None,
                    )
                )

        m1_client, _ = await _login_client(
            transport, username="mill1_op_b2", password="MasterPass#2026"
        )
        try:
            mills_visible = (await m1_client.get("/api/v1/mills")).json()["data"]
            assert [m["id"] for m in mills_visible] == [m1_id]
            assert (await m1_client.get(f"/api/v1/mills/{m1_id}")).status_code == 200
            cross_mill = await m1_client.get(f"/api/v1/mills/{m2_id}")
            assert cross_mill.status_code == 403
            assert cross_mill.json()["error"]["code"] == "AUTH_SCOPE_FORBIDDEN"
        finally:
            await m1_client.aclose()

        # Vehicles & Drivers.
        veh = await ops.post(
            "/api/v1/vehicles",
            headers={"X-CSRF-Token": csrf_ops},
            json={
                "plate_number": "bm 9042 ts",
                "vehicle_type": "Truk Colt Diesel",
                "nominal_capacity_kg": "12000.000",
            },
        )
        assert veh.status_code == 201
        assert veh.json()["data"]["plate_number"] == "BM 9042 TS"

        dup_veh = await ops.post(
            "/api/v1/vehicles",
            headers={"X-CSRF-Token": csrf_ops},
            json={"plate_number": "BM 9042 TS", "vehicle_type": "Dump Truck"},
        )
        assert dup_veh.status_code == 409
        assert dup_veh.json()["error"]["code"] == "MD_DUPLICATE_CODE"

        drv = await ops.post(
            "/api/v1/drivers",
            headers={"X-CSRF-Token": csrf_ops},
            json={
                "full_name": "Rahmat Hidayat",
                "contact_phone": "08120000111",
                "driver_reference": "DRV-01",
            },
        )
        assert drv.status_code == 201
        assert len((await ops.get("/api/v1/drivers")).json()["data"]) == 1
    finally:
        await ops.aclose()
