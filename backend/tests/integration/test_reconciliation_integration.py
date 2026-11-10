"""PostgreSQL integration tests for Reconciliation SM-07, Disputes SM-08, SOD-03 & Allocations (B8)."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import httpx
import pytest
from app.core.config import Settings
from app.core.database import build_async_engine, build_session_factory, dispose_database
from app.core.system_rules import (
    RULE_BUSINESS_MODEL_POLICY_ID,
    RULE_FARMER_ALLOCATION_POLICY_ID,
    RULE_RECONCILIATION_TOLERANCE_ID,
    SystemRuleVersionModel,
    seed_baseline_system_rules,
)
from app.main import create_app
from app.modules.contracts.infrastructure.models import TradeContractModel
from app.modules.identity_access.domain.entities import RoleCode, ScopeType
from app.modules.identity_access.infrastructure.models import (
    UserAccessScopeModel,
    UserAccountModel,
    UserRoleGrantModel,
    deterministic_role_id,
    seed_rbac_catalog,
)
from app.modules.identity_access.infrastructure.security_adapters import Argon2PasswordHasher
from app.modules.logistics.infrastructure.models import (
    DeliveryOrderLineModel,
    DeliveryOrderModel,
)
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
from app.modules.mill_weighing.infrastructure.models import MillWeighingTicketModel
from app.modules.tbs_receiving.infrastructure.models import TbsReceiptModel
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
async def b8_env(test_db_url: str | None, test_redis_url: str | None) -> AsyncIterator[dict]:
    assert test_db_url and test_redis_url
    assert test_redis_url.endswith("/1")

    cfg = Settings(LOG_JSON=False)
    engine = build_async_engine(cfg, dsn_override=test_db_url)
    sf = build_session_factory(engine)
    redis_client = Redis.from_url(test_redis_url, decode_responses=True)

    now = datetime.now(UTC)
    hasher = Argon2PasswordHasher()
    pw_hash = await hasher.hash_password("RecPass#2026")

    p_perumda, p_mc, p_coop = uuid4(), uuid4(), uuid4()
    mc_id, mill_id, coop_id, veh_id, drv_id, contract_id = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    do_matched_id, do_dispute_id, do_surplus_id, do_unverified_id = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    tkt_dispute_id = uuid4()

    async with sf() as session:
        async with session.begin():
            await session.execute(
                text(
                    "TRUNCATE TABLE audit_events, idempotency_records, auth_sessions, "
                    "user_access_scopes, user_role_grants, user_accounts, "
                    "farmer_settlement_allocations, dispute_reviews, reconciliation_cases, "
                    "mill_grading_items, mill_weighing_tickets, file_assets, "
                    "delivery_status_events, delivery_order_lines, delivery_orders, "
                    "contract_approval_events, quota_reservations, contract_quota_periods, "
                    "trade_contracts, receipt_grading_items, receipt_weighing_revisions, "
                    "tbs_receipts, farms, cooperative_memberships, farmers, cooperatives, "
                    "mills, mill_companies, vehicles, drivers, parties, system_rule_versions "
                    "RESTART IDENTITY CASCADE"
                )
            )
            await seed_rbac_catalog(session)
            await seed_baseline_system_rules(session)

            for pid, ptype, pname in (
                (p_perumda, "PERUMDA", "Perumda Tuah Sekata"),
                (p_mc, "MILL_COMPANY", "PT Sawit Makmur"),
                (p_coop, "COOPERATIVE", "KUD B8"),
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
                    cooperative_code="KOP-B8",
                    cooperative_name="KUD B8",
                    address="Pelalawan",
                    contact_phone="0812000",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            session.add(
                MillCompanyModel(
                    id=mc_id,
                    party_id=p_mc,
                    company_code="MC-B8",
                    company_name="PT Sawit Makmur",
                    contact_phone="0761000",
                    address="Pekanbaru",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()
            session.add(
                MillModel(
                    id=mill_id,
                    mill_company_id=mc_id,
                    mill_code="PKS-B8",
                    mill_name="PKS Pelalawan",
                    address="Pelalawan",
                    district="Kerinci",
                    regency="Pelalawan",
                    province="Riau",
                    latitude=Decimal("0.402100"),
                    longitude=Decimal("101.860400"),
                    contact_phone="0761002",
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
                    id=veh_id,
                    plate_number="BM 8888 REC",
                    vehicle_type="TRUCK",
                    nominal_capacity_kg=Decimal("12000.000"),
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            session.add(
                DriverModel(
                    id=drv_id,
                    full_name="Sopir B8",
                    contact_phone="0812999",
                    driver_reference="SIM-B8",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )

            actors = (
                ("ops_rec_1", RoleCode.PERUMDA_OPERATIONS, ScopeType.PERUMDA_GLOBAL, None),
                ("dir_rec_2", RoleCode.DIRECTOR, ScopeType.PERUMDA_GLOBAL, None),
                ("coop_b8", RoleCode.COOPERATIVE_OPERATOR, ScopeType.COOPERATIVE, coop_id),
                ("sys_admin_b8", RoleCode.SYSTEM_ADMIN, ScopeType.PERUMDA_GLOBAL, None),
            )
            ops_uid = uuid4()
            for uname, role, stype, cid in actors:
                uid = ops_uid if uname == "ops_rec_1" else uuid4()
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
                        farmer_id=None,
                        cooperative_id=cid,
                        mill_id=None,
                        granted_by=None,
                        created_at=now,
                        revoked_at=None,
                    )
                )

            session.add(
                TradeContractModel(
                    id=contract_id,
                    contract_number="KTR-B8-MAIN",
                    mill_id=mill_id,
                    start_date=now.date() - timedelta(days=5),
                    end_date=now.date() + timedelta(days=30),
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
                    created_by=ops_uid,
                    approved_by=ops_uid,
                    approved_at=now,
                    version=2,
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()

            # 3 multi-farmer receipts (3000, 2000, 5000 = 10000 kg) linked to do_matched_id.
            receipt_ids: list[tuple[UUID, Decimal]] = []
            for idx, (fcode, fname, wt) in enumerate(
                (
                    ("FB8-1", "Hendra Wijaya", Decimal("3000.000")),
                    ("FB8-2", "Siti Aminah", Decimal("2000.000")),
                    ("FB8-3", "Budi Santoso", Decimal("5000.000")),
                ),
                start=1,
            ):
                pf, fid, fmid, rid = uuid4(), uuid4(), uuid4(), uuid4()
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
                        contact_phone="0812111",
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
                        membership_number=f"M-{idx}",
                        joined_at=now,
                        ended_at=None,
                        status="ACTIVE",
                    )
                )
                session.add(
                    FarmModel(
                        id=fmid,
                        farmer_id=fid,
                        farm_code=f"FM-{idx}",
                        farm_name=f"Kebun {idx}",
                        area_hectares=Decimal("2.0000"),
                        planting_year=2020,
                        stdb_number=None,
                        village="Makmur",
                        district="Kerinci",
                        latitude=Decimal("0.402100"),
                        longitude=Decimal("101.860400"),
                        verification_status="VERIFIED",
                        version=1,
                        created_at=now,
                        updated_at=now,
                    )
                )
                await session.flush()
                session.add(
                    TbsReceiptModel(
                        id=rid,
                        receipt_number=f"RCV-B8-{idx}",
                        farmer_id=fid,
                        farm_id=fmid,
                        cooperative_id=coop_id,
                        harvest_date=now.date(),
                        received_at=now,
                        status="SHIPPED",
                        notes=None,
                        created_by=ops_uid,
                        created_at=now,
                        updated_at=now,
                        version=3,
                    )
                )
                receipt_ids.append((rid, wt))

            await session.flush()

            # 4 Delivery Orders + Tickets: Matched (9900), Dispute (9600), Surplus (10150), Unverified (SUBMITTED).
            do_specs = (
                (
                    do_matched_id,
                    "EDO-B8-MATCH",
                    Decimal("10000.000"),
                    Decimal("9900.000"),
                    "VERIFIED",
                    uuid4(),
                    "WB-B8-01",
                ),
                (
                    do_dispute_id,
                    "EDO-B8-DISP",
                    Decimal("10000.000"),
                    Decimal("9600.000"),
                    "VERIFIED",
                    tkt_dispute_id,
                    "WB-B8-02",
                ),
                (
                    do_surplus_id,
                    "EDO-B8-SURP",
                    Decimal("10000.000"),
                    Decimal("10150.000"),
                    "VERIFIED",
                    uuid4(),
                    "WB-B8-03",
                ),
                (
                    do_unverified_id,
                    "EDO-B8-UNV",
                    Decimal("10000.000"),
                    Decimal("9900.000"),
                    "SUBMITTED",
                    uuid4(),
                    "WB-B8-04",
                ),
            )
            for do_id, dnum, orig_wt, mill_wt, tkt_st, tkt_id, tnum in do_specs:
                session.add(
                    DeliveryOrderModel(
                        id=do_id,
                        delivery_order_number=dnum,
                        cooperative_id=coop_id,
                        mill_id=mill_id,
                        contract_id=contract_id,
                        vehicle_id=veh_id,
                        driver_id=drv_id,
                        total_origin_weight_kg=orig_wt,
                        status="RECEIVED" if tkt_st == "VERIFIED" else "ARRIVED",
                        issued_at=now,
                        departed_at=now,
                        arrived_at=now,
                        completed_at=None,
                        qr_verification_token=f"QR-{dnum}",
                        qr_reference_hash=f"HASH-{dnum}",
                        created_by=ops_uid,
                        version=4,
                        created_at=now,
                        updated_at=now,
                    )
                )
                await session.flush()
                if do_id == do_matched_id:
                    for rid, wt in receipt_ids:
                        session.add(
                            DeliveryOrderLineModel(
                                id=uuid4(),
                                delivery_order_id=do_id,
                                receipt_id=rid,
                                origin_weight_snapshot_kg=wt,
                                allocation_status="ACTIVE",
                                created_at=now,
                                released_at=None,
                            )
                        )
                session.add(
                    MillWeighingTicketModel(
                        id=tkt_id,
                        delivery_order_id=do_id,
                        mill_id=mill_id,
                        ticket_number=tnum,
                        revision_number=1,
                        previous_ticket_id=None,
                        gross_weight_kg=mill_wt + Decimal("7440.000"),
                        tare_weight_kg=Decimal("7440.000"),
                        net_weight_kg=mill_wt,
                        weighed_at=now,
                        verified_at=now if tkt_st == "VERIFIED" else None,
                        verified_by=ops_uid if tkt_st == "VERIFIED" else None,
                        is_current=True,
                        status=tkt_st,
                        proof_file_id=None,
                        correction_reason=None,
                        created_by=ops_uid,
                        created_at=now,
                    )
                )

    await redis_client.flushdb()
    app = create_app(settings=cfg, db_dsn_override=test_db_url, redis_url_override=test_redis_url)
    async with app.router.lifespan_context(app):
        yield {
            "app": app,
            "sf": sf,
            "mill_id": str(mill_id),
            "do_matched_id": str(do_matched_id),
            "do_dispute_id": str(do_dispute_id),
            "do_surplus_id": str(do_surplus_id),
            "do_unverified_id": str(do_unverified_id),
            "tkt_dispute_id": str(tkt_dispute_id),
        }

    await redis_client.aclose()
    await dispose_database(engine)


async def test_b8_reconciliation_tolerance_snapshot_negative_diff_and_concurrency(
    b8_env: dict,
) -> None:
    transport = httpx.ASGITransport(app=b8_env["app"])
    ops, csrf_ops = await _login(transport, username="ops_rec_1", password="RecPass#2026")
    director, _ = await _login(transport, username="dir_rec_2", password="RecPass#2026")
    coop, _ = await _login(transport, username="coop_b8", password="RecPass#2026")

    try:
        # 1. Unequal weight basis -> 422 REC_INVALID_WEIGHT_BASIS.
        bad_basis = await ops.post(
            "/api/v1/reconciliations",
            json={
                "delivery_order_id": b8_env["do_matched_id"],
                "weight_basis": "NET_WEIGHT_AFTER_GRADING",
            },
            headers={"X-CSRF-Token": csrf_ops, "Idempotency-Key": "rec-bad-basis"},
        )
        assert bad_basis.status_code == 422
        assert bad_basis.json()["error"]["code"] == "REC_INVALID_WEIGHT_BASIS"

        # 2. Unverified ticket -> 409 REC_NOT_READY.
        not_ready = await ops.post(
            "/api/v1/reconciliations",
            json={"delivery_order_id": b8_env["do_unverified_id"]},
            headers={"X-CSRF-Token": csrf_ops, "Idempotency-Key": "rec-not-ready"},
        )
        assert not_ready.status_code == 409
        assert not_ready.json()["error"]["code"] == "REC_NOT_READY"

        # 3. Concurrent reconciliation with distinct Idempotency-Keys -> strictly 1 created!
        r1, r2 = await asyncio.gather(
            ops.post(
                "/api/v1/reconciliations",
                json={"delivery_order_id": b8_env["do_matched_id"]},
                headers={"X-CSRF-Token": csrf_ops, "Idempotency-Key": "rec-conc-a"},
            ),
            ops.post(
                "/api/v1/reconciliations",
                json={"delivery_order_id": b8_env["do_matched_id"]},
                headers={"X-CSRF-Token": csrf_ops, "Idempotency-Key": "rec-conc-b"},
            ),
        )
        assert sorted([r1.status_code, r2.status_code]) == [201, 409]
        matched_case = (r1 if r1.status_code == 201 else r2).json()["data"]
        assert matched_case["status"] == "MATCHED"
        assert matched_case["difference_weight_kg"] == "100.000"
        assert matched_case["difference_percent"] == "1.0000"
        assert matched_case["tolerance_percent"] == "1.5000"
        assert matched_case["is_negative_difference"] is False

        # 4. Negative difference (mill > origin) -> auto DISPUTE_HOLD (BR-REC-009)!
        surplus = await ops.post(
            "/api/v1/reconciliations",
            json={"delivery_order_id": b8_env["do_surplus_id"]},
            headers={"X-CSRF-Token": csrf_ops, "Idempotency-Key": "rec-surplus-01"},
        )
        assert surplus.status_code == 201
        sd = surplus.json()["data"]
        assert sd["status"] == "DISPUTE_HOLD"
        assert sd["difference_weight_kg"] == "-150.000"
        assert sd["is_negative_difference"] is True

        # 5. Bump tolerance version 2 to 0.5000%; historical matched_case still retains 1.5000%!
        async with b8_env["sf"]() as session:
            async with session.begin():
                session.add(
                    SystemRuleVersionModel(
                        id=uuid4(),
                        rule_code="RECONCILIATION_TOLERANCE",
                        version_number=2,
                        effective_from=datetime.now(UTC),
                        effective_until=None,
                        rule_config={"tolerance_percent": "0.5000"},
                        approval_status="SIMULATION_ONLY",
                        approved_by=None,
                        created_at=datetime.now(UTC),
                    )
                )
        hist = (await director.get(f"/api/v1/reconciliations/{matched_case['id']}")).json()["data"]
        assert hist["tolerance_percent"] == "1.5000"
        assert hist["rule_version_id"] == str(RULE_RECONCILIATION_TOLERANCE_ID)

        # 6. Farmer proportional allocations simulation + block FINAL before SOP.
        block_final = await ops.post(
            f"/api/v1/reconciliations/{matched_case['id']}/allocations",
            json={
                "mode": "FINAL",
                "allocation_policy_version_id": str(RULE_FARMER_ALLOCATION_POLICY_ID),
            },
            headers={"X-CSRF-Token": csrf_ops},
        )
        assert block_final.status_code == 409
        assert block_final.json()["error"]["code"] == "REC_ALLOCATION_POLICY_UNCONFIRMED"

        sim_alloc = await ops.post(
            f"/api/v1/reconciliations/{matched_case['id']}/allocations",
            json={
                "mode": "SIMULATION",
                "allocation_policy_version_id": str(RULE_FARMER_ALLOCATION_POLICY_ID),
            },
            headers={"X-CSRF-Token": csrf_ops},
        )
        assert sim_alloc.status_code == 200
        alloc_rows = sim_alloc.json()["data"]
        assert [a["agreed_weight_kg"] for a in alloc_rows] == ["2970.000", "1980.000", "4950.000"]
        assert all(a["status"] == "SIMULATED" for a in alloc_rows)
        assert (await coop.get(f"/api/v1/reconciliations/{matched_case['id']}")).status_code == 200
    finally:
        await ops.aclose()
        await director.aclose()
        await coop.aclose()


async def test_b8_dispute_sod03_permissions_and_revision_history(b8_env: dict) -> None:
    transport = httpx.ASGITransport(app=b8_env["app"])
    ops, csrf_ops = await _login(transport, username="ops_rec_1", password="RecPass#2026")
    director, csrf_dir = await _login(transport, username="dir_rec_2", password="RecPass#2026")
    coop, csrf_coop = await _login(transport, username="coop_b8", password="RecPass#2026")
    sys_admin, csrf_adm = await _login(transport, username="sys_admin_b8", password="RecPass#2026")

    try:
        disp_resp = await ops.post(
            "/api/v1/reconciliations",
            json={"delivery_order_id": b8_env["do_dispute_id"]},
            headers={"X-CSRF-Token": csrf_ops, "Idempotency-Key": "rec-dispute-01"},
        )
        assert disp_resp.status_code == 201
        disp_case = disp_resp.json()["data"]
        disp_id = disp_case["id"]
        assert disp_case["status"] == "DISPUTE_HOLD"

        # Blocked allocations while DISPUTE_HOLD -> 409 REC_WEIGHT_DISPUTE.
        blocked_alloc = await ops.post(
            f"/api/v1/reconciliations/{disp_id}/allocations",
            json={
                "mode": "SIMULATION",
                "allocation_policy_version_id": str(RULE_FARMER_ALLOCATION_POLICY_ID),
            },
            headers={"X-CSRF-Token": csrf_ops},
        )
        assert blocked_alloc.status_code == 409
        assert blocked_alloc.json()["error"]["code"] == "REC_WEIGHT_DISPUTE"

        # Coop unauthorized to review dispute -> 403 AUTH_ACCESS_DENIED.
        assert (
            await coop.post(
                f"/api/v1/reconciliations/{disp_id}/review",
                json={"decision": "HOLD_FOR_AUDIT", "reason": "Coba akses review"},
                headers={"X-CSRF-Token": csrf_coop},
            )
        ).status_code == 403

        # Submit review by ops_rec_1 -> UNDER_REVIEW.
        rev_resp = await ops.post(
            f"/api/v1/reconciliations/{disp_id}/review",
            json={
                "decision": "HOLD_FOR_AUDIT",
                "reason": "Susut 4.00% melebihi batas simulasi 1.50%, verifikasi tiket ramp.",
                "proposed_settlement_weight_kg": "9750.000",
            },
            headers={"X-CSRF-Token": csrf_ops},
        )
        assert rev_resp.status_code == 200
        assert rev_resp.json()["data"]["status"] == "UNDER_REVIEW"

        # Same reviewer attempting resolve -> 403 AUTH_CONFLICT_OF_DUTIES (SOD-03)!
        sod_fail = await ops.post(
            f"/api/v1/reconciliations/{disp_id}/resolve",
            json={
                "decision": "AGREED_SETTLEMENT_WEIGHT",
                "final_outcome": "RESOLVED",
                "agreed_settlement_weight_kg": "9750.000",
                "reason": "Coba sahkan sendiri keputusan review",
            },
            headers={"X-CSRF-Token": csrf_ops},
        )
        assert sod_fail.status_code == 403
        assert sod_fail.json()["error"]["code"] == "AUTH_CONFLICT_OF_DUTIES"

        # SYSTEM_ADMIN attempting resolve -> 403 AUTH_OPERATION_FORBIDDEN (BR-SYS-002).
        adm_fail = await sys_admin.post(
            f"/api/v1/reconciliations/{disp_id}/resolve",
            json={
                "decision": "AGREED_SETTLEMENT_WEIGHT",
                "final_outcome": "RESOLVED",
                "agreed_settlement_weight_kg": "9750.000",
                "reason": "Admin coba otorisasi",
            },
            headers={"X-CSRF-Token": csrf_adm},
        )
        assert adm_fail.status_code == 403
        assert adm_fail.json()["error"]["code"] == "AUTH_OPERATION_FORBIDDEN"

        # Director (Checker != Reviewer) resolves -> UNDER_REVIEW -> RESOLVED.
        res_ok = await director.post(
            f"/api/v1/reconciliations/{disp_id}/resolve",
            json={
                "decision": "AGREED_SETTLEMENT_WEIGHT",
                "final_outcome": "RESOLVED",
                "agreed_settlement_weight_kg": "9750.000",
                "reason": "Disetujui berdasar berita acara pemeriksaan gabungan Perumda dan PKS.",
            },
            headers={"X-CSRF-Token": csrf_dir},
        )
        assert res_ok.status_code == 200
        assert res_ok.json()["data"]["status"] == "RESOLVED"
        assert res_ok.json()["data"]["resolved_at"] is not None

        # Simulate revised verified ticket v2 on do_dispute_id -> revision_number=2 keeps rev 1 history!
        tkt_v2_id = uuid4()
        async with b8_env["sf"]() as session:
            async with session.begin():
                now = datetime.now(UTC)
                await session.execute(
                    text("UPDATE mill_weighing_tickets SET is_current = false WHERE id = :tid"),
                    {"tid": UUID(b8_env["tkt_dispute_id"])},
                )
                ops_uid = (
                    await session.execute(
                        text("SELECT id FROM user_accounts WHERE username = 'ops_rec_1'")
                    )
                ).scalar_one()
                session.add(
                    MillWeighingTicketModel(
                        id=tkt_v2_id,
                        delivery_order_id=UUID(b8_env["do_dispute_id"]),
                        mill_id=UUID(b8_env["mill_id"]),
                        ticket_number="WB-B8-02",
                        revision_number=2,
                        previous_ticket_id=UUID(b8_env["tkt_dispute_id"]),
                        gross_weight_kg=Decimal("17340.000"),
                        tare_weight_kg=Decimal("7440.000"),
                        net_weight_kg=Decimal("9900.000"),
                        weighed_at=now,
                        verified_at=now,
                        verified_by=ops_uid,
                        is_current=True,
                        status="VERIFIED",
                        proof_file_id=None,
                        correction_reason="Koreksi slip timbangan",
                        created_by=ops_uid,
                        created_at=now,
                    )
                )

        re_rec = await ops.post(
            "/api/v1/reconciliations",
            json={"delivery_order_id": b8_env["do_dispute_id"]},
            headers={"X-CSRF-Token": csrf_ops, "Idempotency-Key": "rec-rev-2"},
        )
        assert re_rec.status_code == 201
        r2_data = re_rec.json()["data"]
        assert r2_data["revision_number"] == 2
        assert r2_data["status"] == "MATCHED"
        old_v1 = (await ops.get(f"/api/v1/reconciliations/{disp_id}")).json()["data"]
        assert old_v1["is_current"] is False
    finally:
        await ops.aclose()
        await director.aclose()
        await coop.aclose()
        await sys_admin.aclose()
