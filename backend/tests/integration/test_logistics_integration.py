"""PostgreSQL integration tests for Multi-Farmer e-DO, Double-Allocation, SM-05 & QR (B6)."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import httpx
import pytest
from app.core.config import Settings
from app.core.database import build_async_engine, build_session_factory, dispose_database
from app.core.system_rules import RULE_BUSINESS_MODEL_POLICY_ID, seed_baseline_system_rules
from app.main import create_app
from app.modules.contracts.infrastructure.models import (
    ContractQuotaPeriodModel,
    TradeContractModel,
)
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
    DriverModel,
    FarmerModel,
    FarmModel,
    MillCompanyModel,
    MillModel,
    PartyModel,
    VehicleModel,
)
from app.modules.tbs_receiving.infrastructure.models import (
    ReceiptWeighingRevisionModel,
    TbsReceiptModel,
)
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
async def b6_env(test_db_url: str | None, test_redis_url: str | None) -> AsyncIterator[dict]:
    assert test_db_url and test_redis_url
    assert test_redis_url.endswith("/1")

    cfg = Settings(LOG_JSON=False)
    engine = build_async_engine(cfg, dsn_override=test_db_url)
    sf = build_session_factory(engine)
    redis_client = Redis.from_url(test_redis_url, decode_responses=True)

    now = datetime.now(UTC)
    hasher = Argon2PasswordHasher()
    pw_hash = await hasher.hash_password("LogisticsPass#2026")

    p_perumda, p_mc, p_coop = uuid4(), uuid4(), uuid4()
    mc_id, mill_a_id, mill_b_id, coop_id = uuid4(), uuid4(), uuid4(), uuid4()
    vehicle_id, driver_id = uuid4(), uuid4()
    contract_id, small_contract_id = uuid4(), uuid4()
    farmer_a_id, farmer_b_id, farmer_c_id = uuid4(), uuid4(), uuid4()
    rcv_a_id, rcv_b_id, rcv_c_id, rcv_small_id = uuid4(), uuid4(), uuid4(), uuid4()

    async with sf() as session:
        async with session.begin():
            await session.execute(
                text(
                    "TRUNCATE TABLE audit_events, idempotency_records, auth_sessions, "
                    "user_access_scopes, user_role_grants, user_accounts, "
                    "delivery_status_events, delivery_order_lines, delivery_orders, "
                    "contract_approval_events, quota_reservations, contract_quota_periods, "
                    "trade_contracts, receipt_grading_items, receipt_weighing_revisions, "
                    "tbs_receipts, farms, cooperative_memberships, farmers, cooperatives, "
                    "mills, mill_companies, vehicles, drivers, parties RESTART IDENTITY CASCADE"
                )
            )
            await seed_rbac_catalog(session)
            await seed_baseline_system_rules(session)

            for pid, ptype, pname in (
                (p_perumda, "PERUMDA", "Perumda Tuah Sekata"),
                (p_mc, "MILL_COMPANY", "PT Sawit Indo"),
                (p_coop, "COOPERATIVE", "KUD Makmur Jaya"),
            ):
                session.add(
                    PartyModel(
                        id=pid,
                        party_type=ptype,
                        display_name=pname,
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
                    cooperative_code="KOP-B6-01",
                    cooperative_name="KUD Makmur Jaya",
                    address="Pelalawan",
                    contact_phone="08121111000",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            session.add(
                MillCompanyModel(
                    id=mc_id,
                    party_id=p_mc,
                    company_code="MC-B6-01",
                    company_name="PT Sawit Indo",
                    contact_phone="0761222333",
                    address="Pekanbaru",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()

            for mid, code, name in (
                (mill_a_id, "PKS-A", "PKS Pangkalan Kerinci"),
                (mill_b_id, "PKS-B", "PKS Langgam Jaya"),
            ):
                session.add(
                    MillModel(
                        id=mid,
                        mill_company_id=mc_id,
                        mill_code=code,
                        mill_name=name,
                        address="Pelalawan",
                        district="Pangkalan Kerinci",
                        regency="Pelalawan",
                        province="Riau",
                        latitude=Decimal("0.402100"),
                        longitude=Decimal("101.860400"),
                        contact_phone="0761000111",
                        partnership_status="ACTIVE",
                        is_public=True,
                        location_verified_at=now,
                        version=1,
                        created_at=now,
                        updated_at=now,
                    )
                )
            session.add(
                VehicleModel(
                    id=vehicle_id,
                    plate_number="BM 9042 TS",
                    vehicle_type="TRUCK",
                    nominal_capacity_kg=Decimal("12000.000"),
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            session.add(
                DriverModel(
                    id=driver_id,
                    full_name="Rahmat Hidayat",
                    contact_phone="0813444555",
                    driver_reference="SIM-B1-001",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )

            actors_meta = (
                (
                    "coop_b6",
                    RoleCode.COOPERATIVE_OPERATOR,
                    ScopeType.COOPERATIVE,
                    None,
                    coop_id,
                    None,
                ),
                ("ops_b6", RoleCode.PERUMDA_OPERATIONS, ScopeType.PERUMDA_GLOBAL, None, None, None),
                ("mill_op_a", RoleCode.MILL_OPERATOR, ScopeType.MILL, None, None, mill_a_id),
                ("mill_op_b", RoleCode.MILL_OPERATOR, ScopeType.MILL, None, None, mill_b_id),
                ("farmer_a", RoleCode.FARMER, ScopeType.FARMER, farmer_a_id, None, None),
            )

            # Seed farmers + farms + VALIDATED receipts FIRST so farmer_a_id FK exists on scopes!
            farmer_receipts = (
                (
                    farmer_a_id,
                    "FRM-A",
                    "Hendra Wijaya",
                    rcv_a_id,
                    "RCV-B6-001",
                    Decimal("3000.000"),
                ),
                (farmer_b_id, "FRM-B", "Siti Aminah", rcv_b_id, "RCV-B6-002", Decimal("2000.000")),
                (farmer_c_id, "FRM-C", "Budi Santoso", rcv_c_id, "RCV-B6-003", Decimal("5000.000")),
            )
            coop_op_uid = uuid4()
            for idx, (fid, fcode, fname, rid, rnum, net_kg) in enumerate(farmer_receipts):
                pf = uuid4()
                fm_id = uuid4()
                session.add(
                    PartyModel(
                        id=pf,
                        party_type="FARMER",
                        display_name=fname,
                        status="ACTIVE",
                        created_at=now,
                        updated_at=now,
                    )
                )
                await session.flush()
                session.add(
                    FarmerModel(
                        id=fid,
                        party_id=pf,
                        farmer_code=fcode,
                        full_name=fname,
                        contact_phone="08120000111",
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
                        cooperative_id=coop_id,
                        farmer_id=fid,
                        membership_number=f"M-{fcode}",
                        joined_at=now,
                        ended_at=None,
                        status="ACTIVE",
                    )
                )
                session.add(
                    FarmModel(
                        id=fm_id,
                        farmer_id=fid,
                        farm_code=f"KBN-{fcode}",
                        farm_name=f"Kebun {fname}",
                        area_hectares=Decimal("2.0000"),
                        planting_year=2020,
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
                if idx == 0:
                    session.add(
                        UserAccountModel(
                            id=coop_op_uid,
                            username="coop_b6",
                            email="coop_b6@agroniaga.local",
                            display_name="coop_b6",
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
                    TbsReceiptModel(
                        id=rid,
                        receipt_number=rnum,
                        farmer_id=fid,
                        farm_id=fm_id,
                        cooperative_id=coop_id,
                        harvest_date=now.date(),
                        received_at=now,
                        status="VALIDATED",
                        notes=None,
                        created_by=coop_op_uid,
                        created_at=now,
                        updated_at=now,
                        version=2,
                    )
                )
                await session.flush()
                session.add(
                    ReceiptWeighingRevisionModel(
                        id=uuid4(),
                        receipt_id=rid,
                        revision_number=1,
                        gross_weight_kg=net_kg + Decimal("1200.000"),
                        tare_weight_kg=Decimal("1200.000"),
                        net_weight_kg=net_kg,
                        weighed_at=now,
                        weighed_by=coop_op_uid,
                        is_current=True,
                        correction_reason=None,
                        created_at=now,
                    )
                )

            # Extra receipt 4000 kg owned by farmer_a to test insufficient quota rollback.
            extra_farm = (
                await session.execute(
                    text("SELECT id FROM farms WHERE farmer_id = :fid LIMIT 1"),
                    {"fid": farmer_a_id},
                )
            ).scalar_one()
            session.add(
                TbsReceiptModel(
                    id=rcv_small_id,
                    receipt_number="RCV-B6-SMALL-004",
                    farmer_id=farmer_a_id,
                    farm_id=extra_farm,
                    cooperative_id=coop_id,
                    harvest_date=now.date(),
                    received_at=now,
                    status="VALIDATED",
                    notes=None,
                    created_by=coop_op_uid,
                    created_at=now,
                    updated_at=now,
                    version=2,
                )
            )
            await session.flush()
            session.add(
                ReceiptWeighingRevisionModel(
                    id=uuid4(),
                    receipt_id=rcv_small_id,
                    revision_number=1,
                    gross_weight_kg=Decimal("5200.000"),
                    tare_weight_kg=Decimal("1200.000"),
                    net_weight_kg=Decimal("4000.000"),
                    weighed_at=now,
                    weighed_by=coop_op_uid,
                    is_current=True,
                    correction_reason=None,
                    created_at=now,
                )
            )

            for uname, role, stype, fid, cid, mid in actors_meta:
                uid = coop_op_uid if uname == "coop_b6" else uuid4()
                if uname != "coop_b6":
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
                        mill_id=mid,
                        granted_by=None,
                        created_at=now,
                        revoked_at=None,
                    )
                )

            # Seed 2 ACTIVE contracts: 1 large (50,000 kg) on Mill A, 1 tight (1,000 kg) on Mill A.
            start_d = now.date() - timedelta(days=5)
            end_d = now.date() + timedelta(days=30)
            for c_id, c_num, q_limit in (
                (contract_id, "KTR-B6-MAIN", Decimal("50000.000")),
                (small_contract_id, "KTR-B6-TIGHT", Decimal("1000.000")),
            ):
                session.add(
                    TradeContractModel(
                        id=c_id,
                        contract_number=c_num,
                        mill_id=mill_a_id,
                        start_date=start_d,
                        end_date=end_d,
                        price_rule_type="FIXED",
                        agreed_price_per_kg=Decimal("2850.00"),
                        grading_policy_reference="BSD-DEC-006",
                        business_model_code="PRINCIPAL",
                        perumda_role="SELLER",
                        seller_party_id=p_perumda,
                        buyer_party_id=p_mc,
                        agent_party_id=None,
                        represented_party_id=None,
                        business_model_rule_version=RULE_BUSINESS_MODEL_POLICY_ID,
                        payment_terms="14 hari",
                        status="ACTIVE",
                        created_by=coop_op_uid,
                        approved_by=coop_op_uid,
                        approved_at=now,
                        version=2,
                        created_at=now,
                        updated_at=now,
                    )
                )
                await session.flush()
                session.add(
                    ContractQuotaPeriodModel(
                        id=uuid4(),
                        contract_id=c_id,
                        period_start=start_d,
                        period_end=end_d,
                        quota_limit_kg=q_limit,
                        status="ACTIVE",
                        created_at=now,
                        updated_at=now,
                    )
                )

    await redis_client.flushdb()
    app = create_app(settings=cfg, db_dsn_override=test_db_url, redis_url_override=test_redis_url)
    async with app.router.lifespan_context(app):
        yield {
            "app": app,
            "sf": sf,
            "mill_a_id": str(mill_a_id),
            "mill_b_id": str(mill_b_id),
            "vehicle_id": str(vehicle_id),
            "driver_id": str(driver_id),
            "contract_id": str(contract_id),
            "small_contract_id": str(small_contract_id),
            "rcv_a_id": str(rcv_a_id),
            "rcv_b_id": str(rcv_b_id),
            "rcv_c_id": str(rcv_c_id),
            "rcv_small_id": str(rcv_small_id),
            "farmer_a_id": str(farmer_a_id),
        }

    await redis_client.aclose()
    await dispose_database(engine)


async def test_b6_multi_farmer_edo_atomic_issue_idempotency_privacy_and_qr(b6_env: dict) -> None:
    transport = httpx.ASGITransport(app=b6_env["app"])
    coop, csrf_coop = await _login(transport, username="coop_b6", password="LogisticsPass#2026")
    ops, csrf_ops = await _login(transport, username="ops_b6", password="LogisticsPass#2026")
    mill_a, csrf_ma = await _login(transport, username="mill_op_a", password="LogisticsPass#2026")
    mill_b, csrf_mb = await _login(transport, username="mill_op_b", password="LogisticsPass#2026")
    farmer_a, _ = await _login(transport, username="farmer_a", password="LogisticsPass#2026")

    try:
        # 1. Create consolidated e-DO across 3 farmers (3000 + 2000 + 5000 = 10000.000 kg).
        draft_resp = await coop.post(
            "/api/v1/delivery-orders",
            json={
                "mill_id": b6_env["mill_a_id"],
                "contract_id": b6_env["contract_id"],
                "vehicle_id": b6_env["vehicle_id"],
                "driver_id": b6_env["driver_id"],
                "receipt_ids": [b6_env["rcv_a_id"], b6_env["rcv_b_id"], b6_env["rcv_c_id"]],
            },
            headers={"X-CSRF-Token": csrf_coop},
        )
        assert draft_resp.status_code == 201
        do_data = draft_resp.json()["data"]
        do_id = do_data["id"]
        assert do_data["total_origin_weight_kg"] == "10000.000"
        assert do_data["status"] == "DRAFT"
        assert do_data["gps_tracking_supported"] is False
        assert len(do_data["lines"]) == 3

        # 2. Attempt double-allocation of rcv_a_id in another draft -> 409 LOG_DELIVERY_ALREADY_ASSIGNED.
        dup_draft = await coop.post(
            "/api/v1/delivery-orders",
            json={
                "mill_id": b6_env["mill_a_id"],
                "contract_id": b6_env["contract_id"],
                "vehicle_id": b6_env["vehicle_id"],
                "driver_id": b6_env["driver_id"],
                "receipt_ids": [b6_env["rcv_a_id"]],
            },
            headers={"X-CSRF-Token": csrf_coop},
        )
        assert dup_draft.status_code == 409
        assert dup_draft.json()["error"]["code"] == "LOG_DELIVERY_ALREADY_ASSIGNED"
        assert b6_env["rcv_a_id"] in dup_draft.json()["error"]["details"]["conflicting_receipt_ids"]

        # 3. Concurrent issueDeliveryOrder with same Idempotency-Key emits 1 atomic READY + QR!
        issue_payload = {"version": 1, "confirm_lock_allocations": True}
        ir1, ir2 = await asyncio.gather(
            coop.post(
                f"/api/v1/delivery-orders/{do_id}/issue",
                json=issue_payload,
                headers={"X-CSRF-Token": csrf_coop, "Idempotency-Key": "issue-edo-race-001"},
            ),
            coop.post(
                f"/api/v1/delivery-orders/{do_id}/issue",
                json=issue_payload,
                headers={"X-CSRF-Token": csrf_coop, "Idempotency-Key": "issue-edo-race-001"},
            ),
        )
        assert sorted([ir1.status_code, ir2.status_code]) in ([200, 200], [200, 409])

        replay = await coop.post(
            f"/api/v1/delivery-orders/{do_id}/issue",
            json=issue_payload,
            headers={"X-CSRF-Token": csrf_coop, "Idempotency-Key": "issue-edo-race-001"},
        )
        assert replay.status_code == 200
        assert replay.json()["meta"]["idempotency_replayed"] is True
        issued_do = replay.json()["data"]
        assert issued_do["status"] == "READY"
        qr_token = issued_do["qr_verification_token"]
        assert qr_token is not None

        # Verify contract quota now has 10000.000 reserved.
        quota_after = (await ops.get(f"/api/v1/contracts/{b6_env['contract_id']}/quota")).json()[
            "data"
        ][0]
        assert quota_after["active_reserved_kg"] == "10000.000"
        assert quota_after["available_quota_kg"] == "40000.000"

        # 4. FARMER privacy: Farmer A ONLY sees own line, not Farmers B/C.
        f_detail = await farmer_a.get(f"/api/v1/delivery-orders/{do_id}")
        assert f_detail.status_code == 200
        assert len(f_detail.json()["data"]["lines"]) == 1
        assert f_detail.json()["data"]["lines"][0]["farmer_id"] == b6_env["farmer_a_id"]

        # 5. Unauthorized COMPLETED transition by Coop blocked; READY -> IN_TRANSIT succeeds.
        bad_trans = await coop.post(
            f"/api/v1/delivery-orders/{do_id}/status",
            json={"target_status": "COMPLETED", "version": issued_do["version"]},
            headers={"X-CSRF-Token": csrf_coop},
        )
        assert bad_trans.status_code == 409

        transit = await coop.post(
            f"/api/v1/delivery-orders/{do_id}/status",
            json={"target_status": "IN_TRANSIT", "version": issued_do["version"]},
            headers={"X-CSRF-Token": csrf_coop},
        )
        assert transit.status_code == 200
        assert transit.json()["data"]["status"] == "IN_TRANSIT"

        # 6. Mill B operator scanning Mill A's QR gets 403 MILL_EDO_MILL_MISMATCH!
        wrong_mill_qr = await mill_b.post(
            "/api/v1/delivery-orders/verify-qr",
            json={"qr_token_or_edo_number": qr_token, "observed_plate_number": "BM 9042 TS"},
            headers={"X-CSRF-Token": csrf_mb},
        )
        assert wrong_mill_qr.status_code == 403
        assert wrong_mill_qr.json()["error"]["code"] == "MILL_EDO_MILL_MISMATCH"

        # Mill A scans QR -> IN_TRANSIT -> ARRIVED!
        arrived = await mill_a.post(
            "/api/v1/delivery-orders/verify-qr",
            json={"qr_token_or_edo_number": qr_token, "observed_plate_number": "BM 9042 TS"},
            headers={"X-CSRF-Token": csrf_ma},
        )
        assert arrived.status_code == 200
        assert arrived.json()["data"]["status"] == "ARRIVED"

        # Cannot cancel ARRIVED e-DO -> 409 LOG_CANCELLATION_FORBIDDEN!
        cancel_arrived = await ops.post(
            f"/api/v1/delivery-orders/{do_id}/cancel",
            json={
                "reason": "Coba batalkan pasca tiba",
                "version": arrived.json()["data"]["version"],
            },
            headers={"X-CSRF-Token": csrf_ops},
        )
        assert cancel_arrived.status_code == 409
        assert cancel_arrived.json()["error"]["code"] == "LOG_CANCELLATION_FORBIDDEN"
    finally:
        await coop.aclose()
        await ops.aclose()
        await mill_a.aclose()
        await mill_b.aclose()
        await farmer_a.aclose()


async def test_b6_insufficient_quota_rollback_and_pre_departure_cancellation_release(
    b6_env: dict,
) -> None:
    transport = httpx.ASGITransport(app=b6_env["app"])
    coop, csrf_coop = await _login(transport, username="coop_b6", password="LogisticsPass#2026")
    ops, csrf_ops = await _login(transport, username="ops_b6", password="LogisticsPass#2026")

    try:
        # 1. Create draft against tight 1,000 kg contract with 4,000 kg receipt -> DRAFT ok.
        d_tight = await coop.post(
            "/api/v1/delivery-orders",
            json={
                "mill_id": b6_env["mill_a_id"],
                "contract_id": b6_env["small_contract_id"],
                "vehicle_id": b6_env["vehicle_id"],
                "driver_id": b6_env["driver_id"],
                "receipt_ids": [b6_env["rcv_small_id"]],
            },
            headers={"X-CSRF-Token": csrf_coop},
        )
        assert d_tight.status_code == 201
        tight_id = d_tight.json()["data"]["id"]

        # Issuing fails 409 CONTRACT_QUOTA_EXCEEDED and rolls back cleanly.
        fail_issue = await coop.post(
            f"/api/v1/delivery-orders/{tight_id}/issue",
            json={"version": 1, "confirm_lock_allocations": True},
            headers={"X-CSRF-Token": csrf_coop, "Idempotency-Key": "issue-tight-exceed-01"},
        )
        assert fail_issue.status_code == 409
        assert fail_issue.json()["error"]["code"] == "CONTRACT_QUOTA_EXCEEDED"

        # Cancel draft -> releases line allocation so receipt can be used on main contract.
        cancel_draft = await coop.post(
            f"/api/v1/delivery-orders/{tight_id}/cancel",
            json={"reason": "Kontrak terlalu kecil, pindahkan muatan", "version": 1},
            headers={"X-CSRF-Token": csrf_coop},
        )
        assert cancel_draft.status_code == 200
        assert cancel_draft.json()["data"]["lines"][0]["allocation_status"] == "RELEASED"

        # Re-draft & issue on main contract -> succeeds! Cancel while READY releases receipt & quota!
        d_main = await coop.post(
            "/api/v1/delivery-orders",
            json={
                "mill_id": b6_env["mill_a_id"],
                "contract_id": b6_env["contract_id"],
                "vehicle_id": b6_env["vehicle_id"],
                "driver_id": b6_env["driver_id"],
                "receipt_ids": [b6_env["rcv_small_id"]],
            },
            headers={"X-CSRF-Token": csrf_coop},
        )
        assert d_main.status_code == 201
        main_do_id = d_main.json()["data"]["id"]

        issued = await coop.post(
            f"/api/v1/delivery-orders/{main_do_id}/issue",
            json={"version": 1, "confirm_lock_allocations": True},
            headers={"X-CSRF-Token": csrf_coop, "Idempotency-Key": "issue-main-reuse-01"},
        )
        assert issued.status_code == 200

        cancel_ready = await coop.post(
            f"/api/v1/delivery-orders/{main_do_id}/cancel",
            json={"reason": "Kendaraan bermasalah sebelum berangkat", "version": 2},
            headers={"X-CSRF-Token": csrf_coop},
        )
        assert cancel_ready.status_code == 200
        assert cancel_ready.json()["data"]["status"] == "CANCELLED"

        # Verify receipt returned to VALIDATED & quota reservation released back to 50000.000.
        r_chk = await ops.get(f"/api/v1/receipts/{b6_env['rcv_small_id']}")
        assert r_chk.json()["data"]["status"] == "VALIDATED"
        q_chk = (await ops.get(f"/api/v1/contracts/{b6_env['contract_id']}/quota")).json()["data"][
            0
        ]
        assert q_chk["active_reserved_kg"] == "0.000"
        assert q_chk["available_quota_kg"] == "50000.000"
    finally:
        await coop.aclose()
        await ops.aclose()
