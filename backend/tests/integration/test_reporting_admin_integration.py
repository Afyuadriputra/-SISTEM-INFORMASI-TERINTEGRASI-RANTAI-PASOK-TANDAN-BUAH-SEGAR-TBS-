"""PostgreSQL + Redis integration tests for Reporting & Admin Governance/Observability (B10)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import httpx
import pytest
from app.core.audit import AuditRecordInput, append_audit_event
from app.core.config import Settings
from app.core.database import build_async_engine, build_session_factory, dispose_database
from app.core.system_rules import (
    RULE_BUSINESS_MODEL_POLICY_ID,
    RULE_RECONCILIATION_TOLERANCE_ID,
    seed_baseline_system_rules,
)
from app.main import create_app
from app.modules.contracts.infrastructure.models import TradeContractModel
from app.modules.files.infrastructure.models import FileAssetModel
from app.modules.finance.infrastructure.models import (
    InvoiceLineModel,
    InvoiceModel,
    PaymentApprovalModel,
    PaymentRecordModel,
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
from app.modules.reconciliation.infrastructure.models import ReconciliationCaseModel
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
async def b10_env(test_db_url: str | None, test_redis_url: str | None) -> AsyncIterator[dict]:
    assert test_db_url and test_redis_url
    assert test_redis_url.endswith("/1")

    cfg = Settings(LOG_JSON=False)
    engine = build_async_engine(cfg, dsn_override=test_db_url)
    sf = build_session_factory(engine)
    redis_client = Redis.from_url(test_redis_url, decode_responses=True)
    await redis_client.flushdb()

    now = datetime.now(UTC)
    hasher = Argon2PasswordHasher()
    pw_hash = await hasher.hash_password("AdmPass#2026")

    p_perumda, p_mc, p_coop1, p_coop2, p_f1, p_f2 = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    mc_id, mill_id, coop1_id, coop2_id, f1_id, f2_id = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    farm1_id, farm2_id, veh_id, drv_id, ctr_id = (uuid4(), uuid4(), uuid4(), uuid4(), uuid4())
    proof_id = uuid4()
    case_active_id = uuid4()

    async with sf() as session:
        async with session.begin():
            await session.execute(
                text(
                    "TRUNCATE TABLE audit_events, idempotency_records, auth_sessions, "
                    "user_access_scopes, user_role_grants, user_accounts, "
                    "payment_records, payment_approvals, invoice_lines, invoices, "
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
                (p_mc, "MILL_COMPANY", "PT Sawit B10"),
                (p_coop1, "COOPERATIVE", "KUD Satu"),
                (p_coop2, "COOPERATIVE", "KUD Dua"),
                (p_f1, "FARMER", "Petani B10-1"),
                (p_f2, "FARMER", "Petani B10-2"),
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

            for cid, cpid, code, name in (
                (coop1_id, p_coop1, "KOP-B10-1", "KUD Satu"),
                (coop2_id, p_coop2, "KOP-B10-2", "KUD Dua"),
            ):
                session.add(
                    CooperativeModel(
                        id=cid,
                        party_id=cpid,
                        cooperative_code=code,
                        cooperative_name=name,
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
                    company_code="MC-B10",
                    company_name="PT Sawit B10",
                    contact_phone="0761000",
                    address="Pekanbaru",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()

            for fid, fpid, code, name, cid, fm_id in (
                (f1_id, p_f1, "FRM-B10-1", "Petani B10-1", coop1_id, farm1_id),
                (f2_id, p_f2, "FRM-B10-2", "Petani B10-2", coop2_id, farm2_id),
            ):
                session.add(
                    FarmerModel(
                        id=fid,
                        party_id=fpid,
                        farmer_code=code,
                        full_name=name,
                        identity_reference=f"140501{code[-1]}",
                        contact_phone="0813000",
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
                        cooperative_id=cid,
                        farmer_id=fid,
                        membership_number=f"MEM-{code}",
                        joined_at=now,
                        ended_at=None,
                        status="ACTIVE",
                    )
                )
                session.add(
                    FarmModel(
                        id=fm_id,
                        farmer_id=fid,
                        farm_code=f"KB-{code}",
                        farm_name=f"Kebun {code}",
                        area_hectares=Decimal("2.5000"),
                        planting_year=2019,
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

            session.add(
                MillModel(
                    id=mill_id,
                    mill_company_id=mc_id,
                    mill_code="PKS-B10",
                    mill_name="PKS Pelalawan Report",
                    address="Pelalawan",
                    district="Kerinci",
                    regency="Pelalawan",
                    province="Riau",
                    latitude=Decimal("0.402100"),
                    longitude=Decimal("101.860400"),
                    contact_phone="0761009",
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
                    plate_number="BM 1010 RPT",
                    vehicle_type="TRUCK",
                    nominal_capacity_kg=Decimal("15000.000"),
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            session.add(
                DriverModel(
                    id=drv_id,
                    full_name="Sopir B10",
                    contact_phone="0812888",
                    driver_reference="SIM-B10",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()

            fin_uid, dir_uid, sys_uid = uuid4(), uuid4(), uuid4()
            actors = (
                ("sys_b10", RoleCode.SYSTEM_ADMIN, ScopeType.PERUMDA_GLOBAL, None, None, None),
                ("dir_b10", RoleCode.DIRECTOR, ScopeType.PERUMDA_GLOBAL, None, None, None),
                ("fin_b10", RoleCode.PERUMDA_FINANCE, ScopeType.PERUMDA_GLOBAL, None, None, None),
                (
                    "ops_b10",
                    RoleCode.PERUMDA_OPERATIONS,
                    ScopeType.PERUMDA_GLOBAL,
                    None,
                    None,
                    None,
                ),
                ("pks_b10", RoleCode.MILL_OPERATOR, ScopeType.MILL, None, None, mill_id),
                (
                    "coop1_b10",
                    RoleCode.COOPERATIVE_OPERATOR,
                    ScopeType.COOPERATIVE,
                    None,
                    coop1_id,
                    None,
                ),
                ("farmer1_b10", RoleCode.FARMER, ScopeType.FARMER, f1_id, None, None),
                ("farmer2_b10", RoleCode.FARMER, ScopeType.FARMER, f2_id, None, None),
            )
            for uname, role, stype, f_s, c_s, m_s in actors:
                if uname == "fin_b10":
                    uid = fin_uid
                elif uname == "dir_b10":
                    uid = dir_uid
                elif uname == "sys_b10":
                    uid = sys_uid
                else:
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
                        farmer_id=f_s,
                        cooperative_id=c_s,
                        mill_id=m_s,
                        granted_by=None,
                        created_at=now,
                        revoked_at=None,
                    )
                )

            session.add(
                FileAssetModel(
                    id=proof_id,
                    storage_provider="LOCAL_DISK",
                    storage_key="test/b10-proof.pdf",
                    original_filename="b10-proof.pdf",
                    mime_type="application/pdf",
                    size_bytes=54321,
                    checksum=f"sha256:{proof_id.hex}",
                    classification="PAYMENT_PROOF",
                    uploaded_by=fin_uid,
                    created_at=now,
                )
            )
            session.add(
                TradeContractModel(
                    id=ctr_id,
                    contract_number="KTR-B10-001",
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
                    created_by=fin_uid,
                    approved_by=dir_uid,
                    approved_at=now,
                    version=2,
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()

            # Active chain for farmer1 / coop1 + 1 CANCELLED receipt & 1 CANCELLED DO excluded from sums
            rec_active, rec_cancelled = uuid4(), uuid4()
            for r_id, num, r_stat, weight in (
                (rec_active, "TBS-B10-001", "SHIPPED", Decimal("10000.000")),
                (rec_cancelled, "TBS-B10-CAN", "CANCELLED", Decimal("5000.000")),
            ):
                session.add(
                    TbsReceiptModel(
                        id=r_id,
                        receipt_number=num,
                        farmer_id=f1_id,
                        farm_id=farm1_id,
                        cooperative_id=coop1_id,
                        harvest_date=now.date(),
                        received_at=now,
                        status=r_stat,
                        notes=None,
                        created_by=fin_uid,
                        created_at=now,
                        updated_at=now,
                        version=1,
                    )
                )
                await session.flush()
                session.add(
                    ReceiptWeighingRevisionModel(
                        id=uuid4(),
                        receipt_id=r_id,
                        revision_number=1,
                        gross_weight_kg=weight + Decimal("1000.000"),
                        tare_weight_kg=Decimal("1000.000"),
                        net_weight_kg=weight,
                        weighed_at=now,
                        weighed_by=fin_uid,
                        is_current=True,
                        correction_reason=None,
                        created_at=now,
                    )
                )

            do_active, do_cancelled = uuid4(), uuid4()
            tkt_active = uuid4()
            for did, dnum, dstat in (
                (do_active, "EDO-B10-001", "RECEIVED"),
                (do_cancelled, "EDO-B10-CAN", "CANCELLED"),
            ):
                session.add(
                    DeliveryOrderModel(
                        id=did,
                        delivery_order_number=dnum,
                        cooperative_id=coop1_id,
                        mill_id=mill_id,
                        contract_id=ctr_id,
                        vehicle_id=veh_id,
                        driver_id=drv_id,
                        total_origin_weight_kg=Decimal("10000.000"),
                        status=dstat,
                        issued_at=now,
                        departed_at=now,
                        arrived_at=now,
                        completed_at=None,
                        qr_verification_token=f"QRT-{dnum}",
                        qr_reference_hash=f"{'b' * 62}{dnum[-2:]}",
                        created_by=fin_uid,
                        version=2,
                        created_at=now,
                        updated_at=now,
                    )
                )
            await session.flush()

            session.add(
                DeliveryOrderLineModel(
                    id=uuid4(),
                    delivery_order_id=do_active,
                    receipt_id=rec_active,
                    origin_weight_snapshot_kg=Decimal("10000.000"),
                    allocation_status="ACTIVE",
                    created_at=now,
                )
            )
            session.add(
                MillWeighingTicketModel(
                    id=tkt_active,
                    delivery_order_id=do_active,
                    mill_id=mill_id,
                    ticket_number="WB-B10-001",
                    revision_number=1,
                    previous_ticket_id=None,
                    gross_weight_kg=Decimal("14900.000"),
                    tare_weight_kg=Decimal("5000.000"),
                    net_weight_kg=Decimal("9900.000"),
                    weighed_at=now,
                    verified_at=now,
                    verified_by=fin_uid,
                    is_current=True,
                    status="VERIFIED",
                    proof_file_id=proof_id,
                    correction_reason=None,
                    created_by=fin_uid,
                    created_at=now,
                )
            )
            await session.flush()

            session.add(
                ReconciliationCaseModel(
                    id=case_active_id,
                    delivery_order_id=do_active,
                    mill_ticket_id=tkt_active,
                    revision_number=1,
                    origin_weight_kg=Decimal("10000.000"),
                    mill_weight_kg=Decimal("9900.000"),
                    difference_weight_kg=Decimal("100.000"),
                    difference_percent=Decimal("1.0000"),
                    tolerance_percent=Decimal("1.5000"),
                    rule_version_id=RULE_RECONCILIATION_TOLERANCE_ID,
                    tolerance_policy_classification="SIMULATION_ONLY",
                    is_negative_difference=False,
                    status="MATCHED",
                    is_current=True,
                    agreed_settlement_weight_kg=None,
                    calculated_at=now,
                    resolved_at=None,
                    created_by=fin_uid,
                    created_at=now,
                )
            )
            await session.flush()

            # Finance invoices: AR 28,215,000 (VERIFIED INBOUND), AP to Coop approved unpaid 26,000,000, AP to Farmer1 paid 5,000,000
            inv_ar, inv_ap_unpaid, inv_ap_farmer = uuid4(), uuid4(), uuid4()
            for iid, num, itype, cred, deb, amt in (
                (
                    inv_ar,
                    "INV-AR-B10",
                    "ACCOUNTS_RECEIVABLE",
                    p_perumda,
                    p_mc,
                    Decimal("28215000.00"),
                ),
                (
                    inv_ap_unpaid,
                    "INV-AP-COOP",
                    "ACCOUNTS_PAYABLE",
                    p_coop1,
                    p_perumda,
                    Decimal("20000000.00"),
                ),
                (
                    inv_ap_farmer,
                    "INV-AP-FRM",
                    "ACCOUNTS_PAYABLE",
                    p_f1,
                    p_perumda,
                    Decimal("5000000.00"),
                ),
            ):
                session.add(
                    InvoiceModel(
                        id=iid,
                        invoice_number=num,
                        invoice_type=itype,
                        creditor_party_id=cred,
                        debtor_party_id=deb,
                        business_model_code="PRINCIPAL",
                        business_model_rule_version_id=RULE_BUSINESS_MODEL_POLICY_ID,
                        reconciliation_case_id=case_active_id
                        if itype == "ACCOUNTS_RECEIVABLE"
                        else None,
                        invoice_date=now.date(),
                        due_date=now.date() + timedelta(days=7),
                        gross_amount=amt,
                        deduction_amount=Decimal("0.00"),
                        total_amount=amt,
                        status="ISSUED",
                        policy_classification="SIMULATION_ONLY",
                        issued_at=now,
                        created_by=fin_uid,
                        verified_by=dir_uid,
                        verified_at=now,
                        verification_reason=None,
                        version=2,
                        created_at=now,
                        updated_at=now,
                    )
                )
            await session.flush()

            for iid, amt in (
                (inv_ar, Decimal("28215000.00")),
                (inv_ap_unpaid, Decimal("20000000.00")),
                (inv_ap_farmer, Decimal("5000000.00")),
            ):
                session.add(
                    InvoiceLineModel(
                        id=uuid4(),
                        invoice_id=iid,
                        reference_type="RECONCILIATION_CASE",
                        reference_id=case_active_id,
                        reconciliation_case_id=case_active_id,
                        description="Baris faktur B10",
                        quantity=Decimal("9900.000"),
                        unit="kg",
                        unit_price=Decimal("2850.00"),
                        line_amount=amt,
                        created_at=now,
                    )
                )
            for iid in (inv_ap_unpaid, inv_ap_farmer):
                session.add(
                    PaymentApprovalModel(
                        id=uuid4(),
                        invoice_id=iid,
                        requested_by=fin_uid,
                        approver_id=dir_uid,
                        decision="APPROVED",
                        decision_reason="Disetujui B10",
                        requested_at=now,
                        decided_at=now,
                    )
                )
            session.add(
                PaymentRecordModel(
                    id=uuid4(),
                    payment_number="PAY-IN-B10-01",
                    invoice_id=inv_ar,
                    payment_direction="INBOUND",
                    payer_party_id=p_mc,
                    payee_party_id=p_perumda,
                    amount=Decimal("28215000.00"),
                    payment_date=now.date(),
                    payment_method="BANK_TRANSFER_MANUAL",
                    payment_reference="REF-B10-IN-01",
                    proof_file_id=proof_id,
                    status="VERIFIED",
                    recorded_by=fin_uid,
                    verified_by=dir_uid,
                    verified_at=now,
                    created_at=now,
                )
            )
            session.add(
                PaymentRecordModel(
                    id=uuid4(),
                    payment_number="PAY-OUT-FRM-01",
                    invoice_id=inv_ap_farmer,
                    payment_direction="OUTBOUND",
                    payer_party_id=p_perumda,
                    payee_party_id=p_f1,
                    amount=Decimal("5000000.00"),
                    payment_date=now.date(),
                    payment_method="BANK_TRANSFER_MANUAL",
                    payment_reference="REF-B10-FRM-01",
                    proof_file_id=proof_id,
                    status="VERIFIED",
                    recorded_by=fin_uid,
                    verified_by=dir_uid,
                    verified_at=now,
                    created_at=now,
                )
            )

            # Audit row containing sensitive keys that MUST be redacted on read
            append_audit_event(
                session,
                AuditRecordInput(
                    actor_id=sys_uid,
                    event_type="SECURITY_AUDIT_TEST",
                    module="admin",
                    resource_type="user_accounts",
                    resource_id=str(sys_uid),
                    new_state={
                        "bank_account": "12345678901234",
                        "password": "should_never_leak_secret",
                        "safe_flag": "ok",
                    },
                    reason="Audit rekening 123456789012345 dan bearer abcdef.ghij.klmn",
                    request_id="req_audit_b10_redact",
                ),
            )

    app = create_app(settings=cfg, db_dsn_override=test_db_url, redis_url_override=test_redis_url)
    async with app.router.lifespan_context(app):
        yield {
            "app": app,
            "cfg": cfg,
            "test_db_url": test_db_url,
            "sf": sf,
            "case_active_id": case_active_id,
            "mill_id": str(mill_id),
        }

    await redis_client.aclose()
    await dispose_database(engine)


@pytest.mark.asyncio
async def test_b10_reports_scope_caching_rules_audit_and_observability(b10_env: dict) -> None:
    transport = httpx.ASGITransport(app=b10_env["app"])
    sys_c, csrf_s = await _login(transport, username="sys_b10", password="AdmPass#2026")
    dir_c, csrf_d = await _login(transport, username="dir_b10", password="AdmPass#2026")
    fin_c, _ = await _login(transport, username="fin_b10", password="AdmPass#2026")
    pks_c, _ = await _login(transport, username="pks_b10", password="AdmPass#2026")
    coop1_c, _ = await _login(transport, username="coop1_b10", password="AdmPass#2026")
    f1_c, _ = await _login(transport, username="farmer1_b10", password="AdmPass#2026")
    f2_c, _ = await _login(transport, username="farmer2_b10", password="AdmPass#2026")

    try:
        # 1. Overview report isolates CANCELLED + role scopes + Redis cache hit tracking
        r_f1_miss = await f1_c.get("/api/v1/reports/overview")
        assert r_f1_miss.status_code == 200
        d1 = r_f1_miss.json()["data"]
        assert d1["total_receipts_count"] == 1
        assert d1["total_received_weight_kg"] == "10000.000"
        assert d1["farmer_paid_amount"] == "5000000.00"

        # Cache hit on second call + isolated farmer2 gets 0 (not farmer1 cached value!)
        r_f1_hit = await f1_c.get("/api/v1/reports/overview")
        assert r_f1_hit.status_code == 200
        r_f2 = await f2_c.get("/api/v1/reports/overview")
        assert r_f2.status_code == 200
        assert r_f2.json()["data"]["total_receipts_count"] == 0
        assert r_f2.json()["data"]["farmer_paid_amount"] == "0.00"

        # Mill operator never receives farmer payout amounts
        r_pks = await pks_c.get("/api/v1/reports/overview")
        assert r_pks.status_code == 200
        assert r_pks.json()["data"]["farmer_paid_amount"] is None

        # 2. Supply & Reconciliation reports exclude CANCELLED rows
        sup = await coop1_c.get(f"/api/v1/reports/supply?mill_id={b10_env['mill_id']}")
        assert sup.status_code == 200
        sdata = sup.json()["data"]
        assert sdata["excluded_cancelled_count"] == 1
        assert sdata["total_origin_kg"] == "10000.000"
        assert sdata["total_mill_received_kg"] == "9900.000"

        rec = await dir_c.get("/api/v1/reports/reconciliation")
        assert rec.status_code == 200
        assert rec.json()["data"]["matched_count"] == 1

        # 3. Finance report restricted to Finance & Director + BR-MRG-005 non-net-profit label
        assert (await f1_c.get("/api/v1/reports/finance")).status_code == 403
        assert (await coop1_c.get("/api/v1/reports/finance")).status_code == 403
        assert (await pks_c.get("/api/v1/reports/finance")).status_code == 403

        fin_rep = await fin_c.get("/api/v1/reports/finance")
        assert fin_rep.status_code == 200
        fdata = fin_rep.json()["data"]
        assert fdata["ar_billed_total"] == "28215000.00"
        assert fdata["ar_cash_collected_total"] == "28215000.00"
        assert fdata["ap_approved_unpaid_total"] == "20000000.00"
        assert fdata["ap_verified_paid_total"] == "5000000.00"
        assert fdata["farmer_disbursed_verified_total"] == "5000000.00"
        assert fdata["gross_contribution_simulation"] == "3215000.00"
        assert fdata["is_net_profit"] is False
        assert "Simulasi" in fdata["margin_label"]

        # 4. BR-SYS-002 rule creation: SYSTEM_ADMIN cannot create CONFIRMED rule, Director can
        assert (
            await sys_c.post(
                "/api/v1/admin/rule-versions",
                headers={"X-CSRF-Token": csrf_s},
                json={
                    "rule_code": "RECONCILIATION_TOLERANCE",
                    "effective_from": "2026-12-01T00:00:00Z",
                    "rule_config": {"tolerance_percent": "2.0000"},
                    "policy_classification": "CONFIRMED",
                    "reason": "Admin mencoba sahkan final.",
                },
            )
        ).status_code == 403

        r_sim = await sys_c.post(
            "/api/v1/admin/rule-versions",
            headers={"X-CSRF-Token": csrf_s},
            json={
                "rule_code": "RECONCILIATION_TOLERANCE",
                "effective_from": "2026-12-01T00:00:00Z",
                "rule_config": {"tolerance_percent": "2.0000"},
                "policy_classification": "SIMULATION_ONLY",
                "reason": "Simulasi toleransi baru.",
            },
        )
        assert r_sim.status_code == 201
        assert r_sim.json()["data"]["version_number"] == 2
        assert r_sim.json()["data"]["approval_status"] == "DRAFT"

        r_dir = await dir_c.post(
            "/api/v1/admin/rule-versions",
            headers={"X-CSRF-Token": csrf_d},
            json={
                "rule_code": "RECONCILIATION_TOLERANCE",
                "effective_from": "2026-12-15T00:00:00Z",
                "rule_config": {"tolerance_percent": "1.2500"},
                "policy_classification": "CONFIRMED",
                "reason": "Pengesahan SOP Direksi v3.",
            },
        )
        assert r_dir.status_code == 201
        assert r_dir.json()["data"]["version_number"] == 3
        assert r_dir.json()["data"]["approval_status"] == "APPROVED"

        # Historical reconciliation retains v1 RULE_RECONCILIATION_TOLERANCE_ID untouched
        async with b10_env["sf"]() as session:
            rec_row = await session.get(ReconciliationCaseModel, b10_env["case_active_id"])
            assert rec_row is not None
            assert rec_row.rule_version_id == RULE_RECONCILIATION_TOLERANCE_ID

        # 5. Audit viewer + secret/account redaction
        assert (await fin_c.get("/api/v1/admin/audit-events")).status_code == 403
        aud = await sys_c.get("/api/v1/admin/audit-events?request_id=req_audit_b10_redact")
        assert aud.status_code == 200
        aitem = aud.json()["data"][0]
        assert aitem["new_state"]["password"] == "[REDACTED]"
        assert aitem["new_state"]["bank_account"] == "[REDACTED]"
        assert "123456789012345" not in (aitem["reason"] or "")

        # 6. System health CCTV Digital: SYSTEM_ADMIN ONLY + live cache ratio & 24h metrics
        assert (await dir_c.get("/api/v1/admin/system-health")).status_code == 403
        health = await sys_c.get("/api/v1/admin/system-health")
        assert health.status_code == 200
        hdata = health.json()["data"]
        assert hdata["health"]["status"] == "ok"
        assert Decimal(hdata["redis_cache_hit_ratio_percent"]) > Decimal("0")
        assert hdata["total_requests_24h"] >= 10
    finally:
        for c in (sys_c, dir_c, fin_c, pks_c, coop1_c, f1_c, f2_c):
            await c.aclose()


@pytest.mark.asyncio
async def test_b10_reporting_falls_back_gracefully_when_redis_unavailable(b10_env: dict) -> None:
    # Direct service call with unreachable Redis URL falls back cleanly to PostgreSQL!
    bad_redis_app = create_app(
        settings=b10_env["cfg"],
        db_dsn_override=b10_env["test_db_url"],
        redis_url_override="redis://127.0.0.1:6399/1",
    )
    async with bad_redis_app.router.lifespan_context(bad_redis_app):
        async with b10_env["sf"]() as session:
            dir_uid = (
                await session.execute(
                    text("SELECT id FROM user_accounts WHERE username = 'dir_b10'")
                )
            ).scalar_one()
        from app.modules.identity_access.domain.entities import (
            AccessScopeEntity,
            AccountStatus,
            AuthenticatedPrincipal,
            ScopeType,
        )

        principal = AuthenticatedPrincipal(
            session_id=uuid4(),
            user_id=dir_uid,
            username="dir_b10",
            email="dir_b10@agroniaga.local",
            display_name="dir_b10",
            linked_party_id=None,
            status=AccountStatus.ACTIVE,
            roles=(RoleCode.DIRECTOR,),
            access_scopes=(
                AccessScopeEntity(
                    id=uuid4(),
                    scope_type=ScopeType.PERUMDA_GLOBAL,
                    farmer_id=None,
                    cooperative_id=None,
                    mill_id=None,
                ),
            ),
            permissions=frozenset({"reports.operational.read", "reports.finance.read"}),
            last_login_at=None,
            non_approver_admin=False,
        )
        overview = await bad_redis_app.state.reporting_service.get_overview(
            principal=principal, date_from=None, date_to=None
        )
        assert overview.total_receipts_count == 1
        assert overview.total_received_weight_kg == Decimal("10000.000")
