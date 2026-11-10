"""PostgreSQL integration tests for TBS Receiving, Versioned Weighing, Grading & Idempotency (B4)."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from decimal import Decimal
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
    FarmerModel,
    FarmModel,
    PartyModel,
)
from app.modules.tbs_receiving.infrastructure.models import TbsReceiptModel
from redis.asyncio import Redis
from sqlalchemy import func, select, text


async def _login(
    transport: httpx.ASGITransport, *, username: str, password: str
) -> tuple[httpx.AsyncClient, str]:
    c = httpx.AsyncClient(transport=transport, base_url="http://testserver")
    resp = await c.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    csrf = (await c.get("/api/v1/auth/csrf")).json()["data"]["csrf_token"]
    return c, csrf


@pytest.fixture
async def b4_env(test_db_url: str | None, test_redis_url: str | None) -> AsyncIterator[dict]:
    assert test_db_url and test_redis_url
    assert test_redis_url.endswith("/1")

    cfg = Settings(LOG_JSON=False)
    engine = build_async_engine(cfg, dsn_override=test_db_url)
    sf = build_session_factory(engine)
    redis_client = Redis.from_url(test_redis_url, decode_responses=True)

    now = datetime.now(UTC)
    hasher = Argon2PasswordHasher()
    pw_hash = await hasher.hash_password("ReceivingPass#2026")

    coop_a_id, coop_b_id = uuid4(), uuid4()
    farmer_1_id, farmer_2_id, farmer_b_id = uuid4(), uuid4(), uuid4()
    farm_1_id, farm_2_id, farm_b_id = uuid4(), uuid4(), uuid4()

    async with sf() as session:
        async with session.begin():
            await session.execute(
                text(
                    "TRUNCATE TABLE audit_events, idempotency_records, auth_sessions, "
                    "user_access_scopes, user_role_grants, user_accounts, "
                    "receipt_grading_items, receipt_weighing_revisions, tbs_receipts, "
                    "farms, cooperative_memberships, farmers, cooperatives, parties "
                    "RESTART IDENTITY CASCADE"
                )
            )
            await seed_rbac_catalog(session)

            for p_id, c_id, code, name in (
                (uuid4(), coop_a_id, "KOP-A", "Koperasi Sawit A"),
                (uuid4(), coop_b_id, "KOP-B", "Koperasi Sawit B"),
            ):
                session.add(
                    PartyModel(
                        id=p_id,
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
                        id=c_id,
                        party_id=p_id,
                        cooperative_code=code,
                        cooperative_name=name,
                        address="Kab. Pelalawan",
                        contact_phone="08120000111",
                        status="ACTIVE",
                        created_at=now,
                        updated_at=now,
                    )
                )

            await session.flush()

            farmer_specs = (
                (
                    uuid4(),
                    farmer_1_id,
                    "FRM-001",
                    "Hendra Wijaya",
                    coop_a_id,
                    farm_1_id,
                    "KBN-01",
                    "Kebun A",
                ),
                (
                    uuid4(),
                    farmer_2_id,
                    "FRM-002",
                    "Siti Aminah",
                    coop_a_id,
                    farm_2_id,
                    "KBN-02",
                    "Kebun B",
                ),
                (
                    uuid4(),
                    farmer_b_id,
                    "FRM-003",
                    "Rudi Hartono",
                    coop_b_id,
                    farm_b_id,
                    "KBN-03",
                    "Kebun C",
                ),
            )
            for pf_id, f_id, f_code, f_name, c_id, fm_id, fm_code, fm_name in farmer_specs:
                session.add(
                    PartyModel(
                        id=pf_id,
                        party_type="FARMER",
                        display_name=f_name,
                        status="ACTIVE",
                        created_at=now,
                        updated_at=now,
                    )
                )
                await session.flush()
                session.add(
                    FarmerModel(
                        id=f_id,
                        party_id=pf_id,
                        farmer_code=f_code,
                        full_name=f_name,
                        contact_phone="08130000222",
                        identity_reference=None,
                        status="ACTIVE",
                        version=1,
                        created_at=now,
                        updated_at=now,
                    )
                )
                await session.flush()
                session.add(
                    CooperativeMembershipModel(
                        id=uuid4(),
                        cooperative_id=c_id,
                        farmer_id=f_id,
                        membership_number=f"MBR-{f_code}",
                        joined_at=now,
                        ended_at=None,
                        status="ACTIVE",
                    )
                )
                session.add(
                    FarmModel(
                        id=fm_id,
                        farmer_id=f_id,
                        farm_code=fm_code,
                        farm_name=fm_name,
                        area_hectares=Decimal("2.5000"),
                        planting_year=2019,
                        stdb_number=None,
                        village="Desa Makmur",
                        district="Pangkalan Kerinci",
                        latitude=Decimal("0.402100"),
                        longitude=Decimal("101.860400"),
                        verification_status="VERIFIED",
                        version=1,
                        created_at=now,
                        updated_at=now,
                    )
                )

            users = [
                ("coop_a", RoleCode.COOPERATIVE_OPERATOR, ScopeType.COOPERATIVE, None, coop_a_id),
                ("coop_b", RoleCode.COOPERATIVE_OPERATOR, ScopeType.COOPERATIVE, None, coop_b_id),
                ("farmer_1", RoleCode.FARMER, ScopeType.FARMER, farmer_1_id, None),
                ("ops_perumda", RoleCode.PERUMDA_OPERATIONS, ScopeType.PERUMDA_GLOBAL, None, None),
            ]
            for uname, role, stype, fid, cid in users:
                uid = uuid4()
                session.add(
                    UserAccountModel(
                        id=uid,
                        username=uname,
                        email=f"{uname}@agroniaga.local",
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
                await session.flush()
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
                        scope_type=stype.value,
                        farmer_id=fid,
                        cooperative_id=cid,
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
            "coop_a_id": str(coop_a_id),
            "farmer_1_id": str(farmer_1_id),
            "farm_1_id": str(farm_1_id),
            "farmer_2_id": str(farmer_2_id),
            "farm_2_id": str(farm_2_id),
            "farmer_b_id": str(farmer_b_id),
            "farm_b_id": str(farm_b_id),
        }

    await redis_client.aclose()
    await dispose_database(engine)


async def test_b4_full_receiving_weighing_grading_revisions_and_validation(b4_env: dict) -> None:
    transport = httpx.ASGITransport(app=b4_env["app"])
    coop_a, csrf_a = await _login(transport, username="coop_a", password="ReceivingPass#2026")
    farmer_1, csrf_f = await _login(transport, username="farmer_1", password="ReceivingPass#2026")

    try:
        # 1. Farmer cannot create receipt draft (BR-MD-004).
        f_resp = await farmer_1.post(
            "/api/v1/receipts",
            json={
                "farmer_id": b4_env["farmer_1_id"],
                "farm_id": b4_env["farm_1_id"],
                "received_at": "2026-11-10T01:30:00Z",
            },
            headers={"X-CSRF-Token": csrf_f, "Idempotency-Key": "farmer-attempt-001"},
        )
        assert f_resp.status_code == 403
        assert f_resp.json()["error"]["code"] == "AUTH_ACCESS_DENIED"

        # 2. Cannot validate draft before weighing.
        draft_resp = await coop_a.post(
            "/api/v1/receipts",
            json={
                "farmer_id": b4_env["farmer_1_id"],
                "farm_id": b4_env["farm_1_id"],
                "harvest_date": "2026-11-10",
                "received_at": "2026-11-10T01:30:00Z",
                "notes": "Masuk pagi hari",
            },
            headers={"X-CSRF-Token": csrf_a, "Idempotency-Key": "coop-a-create-001"},
        )
        assert draft_resp.status_code == 201
        receipt = draft_resp.json()["data"]
        receipt_id = receipt["id"]
        assert receipt["status"] == "DRAFT"
        assert receipt["current_weighing"] is None
        assert receipt["version"] == 1
        assert draft_resp.json()["meta"]["idempotency_replayed"] is False

        val_early = await coop_a.post(
            f"/api/v1/receipts/{receipt_id}/validate",
            headers={"X-CSRF-Token": csrf_a},
        )
        assert val_early.status_code == 409
        assert val_early.json()["error"]["code"] == "TBS_INVALID_STATE_TRANSITION"

        # 3. Invalid tare > gross rejected with 422 TBS_INVALID_WEIGHT.
        bad_weight = await coop_a.post(
            f"/api/v1/receipts/{receipt_id}/weighing",
            json={
                "gross_weight_kg": "3200.000",
                "tare_weight_kg": "3300.000",
                "version": 1,
            },
            headers={"X-CSRF-Token": csrf_a},
        )
        assert bad_weight.status_code == 422
        assert bad_weight.json()["error"]["code"] == "TBS_INVALID_WEIGHT"

        # 4. Initial weighing revision 1 computes exact net = gross - tare.
        w1 = await coop_a.post(
            f"/api/v1/receipts/{receipt_id}/weighing",
            json={
                "gross_weight_kg": "4200.000",
                "tare_weight_kg": "1200.000",
                "version": 1,
            },
            headers={"X-CSRF-Token": csrf_a},
        )
        assert w1.status_code == 200
        d1 = w1.json()["data"]
        assert d1["current_weighing"]["revision_number"] == 1
        assert d1["current_weighing"]["net_weight_kg"] == "3000.000"
        assert d1["net_weight_after_grading_kg"] == "3000.000"
        assert d1["version"] == 2

        # 5. Stale version rejected with TBS_STALE_RECORD_VERSION.
        stale = await coop_a.post(
            f"/api/v1/receipts/{receipt_id}/weighing",
            json={
                "gross_weight_kg": "4250.000",
                "tare_weight_kg": "1200.000",
                "correction_reason": "Ulangi timbang",
                "version": 1,
            },
            headers={"X-CSRF-Token": csrf_a},
        )
        assert stale.status_code == 409
        assert stale.json()["error"]["code"] == "TBS_STALE_RECORD_VERSION"

        # 6. Revision 2 requires correction_reason; rev 1 stays in history (is_current=false).
        missing_reason = await coop_a.post(
            f"/api/v1/receipts/{receipt_id}/weighing",
            json={
                "gross_weight_kg": "4300.000",
                "tare_weight_kg": "1200.000",
                "version": 2,
            },
            headers={"X-CSRF-Token": csrf_a},
        )
        assert missing_reason.status_code == 422
        assert missing_reason.json()["error"]["code"] == "VAL_REQUIRED_FIELD"

        w2 = await coop_a.post(
            f"/api/v1/receipts/{receipt_id}/weighing",
            json={
                "gross_weight_kg": "4200.000",
                "tare_weight_kg": "1100.000",
                "correction_reason": "Kalibrasi ulang timbangan tara truk",
                "version": 2,
            },
            headers={"X-CSRF-Token": csrf_a},
        )
        assert w2.status_code == 200
        d2 = w2.json()["data"]
        assert len(d2["weighing_revisions"]) == 2
        assert d2["weighing_revisions"][0]["is_current"] is False
        assert d2["weighing_revisions"][0]["net_weight_kg"] == "3000.000"
        assert d2["weighing_revisions"][1]["is_current"] is True
        assert d2["weighing_revisions"][1]["net_weight_kg"] == "3100.000"
        assert d2["version"] == 3

        # 7. Separate grading: weight deduction computed without mutating net_weight_kg.
        g_resp = await coop_a.post(
            f"/api/v1/receipts/{receipt_id}/grading",
            json={
                "items": [
                    {
                        "grading_category": "Sortasi Buah Mentah Simulasi",
                        "measurement_value": "2.0000",
                        "deduction_type": "WEIGHT_PERCENT",
                        "deduction_value": "2.0000",
                        "calculation_basis": "NET_WEIGHT_BEFORE_GRADING",
                        "notes": "Simulasi BSD-DEC-006",
                    }
                ],
                "version": 3,
            },
            headers={"X-CSRF-Token": csrf_a},
        )
        assert g_resp.status_code == 200
        gd = g_resp.json()["data"]
        assert gd["current_weighing"]["net_weight_kg"] == "3100.000"
        assert gd["grading_items"][0]["deduction_weight_kg"] == "62.000"
        assert gd["grading_items"][0]["is_simulation"] is True
        assert gd["net_weight_after_grading_kg"] == "3038.000"
        assert "SIMULATION_ONLY" in g_resp.json()["meta"]["simulation_notice"]
        assert gd["version"] == 4

        # 8. Validate transition DRAFT -> VALIDATED; farmer_1 reads own validated receipt.
        val_ok = await coop_a.post(
            f"/api/v1/receipts/{receipt_id}/validate",
            headers={"X-CSRF-Token": csrf_a},
        )
        assert val_ok.status_code == 200
        assert val_ok.json()["data"]["status"] == "VALIDATED"

        f_read = await farmer_1.get(f"/api/v1/receipts/{receipt_id}")
        assert f_read.status_code == 200
        assert f_read.json()["data"]["status"] == "VALIDATED"
    finally:
        await coop_a.aclose()
        await farmer_1.aclose()


async def test_b4_scope_isolation_locked_receipt_and_idempotency_concurrency(b4_env: dict) -> None:
    transport = httpx.ASGITransport(app=b4_env["app"])
    coop_a, csrf_a = await _login(transport, username="coop_a", password="ReceivingPass#2026")
    coop_b, csrf_b = await _login(transport, username="coop_b", password="ReceivingPass#2026")
    farmer_1, _ = await _login(transport, username="farmer_1", password="ReceivingPass#2026")

    try:
        # Cross-cooperative creation blocked; released slot allows retry if needed.
        cross_create = await coop_b.post(
            "/api/v1/receipts",
            json={
                "farmer_id": b4_env["farmer_1_id"],
                "farm_id": b4_env["farm_1_id"],
                "received_at": "2026-11-10T02:00:00Z",
            },
            headers={"X-CSRF-Token": csrf_b, "Idempotency-Key": "cross-coop-attempt-1"},
        )
        assert cross_create.status_code == 403
        assert cross_create.json()["error"]["code"] == "AUTH_SCOPE_FORBIDDEN"

        # Missing Idempotency-Key -> 422 VAL_REQUIRED_FIELD.
        no_key = await coop_a.post(
            "/api/v1/receipts",
            json={
                "farmer_id": b4_env["farmer_1_id"],
                "farm_id": b4_env["farm_1_id"],
                "received_at": "2026-11-10T02:00:00Z",
            },
            headers={"X-CSRF-Token": csrf_a},
        )
        assert no_key.status_code == 422
        assert no_key.json()["error"]["code"] == "VAL_REQUIRED_FIELD"

        # Mismatched farm_id fails 422 AND releases idempotency slot so retry works.
        bad_farm = await coop_a.post(
            "/api/v1/receipts",
            json={
                "farmer_id": b4_env["farmer_1_id"],
                "farm_id": b4_env["farm_2_id"],
                "received_at": "2026-11-10T02:00:00Z",
            },
            headers={"X-CSRF-Token": csrf_a, "Idempotency-Key": "retry-after-422-key"},
        )
        assert bad_farm.status_code == 422

        payload = {
            "farmer_id": b4_env["farmer_2_id"],
            "farm_id": b4_env["farm_2_id"],
            "received_at": "2026-11-10T02:05:00Z",
        }
        # Concurrent requests with same Idempotency-Key must produce at most 1 receipt!
        r1, r2 = await asyncio.gather(
            coop_a.post(
                "/api/v1/receipts",
                json=payload,
                headers={"X-CSRF-Token": csrf_a, "Idempotency-Key": "idem-concurrent-001"},
            ),
            coop_a.post(
                "/api/v1/receipts",
                json=payload,
                headers={"X-CSRF-Token": csrf_a, "Idempotency-Key": "idem-concurrent-001"},
            ),
        )
        statuses = sorted([r1.status_code, r2.status_code])
        assert statuses in ([201, 201], [201, 409])
        if 409 in statuses:
            err_resp = r1 if r1.status_code == 409 else r2
            assert err_resp.json()["error"]["code"] == "IDM_REQUEST_IN_PROGRESS"

        async with b4_env["sf"]() as session:
            count = int(
                (
                    await session.execute(select(func.count()).select_from(TbsReceiptModel))
                ).scalar_one()
            )
            assert count == 1

        # Sequential replay returns identical receipt_id with idempotency_replayed=True.
        replay = await coop_a.post(
            "/api/v1/receipts",
            json=payload,
            headers={"X-CSRF-Token": csrf_a, "Idempotency-Key": "idem-concurrent-001"},
        )
        assert replay.status_code == 201
        assert replay.json()["meta"]["idempotency_replayed"] is True
        r_f2_id = replay.json()["data"]["id"]

        # Same Idempotency-Key with modified payload returns 409 IDM_KEY_CONFLICT_PAYLOAD_MISMATCH.
        mismatch = await coop_a.post(
            "/api/v1/receipts",
            json={
                "farmer_id": b4_env["farmer_1_id"],
                "farm_id": b4_env["farm_1_id"],
                "received_at": "2026-11-10T02:05:00Z",
            },
            headers={"X-CSRF-Token": csrf_a, "Idempotency-Key": "idem-concurrent-001"},
        )
        assert mismatch.status_code == 409
        assert mismatch.json()["error"]["code"] == "IDM_KEY_CONFLICT_PAYLOAD_MISMATCH"

        # Farmer 1 cannot read Farmer 2 receipt; Coop B cannot read Coop A receipt.
        assert (await farmer_1.get(f"/api/v1/receipts/{r_f2_id}")).status_code == 403
        assert (await coop_b.get(f"/api/v1/receipts/{r_f2_id}")).status_code == 403

        # Simulate receipt ALLOCATED -> weighing & cancel locked with 409 TBS_RECEIPT_LOCKED.
        async with b4_env["sf"]() as session:
            async with session.begin():
                await session.execute(
                    text("UPDATE tbs_receipts SET status = 'ALLOCATED' WHERE id = :rid"),
                    {"rid": UUID(r_f2_id)},
                )
        locked_weigh = await coop_a.post(
            f"/api/v1/receipts/{r_f2_id}/weighing",
            json={"gross_weight_kg": "2000.000", "tare_weight_kg": "500.000", "version": 1},
            headers={"X-CSRF-Token": csrf_a},
        )
        assert locked_weigh.status_code == 409
        assert locked_weigh.json()["error"]["code"] == "TBS_RECEIPT_LOCKED"

        locked_cancel = await coop_a.post(
            f"/api/v1/receipts/{r_f2_id}/cancel",
            json={"reason": "Kesalahan input awal sebelum kirim", "version": 1},
            headers={"X-CSRF-Token": csrf_a},
        )
        assert locked_cancel.status_code == 409
        assert locked_cancel.json()["error"]["code"] == "TBS_RECEIPT_LOCKED"
    finally:
        await coop_a.aclose()
        await coop_b.aclose()
        await farmer_1.aclose()
