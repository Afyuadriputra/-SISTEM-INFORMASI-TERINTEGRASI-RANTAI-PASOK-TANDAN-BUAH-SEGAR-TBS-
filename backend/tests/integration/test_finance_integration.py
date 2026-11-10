"""PostgreSQL + Redis integration tests for Finance AR/AP, Approvals & Payments (B9)."""

from __future__ import annotations

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
    RULE_RECONCILIATION_TOLERANCE_ID,
    seed_baseline_system_rules,
)
from app.main import create_app
from app.modules.contracts.infrastructure.models import TradeContractModel
from app.modules.files.infrastructure.models import FileAssetModel
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
from app.modules.pricing.infrastructure.models import (
    MillPriceQuoteModel,
    deterministic_category_id,
    deterministic_source_id,
    seed_pricing_catalog,
)
from app.modules.reconciliation.infrastructure.models import ReconciliationCaseModel
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
async def b9_env(test_db_url: str | None, test_redis_url: str | None) -> AsyncIterator[dict]:
    assert test_db_url and test_redis_url
    assert test_redis_url.endswith("/1")

    cfg = Settings(LOG_JSON=False)
    engine = build_async_engine(cfg, dsn_override=test_db_url)
    sf = build_session_factory(engine)
    redis_client = Redis.from_url(test_redis_url, decode_responses=True)

    now = datetime.now(UTC)
    hasher = Argon2PasswordHasher()
    pw_hash = await hasher.hash_password("FinPass#2026")

    p_perumda, p_mc, p_coop, p_farmer1, p_farmer2 = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    mc_id, mill_id, coop_id, farmer1_id, farmer2_id = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    farm1_id, farm2_id, veh_id, drv_id = uuid4(), uuid4(), uuid4(), uuid4()
    ctr_principal_id, ctr_unconfirmed_id, ctr_formula_id = uuid4(), uuid4(), uuid4()
    do_principal_id, do_dispute_id, do_unconfirmed_id, do_formula_id = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    tkt_principal_id, tkt_dispute_id, tkt_unconfirmed_id, tkt_formula_id = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    case_matched_id, case_dispute_id, case_unconfirmed_id, case_formula_id = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    proof_in_id, proof_out_coop_id, proof_out_farmer_id = uuid4(), uuid4(), uuid4()

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
                    "trade_contracts, mill_price_quotes, price_categories, price_sources, "
                    "receipt_grading_items, receipt_weighing_revisions, "
                    "tbs_receipts, farms, cooperative_memberships, farmers, cooperatives, "
                    "mills, mill_companies, vehicles, drivers, parties, system_rule_versions "
                    "RESTART IDENTITY CASCADE"
                )
            )
            await seed_rbac_catalog(session)
            await seed_baseline_system_rules(session)
            await seed_pricing_catalog(session)

            for pid, ptype, pname in (
                (p_perumda, "PERUMDA", "Perumda Tuah Sekata"),
                (p_mc, "MILL_COMPANY", "PT Sawit Keuangan"),
                (p_coop, "COOPERATIVE", "KUD Keuangan"),
                (p_farmer1, "FARMER", "Petani Satu"),
                (p_farmer2, "FARMER", "Petani Dua"),
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
                    cooperative_code="KOP-B9",
                    cooperative_name="KUD Keuangan",
                    address="Pelalawan",
                    contact_phone="08120001",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            session.add(
                MillCompanyModel(
                    id=mc_id,
                    party_id=p_mc,
                    company_code="MC-B9",
                    company_name="PT Sawit Keuangan",
                    contact_phone="07610001",
                    address="Pekanbaru",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()

            for fid, fpid, fcode, fname in (
                (farmer1_id, p_farmer1, "FRM-B9-1", "Petani Satu"),
                (farmer2_id, p_farmer2, "FRM-B9-2", "Petani Dua"),
            ):
                session.add(
                    FarmerModel(
                        id=fid,
                        party_id=fpid,
                        farmer_code=fcode,
                        full_name=fname,
                        identity_reference=f"140500{fcode[-1]}",
                        contact_phone=f"0813000{fcode[-1]}",
                        status="ACTIVE",
                        version=1,
                        created_at=now,
                        updated_at=now,
                    )
                )
            await session.flush()
            for fid in (farmer1_id, farmer2_id):
                session.add(
                    CooperativeMembershipModel(
                        id=uuid4(),
                        cooperative_id=coop_id,
                        farmer_id=fid,
                        membership_number=f"MEM-{str(fid)[:4]}",
                        joined_at=now,
                        ended_at=None,
                        status="ACTIVE",
                    )
                )
            for farm_id, fid, fcode in (
                (farm1_id, farmer1_id, "KB-B9-1"),
                (farm2_id, farmer2_id, "KB-B9-2"),
            ):
                session.add(
                    FarmModel(
                        id=farm_id,
                        farmer_id=fid,
                        farm_code=fcode,
                        farm_name=f"Kebun {fcode}",
                        area_hectares=Decimal("3.0000"),
                        planting_year=2018,
                        stdb_number=None,
                        village="Makmur",
                        district="Kerinci",
                        latitude=Decimal("0.410000"),
                        longitude=Decimal("101.850000"),
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
                    mill_code="PKS-B9",
                    mill_name="PKS Pelalawan Finance",
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
                    plate_number="BM 9999 FIN",
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
                    full_name="Sopir B9",
                    contact_phone="08129991",
                    driver_reference="SIM-B9",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()

            fin_maker_uid = uuid4()
            actors = (
                ("fin_maker_1", RoleCode.PERUMDA_FINANCE, ScopeType.PERUMDA_GLOBAL, None, None),
                ("fin_checker_2", RoleCode.PERUMDA_FINANCE, ScopeType.PERUMDA_GLOBAL, None, None),
                ("dir_b9", RoleCode.DIRECTOR, ScopeType.PERUMDA_GLOBAL, None, None),
                ("ops_b9", RoleCode.PERUMDA_OPERATIONS, ScopeType.PERUMDA_GLOBAL, None, None),
                ("pks_b9", RoleCode.MILL_OPERATOR, ScopeType.MILL, None, None),
                ("coop_b9", RoleCode.COOPERATIVE_OPERATOR, ScopeType.COOPERATIVE, None, coop_id),
                ("farmer1_b9", RoleCode.FARMER, ScopeType.FARMER, farmer1_id, None),
                ("farmer2_b9", RoleCode.FARMER, ScopeType.FARMER, farmer2_id, None),
                ("sys_admin_b9", RoleCode.SYSTEM_ADMIN, ScopeType.PERUMDA_GLOBAL, None, None),
            )
            for uname, role, stype, f_scope, c_scope in actors:
                uid = fin_maker_uid if uname == "fin_maker_1" else uuid4()
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
                        farmer_id=f_scope,
                        cooperative_id=c_scope,
                        mill_id=mill_id if role == RoleCode.MILL_OPERATOR else None,
                        granted_by=None,
                        created_at=now,
                        revoked_at=None,
                    )
                )

            for proof_id, key in (
                (proof_in_id, "test/fin-in.pdf"),
                (proof_out_coop_id, "test/fin-out-coop.pdf"),
                (proof_out_farmer_id, "test/fin-out-farmer.pdf"),
            ):
                session.add(
                    FileAssetModel(
                        id=proof_id,
                        storage_provider="LOCAL_DISK",
                        storage_key=key,
                        original_filename=f"{key.split('/')[-1]}",
                        mime_type="application/pdf",
                        size_bytes=12345,
                        checksum=f"sha256:{proof_id.hex}",
                        classification="PAYMENT_PROOF",
                        uploaded_by=fin_maker_uid,
                        created_at=now,
                    )
                )

            session.add(
                MillPriceQuoteModel(
                    id=uuid4(),
                    mill_id=mill_id,
                    price_category_id=deterministic_category_id("SWADAYA_STD"),
                    source_id=deterministic_source_id("MILL_OFFICIAL"),
                    price_per_kg=Decimal("2650.00"),
                    effective_from=now - timedelta(days=2),
                    effective_until=now - timedelta(hours=1),
                    status="PUBLISHED",
                    submitted_by=fin_maker_uid,
                    verified_by=fin_maker_uid,
                    verified_at=now - timedelta(days=2),
                    published_at=now - timedelta(days=2),
                    source_document_id=None,
                    notes="Harga historis saat e-DO",
                    is_simulation=False,
                    version=1,
                    created_at=now - timedelta(days=2),
                    updated_at=now - timedelta(days=2),
                )
            )

            for cid, num, rule_type, price, bmc, prole in (
                (
                    ctr_principal_id,
                    "KTR-B9-PRIN",
                    "FIXED",
                    Decimal("2850.00"),
                    "PRINCIPAL",
                    "SELLER",
                ),
                (
                    ctr_unconfirmed_id,
                    "KTR-B9-UNC",
                    "FIXED",
                    Decimal("2500.00"),
                    "UNCONFIRMED",
                    "UNCONFIRMED",
                ),
                (
                    ctr_formula_id,
                    "KTR-B9-FRM",
                    "REFERENCE_FORMULA",
                    None,
                    "PRINCIPAL",
                    "SELLER",
                ),
            ):
                session.add(
                    TradeContractModel(
                        id=cid,
                        contract_number=num,
                        mill_id=mill_id,
                        start_date=now.date() - timedelta(days=10),
                        end_date=now.date() + timedelta(days=30),
                        price_rule_type=rule_type,
                        agreed_price_per_kg=price,
                        grading_policy_reference="BSD-DEC-006",
                        business_model_code=bmc,
                        perumda_role=prole,
                        seller_party_id=p_perumda,
                        buyer_party_id=p_mc,
                        agent_party_id=None,
                        represented_party_id=None,
                        business_model_rule_version=RULE_BUSINESS_MODEL_POLICY_ID,
                        payment_terms="14 hari",
                        status="ACTIVE",
                        created_by=fin_maker_uid,
                        approved_by=fin_maker_uid,
                        approved_at=now,
                        version=2,
                        created_at=now,
                        updated_at=now,
                    )
                )
            await session.flush()

            scenarios = (
                (
                    do_principal_id,
                    ctr_principal_id,
                    tkt_principal_id,
                    case_matched_id,
                    "MATCHED",
                    Decimal("9900.000"),
                    now,
                    farmer1_id,
                    farm1_id,
                ),
                (
                    do_dispute_id,
                    ctr_principal_id,
                    tkt_dispute_id,
                    case_dispute_id,
                    "DISPUTE_HOLD",
                    Decimal("9400.000"),
                    now,
                    farmer1_id,
                    farm1_id,
                ),
                (
                    do_unconfirmed_id,
                    ctr_unconfirmed_id,
                    tkt_unconfirmed_id,
                    case_unconfirmed_id,
                    "MATCHED",
                    Decimal("9900.000"),
                    now,
                    farmer2_id,
                    farm2_id,
                ),
                (
                    do_formula_id,
                    ctr_formula_id,
                    tkt_formula_id,
                    case_formula_id,
                    "MATCHED",
                    Decimal("10000.000"),
                    now - timedelta(days=1),
                    farmer1_id,
                    farm1_id,
                ),
            )
            for idx, (did, cid, tid, case_id, rec_status, m_kg, ts_ref, fid, farm_id) in enumerate(
                scenarios, start=1
            ):
                rec_id = uuid4()
                session.add(
                    TbsReceiptModel(
                        id=rec_id,
                        receipt_number=f"TBS-B9-{idx:03d}",
                        farmer_id=fid,
                        farm_id=farm_id,
                        cooperative_id=coop_id,
                        harvest_date=now.date(),
                        received_at=ts_ref,
                        status="SHIPPED",
                        notes=None,
                        created_by=fin_maker_uid,
                        created_at=ts_ref,
                        updated_at=ts_ref,
                        version=2,
                    )
                )
                session.add(
                    DeliveryOrderModel(
                        id=did,
                        delivery_order_number=f"EDO-B9-{idx:03d}",
                        cooperative_id=coop_id,
                        mill_id=mill_id,
                        contract_id=cid,
                        vehicle_id=veh_id,
                        driver_id=drv_id,
                        total_origin_weight_kg=Decimal("10000.000"),
                        status="RECEIVED",
                        issued_at=ts_ref,
                        departed_at=ts_ref,
                        arrived_at=ts_ref,
                        completed_at=None,
                        qr_verification_token=f"QRT-B9-{idx:03d}",
                        qr_reference_hash=f"{'a' * 63}{idx}",
                        created_by=fin_maker_uid,
                        version=3,
                        created_at=ts_ref,
                        updated_at=ts_ref,
                    )
                )
                await session.flush()
                session.add(
                    DeliveryOrderLineModel(
                        id=uuid4(),
                        delivery_order_id=did,
                        receipt_id=rec_id,
                        origin_weight_snapshot_kg=Decimal("10000.000"),
                        allocation_status="ACTIVE",
                        created_at=ts_ref,
                    )
                )
                session.add(
                    MillWeighingTicketModel(
                        id=tid,
                        delivery_order_id=did,
                        mill_id=mill_id,
                        ticket_number=f"WB-B9-{idx:03d}",
                        revision_number=1,
                        previous_ticket_id=None,
                        gross_weight_kg=m_kg + Decimal("5000.000"),
                        tare_weight_kg=Decimal("5000.000"),
                        net_weight_kg=m_kg,
                        weighed_at=ts_ref,
                        verified_at=ts_ref,
                        verified_by=fin_maker_uid,
                        is_current=True,
                        status="VERIFIED",
                        proof_file_id=proof_in_id,
                        correction_reason=None,
                        created_by=fin_maker_uid,
                        created_at=ts_ref,
                    )
                )
                await session.flush()
                session.add(
                    ReconciliationCaseModel(
                        id=case_id,
                        delivery_order_id=did,
                        mill_ticket_id=tid,
                        revision_number=1,
                        origin_weight_kg=Decimal("10000.000"),
                        mill_weight_kg=m_kg,
                        difference_weight_kg=Decimal("10000.000") - m_kg,
                        difference_percent=Decimal("1.0000"),
                        tolerance_percent=Decimal("1.5000"),
                        rule_version_id=RULE_RECONCILIATION_TOLERANCE_ID,
                        tolerance_policy_classification="SIMULATION_ONLY",
                        is_negative_difference=False,
                        status=rec_status,
                        is_current=True,
                        agreed_settlement_weight_kg=None,
                        calculated_at=ts_ref,
                        resolved_at=None,
                        created_by=fin_maker_uid,
                        created_at=ts_ref,
                    )
                )

    app = create_app(settings=cfg, db_dsn_override=test_db_url, redis_url_override=test_redis_url)
    async with app.router.lifespan_context(app):
        yield {
            "app": app,
            "sf": sf,
            "now": now,
            "mill_id": mill_id,
            "p_perumda": str(p_perumda),
            "p_mc": str(p_mc),
            "p_coop": str(p_coop),
            "p_farmer1": str(p_farmer1),
            "p_farmer2": str(p_farmer2),
            "case_matched_id": str(case_matched_id),
            "case_dispute_id": str(case_dispute_id),
            "case_unconfirmed_id": str(case_unconfirmed_id),
            "case_formula_id": str(case_formula_id),
            "tkt_principal_id": str(tkt_principal_id),
            "proof_in_id": str(proof_in_id),
            "proof_out_coop_id": str(proof_out_coop_id),
            "proof_out_farmer_id": str(proof_out_farmer_id),
            "fin_maker_uid": fin_maker_uid,
        }

    await redis_client.aclose()
    await dispose_database(engine)


@pytest.mark.asyncio
async def test_b9_finance_lifecycle_sod_idempotency_finality_and_privacy(b9_env: dict) -> None:
    transport = httpx.ASGITransport(app=b9_env["app"])
    fin1, csrf_f1 = await _login(transport, username="fin_maker_1", password="FinPass#2026")
    fin2, csrf_f2 = await _login(transport, username="fin_checker_2", password="FinPass#2026")
    dir_c, csrf_d = await _login(transport, username="dir_b9", password="FinPass#2026")
    ops_c, _ = await _login(transport, username="ops_b9", password="FinPass#2026")
    pks_c, csrf_p = await _login(transport, username="pks_b9", password="FinPass#2026")
    coop_c, _ = await _login(transport, username="coop_b9", password="FinPass#2026")
    f1_c, _ = await _login(transport, username="farmer1_b9", password="FinPass#2026")
    f2_c, _ = await _login(transport, username="farmer2_b9", password="FinPass#2026")
    sys_c, csrf_s = await _login(transport, username="sys_admin_b9", password="FinPass#2026")

    try:
        # 1. DISPUTE_HOLD blocks createInvoiceDraft
        dispute_resp = await fin1.post(
            "/api/v1/invoices",
            headers={"X-CSRF-Token": csrf_f1},
            json={
                "invoice_type": "ACCOUNTS_RECEIVABLE",
                "creditor_party_id": b9_env["p_perumda"],
                "debtor_party_id": b9_env["p_mc"],
                "reconciliation_case_id": b9_env["case_dispute_id"],
                "invoice_date": "2026-11-10",
            },
        )
        assert dispute_resp.status_code == 409
        assert dispute_resp.json()["error"]["code"] == "FIN_DISPUTE_HOLD_BLOCKED"

        # 2. Invalid AR party pairing rejected
        bad_pair = await fin1.post(
            "/api/v1/invoices",
            headers={"X-CSRF-Token": csrf_f1},
            json={
                "invoice_type": "ACCOUNTS_RECEIVABLE",
                "creditor_party_id": b9_env["p_perumda"],
                "debtor_party_id": b9_env["p_coop"],
                "reconciliation_case_id": b9_env["case_matched_id"],
                "invoice_date": "2026-11-10",
            },
        )
        assert bad_pair.status_code == 422
        assert bad_pair.json()["error"]["code"] == "PAY_INVALID_PARTY_PAIRING"

        # 3. UNCONFIRMED policy allows draft & verify but blocks issueInvoice (409 FIN_POLICY_UNCONFIRMED)
        unc_draft = await fin1.post(
            "/api/v1/invoices",
            headers={"X-CSRF-Token": csrf_f1},
            json={
                "invoice_type": "ACCOUNTS_RECEIVABLE",
                "creditor_party_id": b9_env["p_perumda"],
                "debtor_party_id": b9_env["p_mc"],
                "reconciliation_case_id": b9_env["case_unconfirmed_id"],
                "invoice_date": "2026-11-10",
            },
        )
        assert unc_draft.status_code == 201
        unc_inv_id = unc_draft.json()["data"]["id"]
        assert (
            await fin2.post(
                f"/api/v1/invoices/{unc_inv_id}/verify",
                headers={"X-CSRF-Token": csrf_f2},
                json={"decision": "APPROVE"},
            )
        ).status_code == 200
        unc_issue = await fin1.post(
            f"/api/v1/invoices/{unc_inv_id}/issue",
            headers={"X-CSRF-Token": csrf_f1},
        )
        assert unc_issue.status_code == 409
        assert unc_issue.json()["error"]["code"] == "FIN_POLICY_UNCONFIRMED"

        # 4. AR Invoice happy path + SOD-04 + BR-SYS-002 + MILL_TICKET_ALREADY_FINAL
        ar_draft = await fin1.post(
            "/api/v1/invoices",
            headers={"X-CSRF-Token": csrf_f1},
            json={
                "invoice_type": "ACCOUNTS_RECEIVABLE",
                "creditor_party_id": b9_env["p_perumda"],
                "debtor_party_id": b9_env["p_mc"],
                "reconciliation_case_id": b9_env["case_matched_id"],
                "invoice_date": "2026-11-10",
                "due_date": "2026-11-24",
            },
        )
        assert ar_draft.status_code == 201
        ar_data = ar_draft.json()["data"]
        ar_id = ar_data["id"]
        assert ar_data["total_amount"] == "28215000.00"
        assert ar_data["status"] == "PENDING_VERIFICATION"

        # SOD-04: maker cannot verify
        assert (
            await fin1.post(
                f"/api/v1/invoices/{ar_id}/verify",
                headers={"X-CSRF-Token": csrf_f1},
                json={"decision": "APPROVE"},
            )
        ).status_code == 403
        # BR-SYS-002: SYSTEM_ADMIN cannot verify invoice or approve payment
        assert (
            await sys_c.post(
                f"/api/v1/invoices/{ar_id}/verify",
                headers={"X-CSRF-Token": csrf_s},
                json={"decision": "APPROVE"},
            )
        ).status_code == 403
        assert (
            await sys_c.post(
                f"/api/v1/payments/{ar_id}/approve",
                headers={"X-CSRF-Token": csrf_s, "Idempotency-Key": str(uuid4())},
                json={"decision": "APPROVED", "reason": "Admin tidak boleh approve"},
            )
        ).status_code == 403

        # Checker verifies, fin1 issues
        assert (
            await fin2.post(
                f"/api/v1/invoices/{ar_id}/verify",
                headers={"X-CSRF-Token": csrf_f2},
                json={"decision": "APPROVE"},
            )
        ).status_code == 200
        ar_issued = await fin1.post(
            f"/api/v1/invoices/{ar_id}/issue",
            headers={"X-CSRF-Token": csrf_f1},
        )
        assert ar_issued.status_code == 200
        assert ar_issued.json()["data"]["status"] == "ISSUED"

        # Issued invoice blocks ticket revision with MILL_TICKET_ALREADY_FINAL
        rev_blocked = await pks_c.patch(
            f"/api/v1/mill-tickets/{b9_env['tkt_principal_id']}",
            headers={"X-CSRF-Token": csrf_p},
            json={
                "gross_weight_kg": "14800.000",
                "tare_weight_kg": "5000.000",
                "correction_reason": "Coba ubah setelah invoice terbit",
            },
        )
        assert rev_blocked.status_code == 409
        assert rev_blocked.json()["error"]["code"] == "MILL_TICKET_ALREADY_FINAL"

        # 5. Historical price snapshot test (formula DO keeps 2650.00 after newer 2900.00 published)
        formula_draft = await fin1.post(
            "/api/v1/invoices",
            headers={"X-CSRF-Token": csrf_f1},
            json={
                "invoice_type": "ACCOUNTS_RECEIVABLE",
                "creditor_party_id": b9_env["p_perumda"],
                "debtor_party_id": b9_env["p_mc"],
                "reconciliation_case_id": b9_env["case_formula_id"],
                "invoice_date": "2026-11-10",
            },
        )
        assert formula_draft.status_code == 201
        formula_inv_id = formula_draft.json()["data"]["id"]
        assert formula_draft.json()["data"]["total_amount"] == "26500000.00"

        async with b9_env["sf"]() as session:
            async with session.begin():
                session.add(
                    MillPriceQuoteModel(
                        id=uuid4(),
                        mill_id=b9_env["mill_id"],
                        price_category_id=deterministic_category_id("SWADAYA_STD"),
                        source_id=deterministic_source_id("MILL_OFFICIAL"),
                        price_per_kg=Decimal("2900.00"),
                        effective_from=b9_env["now"],
                        effective_until=b9_env["now"] + timedelta(days=5),
                        status="PUBLISHED",
                        submitted_by=b9_env["fin_maker_uid"],
                        verified_by=b9_env["fin_maker_uid"],
                        verified_at=b9_env["now"],
                        published_at=b9_env["now"],
                        source_document_id=None,
                        notes="Kenaikan harga baru",
                        is_simulation=False,
                        version=1,
                        created_at=b9_env["now"],
                        updated_at=b9_env["now"],
                    )
                )
        formula_after = await ops_c.get(f"/api/v1/invoices/{formula_inv_id}")
        assert formula_after.status_code == 200
        assert formula_after.json()["data"]["total_amount"] == "26500000.00"
        assert formula_after.json()["data"]["lines"][0]["unit_price"] == "2650.00"

        # 6. AR INBOUND Payment flow (partial, overpay, idempotency, unverified != PAID, SOD-06, verify -> PAID)
        partial_in = await fin1.post(
            "/api/v1/payments",
            headers={"X-CSRF-Token": csrf_f1, "Idempotency-Key": str(uuid4())},
            json={
                "invoice_id": ar_id,
                "payment_direction": "INBOUND",
                "payer_party_id": b9_env["p_mc"],
                "payee_party_id": b9_env["p_perumda"],
                "amount": "10000000.00",
                "payment_date": "2026-11-10",
                "payment_method": "BANK_TRANSFER_MANUAL",
                "payment_reference": "TRF-IN-PARTIAL",
                "proof_file_id": b9_env["proof_in_id"],
            },
        )
        assert partial_in.status_code == 422
        assert partial_in.json()["error"]["code"] == "PAY_PARTIAL_NOT_SUPPORTED"

        overpay_in = await fin1.post(
            "/api/v1/payments",
            headers={"X-CSRF-Token": csrf_f1, "Idempotency-Key": str(uuid4())},
            json={
                "invoice_id": ar_id,
                "payment_direction": "INBOUND",
                "payer_party_id": b9_env["p_mc"],
                "payee_party_id": b9_env["p_perumda"],
                "amount": "30000000.00",
                "payment_date": "2026-11-10",
                "payment_method": "BANK_TRANSFER_MANUAL",
                "payment_reference": "TRF-IN-OVER",
                "proof_file_id": b9_env["proof_in_id"],
            },
        )
        assert overpay_in.status_code == 422
        assert overpay_in.json()["error"]["code"] == "PAY_AMOUNT_EXCEEDS_INVOICE"

        idem_in = str(uuid4())
        in_payload = {
            "invoice_id": ar_id,
            "payment_direction": "INBOUND",
            "payer_party_id": b9_env["p_mc"],
            "payee_party_id": b9_env["p_perumda"],
            "amount": "28215000.00",
            "payment_date": "2026-11-10",
            "payment_method": "BANK_TRANSFER_MANUAL",
            "payment_reference": "TRF-IN-001",
            "proof_file_id": b9_env["proof_in_id"],
        }
        pay_in_1 = await fin1.post(
            "/api/v1/payments",
            headers={"X-CSRF-Token": csrf_f1, "Idempotency-Key": idem_in},
            json=in_payload,
        )
        assert pay_in_1.status_code == 201
        pay_in_id = pay_in_1.json()["data"]["id"]

        pay_in_replay = await fin1.post(
            "/api/v1/payments",
            headers={"X-CSRF-Token": csrf_f1, "Idempotency-Key": idem_in},
            json=in_payload,
        )
        assert pay_in_replay.status_code == 201
        assert pay_in_replay.json()["meta"]["idempotency_replayed"] is True
        assert pay_in_replay.json()["data"]["id"] == pay_in_id

        # Unverified payment must NOT mark invoice PAID
        inv_before_v = (await fin2.get(f"/api/v1/invoices/{ar_id}")).json()["data"]
        assert inv_before_v["settlement_status"] == "PENDING_VERIFICATION"

        # SOD-06 blocks fin1 from verifying own recorded payment
        assert (
            await fin1.post(
                f"/api/v1/payments/{pay_in_id}/verify",
                headers={"X-CSRF-Token": csrf_f1},
                json={"decision": "VERIFIED"},
            )
        ).status_code == 403

        assert (
            await fin2.post(
                f"/api/v1/payments/{pay_in_id}/verify",
                headers={"X-CSRF-Token": csrf_f2},
                json={"decision": "VERIFIED"},
            )
        ).status_code == 200
        assert (await fin2.get(f"/api/v1/invoices/{ar_id}")).json()["data"][
            "settlement_status"
        ] == "PAID"

        # 7. AP OUTBOUND Cooperative + Direct Farmer Payment (SM-10 APPROVED != PAID, reversal)
        ap_coop_draft = await fin1.post(
            "/api/v1/invoices",
            headers={"X-CSRF-Token": csrf_f1},
            json={
                "invoice_type": "ACCOUNTS_PAYABLE",
                "creditor_party_id": b9_env["p_coop"],
                "debtor_party_id": b9_env["p_perumda"],
                "reconciliation_case_id": b9_env["case_matched_id"],
                "invoice_date": "2026-11-10",
            },
        )
        assert ap_coop_draft.status_code == 201
        ap_coop_id = ap_coop_draft.json()["data"]["id"]
        assert (
            await fin2.post(
                f"/api/v1/invoices/{ap_coop_id}/verify",
                headers={"X-CSRF-Token": csrf_f2},
                json={"decision": "APPROVE"},
            )
        ).status_code == 200
        assert (
            await fin1.post(
                f"/api/v1/invoices/{ap_coop_id}/issue",
                headers={"X-CSRF-Token": csrf_f1},
            )
        ).status_code == 200

        # OUTBOUND before Director approval -> PAY_APPROVAL_REQUIRED
        unapproved_out = await fin1.post(
            "/api/v1/payments",
            headers={"X-CSRF-Token": csrf_f1, "Idempotency-Key": str(uuid4())},
            json={
                "invoice_id": ap_coop_id,
                "payment_direction": "OUTBOUND",
                "payer_party_id": b9_env["p_perumda"],
                "payee_party_id": b9_env["p_coop"],
                "amount": "28215000.00",
                "payment_date": "2026-11-10",
                "payment_method": "BANK_TRANSFER_MANUAL",
                "payment_reference": "TRF-OUT-COOP-001",
                "proof_file_id": b9_env["proof_out_coop_id"],
            },
        )
        assert unapproved_out.status_code == 409
        assert unapproved_out.json()["error"]["code"] == "PAY_APPROVAL_REQUIRED"

        # Director approves obligation (APPROVED != PAID -> AWAITING_PAYMENT)
        idem_app = str(uuid4())
        app_payload = {
            "decision": "APPROVED",
            "reason": "Disetujui bayar setelah tiket & rekonsiliasi valid.",
        }
        app_resp = await dir_c.post(
            f"/api/v1/payments/{ap_coop_id}/approve",
            headers={"X-CSRF-Token": csrf_d, "Idempotency-Key": idem_app},
            json=app_payload,
        )
        assert app_resp.status_code == 200
        assert app_resp.json()["data"]["decision"] == "APPROVED"

        app_replay = await dir_c.post(
            f"/api/v1/payments/{ap_coop_id}/approve",
            headers={"X-CSRF-Token": csrf_d, "Idempotency-Key": idem_app},
            json=app_payload,
        )
        assert app_replay.status_code == 200
        assert app_replay.json()["meta"]["idempotency_replayed"] is True

        # Different idempotency key hits PAY_ALREADY_APPROVED
        app_dup = await dir_c.post(
            f"/api/v1/payments/{ap_coop_id}/approve",
            headers={"X-CSRF-Token": csrf_d, "Idempotency-Key": str(uuid4())},
            json=app_payload,
        )
        assert app_dup.status_code == 409
        assert app_dup.json()["error"]["code"] == "PAY_ALREADY_APPROVED"

        ap_after_app = (await dir_c.get(f"/api/v1/invoices/{ap_coop_id}")).json()["data"]
        assert ap_after_app["settlement_status"] == "AWAITING_PAYMENT"

        # Record + verify AP payment -> PAID -> REVERSED reverts settlement_status
        pay_coop = await fin1.post(
            "/api/v1/payments",
            headers={"X-CSRF-Token": csrf_f1, "Idempotency-Key": str(uuid4())},
            json={
                "invoice_id": ap_coop_id,
                "payment_direction": "OUTBOUND",
                "payer_party_id": b9_env["p_perumda"],
                "payee_party_id": b9_env["p_coop"],
                "amount": "28215000.00",
                "payment_date": "2026-11-10",
                "payment_method": "BANK_TRANSFER_MANUAL",
                "payment_reference": "TRF-OUT-COOP-001",
                "proof_file_id": b9_env["proof_out_coop_id"],
            },
        )
        assert pay_coop.status_code == 201
        pay_coop_id = pay_coop.json()["data"]["id"]

        assert (
            await fin2.post(
                f"/api/v1/payments/{pay_coop_id}/verify",
                headers={"X-CSRF-Token": csrf_f2},
                json={"decision": "VERIFIED"},
            )
        ).status_code == 200
        assert (await fin2.get(f"/api/v1/invoices/{ap_coop_id}")).json()["data"][
            "settlement_status"
        ] == "PAID"

        rev_resp = await fin2.post(
            f"/api/v1/payments/{pay_coop_id}/verify",
            headers={"X-CSRF-Token": csrf_f2},
            json={"decision": "REVERSED", "reason": "Koreksi nominal retur bank."},
        )
        assert rev_resp.status_code == 200
        assert rev_resp.json()["data"]["status"] == "REVERSED"
        assert (await fin2.get(f"/api/v1/invoices/{ap_coop_id}")).json()["data"][
            "settlement_status"
        ] == "AWAITING_PAYMENT"

        # 8. Direct Farmer Jalur C AP + Role Privacy (BR-PAY-010)
        ap_farmer_draft = await fin1.post(
            "/api/v1/invoices",
            headers={"X-CSRF-Token": csrf_f1},
            json={
                "invoice_type": "ACCOUNTS_PAYABLE",
                "creditor_party_id": b9_env["p_farmer1"],
                "debtor_party_id": b9_env["p_perumda"],
                "reconciliation_case_id": b9_env["case_formula_id"],
                "invoice_date": "2026-11-10",
            },
        )
        assert ap_farmer_draft.status_code == 201
        ap_farmer_id = ap_farmer_draft.json()["data"]["id"]
        assert (
            await fin2.post(
                f"/api/v1/invoices/{ap_farmer_id}/verify",
                headers={"X-CSRF-Token": csrf_f2},
                json={"decision": "APPROVE"},
            )
        ).status_code == 200
        assert (
            await fin1.post(
                f"/api/v1/invoices/{ap_farmer_id}/issue",
                headers={"X-CSRF-Token": csrf_f1},
            )
        ).status_code == 200
        assert (
            await dir_c.post(
                f"/api/v1/payments/{ap_farmer_id}/approve",
                headers={"X-CSRF-Token": csrf_d, "Idempotency-Key": str(uuid4())},
                json={"decision": "APPROVED", "reason": "Persetujuan pembayaran Jalur C petani."},
            )
        ).status_code == 200
        pay_farmer = await fin1.post(
            "/api/v1/payments",
            headers={"X-CSRF-Token": csrf_f1, "Idempotency-Key": str(uuid4())},
            json={
                "invoice_id": ap_farmer_id,
                "payment_direction": "OUTBOUND",
                "payer_party_id": b9_env["p_perumda"],
                "payee_party_id": b9_env["p_farmer1"],
                "amount": "26500000.00",
                "payment_date": "2026-11-10",
                "payment_method": "BANK_TRANSFER_MANUAL",
                "payment_reference": "TRF-OUT-FARMER1-001",
                "proof_file_id": b9_env["proof_out_farmer_id"],
            },
        )
        assert pay_farmer.status_code == 201
        pay_farmer_id = pay_farmer.json()["data"]["id"]

        # FARMER forbidden on invoices, sees ONLY own Jalur C OUTBOUND on payments
        assert (await f1_c.get("/api/v1/invoices")).status_code == 403
        f1_pays = await f1_c.get("/api/v1/payments")
        assert f1_pays.status_code == 200
        assert [p["id"] for p in f1_pays.json()["data"]] == [pay_farmer_id]
        assert (await f1_c.get("/api/v1/payments?payment_direction=INBOUND")).json()["data"] == []

        # Second farmer sees 0 records
        assert (await f2_c.get("/api/v1/payments")).json()["data"] == []

        # Cooperative sees only OUTBOUND payments to its cooperative party
        coop_pays = await coop_c.get("/api/v1/payments")
        assert coop_pays.status_code == 200
        assert [p["id"] for p in coop_pays.json()["data"]] == [pay_coop_id]
        assert (await coop_c.get("/api/v1/payments?payment_direction=INBOUND")).json()["data"] == []

        # Global roles see separate AR & AP lists cleanly
        ar_list = (await fin1.get("/api/v1/invoices?invoice_type=ACCOUNTS_RECEIVABLE")).json()[
            "data"
        ]
        ap_list = (await fin1.get("/api/v1/invoices?invoice_type=ACCOUNTS_PAYABLE")).json()["data"]
        assert all(i["invoice_type"] == "ACCOUNTS_RECEIVABLE" for i in ar_list)
        assert all(i["invoice_type"] == "ACCOUNTS_PAYABLE" for i in ap_list)
        assert UUID(ar_id) == UUID(ar_id)
    finally:
        for client in (fin1, fin2, dir_c, ops_c, pks_c, coop_c, f1_c, f2_c, sys_c):
            await client.aclose()
