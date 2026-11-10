"""B11 end-to-end contract conformance, full 95-op parity, negative catalog, load & EXPLAIN."""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
import yaml
from app.core.config import Settings
from app.core.database import build_async_engine, build_session_factory, dispose_database
from app.core.exceptions import ERROR_CATALOG_DEFAULTS, ErrorCode
from app.core.system_rules import seed_baseline_system_rules
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
    MillCompanyModel,
    PartyModel,
)
from app.modules.pricing.infrastructure.models import (
    deterministic_category_id,
    deterministic_source_id,
    seed_pricing_catalog,
)
from redis.asyncio import Redis
from sqlalchemy import text

REPO_ROOT = Path(__file__).resolve().parents[3]
CONTRACTS_DIR = REPO_ROOT / "contracts"


async def _login(
    transport: httpx.ASGITransport, *, username: str, password: str
) -> tuple[httpx.AsyncClient, str]:
    c = httpx.AsyncClient(transport=transport, base_url="http://testserver")
    resp = await c.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    csrf = (await c.get("/api/v1/auth/csrf")).json()["data"]["csrf_token"]
    return c, csrf


def test_b11_openapi_95_operations_and_error_catalog_parity() -> None:
    openapi_spec = yaml.safe_load((CONTRACTS_DIR / "openapi.v1.yaml").read_text(encoding="utf-8"))
    error_spec = yaml.safe_load((CONTRACTS_DIR / "error-catalog.yaml").read_text(encoding="utf-8"))
    scenarios = json.loads(
        (CONTRACTS_DIR / "fixtures" / "error-scenarios.json").read_text(encoding="utf-8")
    )["scenarios"]

    app = create_app()
    fastapi_spec = app.openapi()

    expected_ops: dict[tuple[str, str], dict] = {}
    for path, item in openapi_spec["paths"].items():
        for method, op in item.items():
            if method.lower() in {"get", "post", "put", "patch", "delete"}:
                expected_ops[(path, method.upper())] = op

    actual_ops: dict[tuple[str, str], dict] = {}
    for path, item in fastapi_spec["paths"].items():
        for method, op in item.items():
            if method.lower() in {"get", "post", "put", "patch", "delete"}:
                actual_ops[(path, method.upper())] = op

    assert len(expected_ops) == 95
    assert set(actual_ops.keys()) == set(expected_ops.keys())

    # Every x-idempotency-required operation in OpenAPI must expose Idempotency-Key header
    for key, op in expected_ops.items():
        if op.get("x-idempotency-required"):
            params = actual_ops[key].get("parameters", [])
            header_names = {p["name"].lower() for p in params if p.get("in") == "header"}
            assert "idempotency-key" in header_names, f"Missing Idempotency-Key on {key}"

    # Canonical error-catalog parity
    catalog_entries = error_spec.get("errors", [])
    assert len(catalog_entries) > 0
    for entry in catalog_entries:
        code = ErrorCode(entry["code"])
        assert ERROR_CATALOG_DEFAULTS[code][0] == int(entry["http_status"])

    # Every negative scenario in error-scenarios.json resolves cleanly to catalog & HTTP status
    for sc in scenarios:
        err_code = ErrorCode(sc["error_response"]["error"]["code"])
        assert ERROR_CATALOG_DEFAULTS[err_code][0] == int(sc["expected_http_status"])


@pytest.fixture
async def b11_env(test_db_url: str | None, test_redis_url: str | None) -> AsyncIterator[dict]:
    assert test_db_url and test_redis_url
    assert test_redis_url.endswith("/1")

    cfg = Settings(LOG_JSON=False)
    engine = build_async_engine(cfg, dsn_override=test_db_url)
    sf = build_session_factory(engine)
    redis_client = Redis.from_url(test_redis_url, decode_responses=True)
    await redis_client.flushdb()

    now = datetime.now(UTC)
    hasher = Argon2PasswordHasher()
    pw_hash = await hasher.hash_password("E2ePass#2026")

    p_perumda, p_coop, p_mc = uuid4(), uuid4(), uuid4()
    coop_id, mc_id = uuid4(), uuid4()

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
                    "trade_contracts, price_verification_events, mill_price_quotes, "
                    "disbun_reference_prices, price_categories, price_sources, "
                    "public_notices, public_pages, "
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
                (p_coop, "COOPERATIVE", "KUD E2E"),
                (p_mc, "MILL_COMPANY", "PT Sawit E2E"),
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
                    cooperative_code="KOP-E2E",
                    cooperative_name="KUD E2E",
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
                    company_code="MC-E2E",
                    company_name="PT Sawit E2E",
                    contact_phone="0761000",
                    address="Pekanbaru",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()

            actors = (
                ("ops_1_e2e", RoleCode.PERUMDA_OPERATIONS, ScopeType.PERUMDA_GLOBAL, None),
                ("ops_2_e2e", RoleCode.PERUMDA_OPERATIONS, ScopeType.PERUMDA_GLOBAL, None),
                ("fin_1_e2e", RoleCode.PERUMDA_FINANCE, ScopeType.PERUMDA_GLOBAL, None),
                ("fin_2_e2e", RoleCode.PERUMDA_FINANCE, ScopeType.PERUMDA_GLOBAL, None),
                ("dir_e2e", RoleCode.DIRECTOR, ScopeType.PERUMDA_GLOBAL, None),
                ("coop_e2e", RoleCode.COOPERATIVE_OPERATOR, ScopeType.COOPERATIVE, coop_id),
                ("sys_e2e", RoleCode.SYSTEM_ADMIN, ScopeType.PERUMDA_GLOBAL, None),
            )
            for uname, role, stype, cid in actors:
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
                        farmer_id=None,
                        cooperative_id=cid,
                        mill_id=None,
                        granted_by=None,
                        created_at=now,
                        revoked_at=None,
                    )
                )

    app = create_app(settings=cfg, db_dsn_override=test_db_url, redis_url_override=test_redis_url)
    async with app.router.lifespan_context(app):
        yield {
            "app": app,
            "engine": engine,
            "sf": sf,
            "now": now,
            "p_perumda": str(p_perumda),
            "p_coop": str(p_coop),
            "p_mc": str(p_mc),
            "coop_id": str(coop_id),
            "mc_id": str(mc_id),
        }

    await redis_client.aclose()
    await dispose_database(engine)


@pytest.mark.asyncio
async def test_b11_full_e2e_supply_chain_and_security_headers(b11_env: dict) -> None:
    transport = httpx.ASGITransport(app=b11_env["app"])
    anon = httpx.AsyncClient(transport=transport, base_url="http://testserver")

    # NEG-01 unauthenticated private endpoint rejected + security headers present
    neg01 = await anon.get("/api/v1/farmers")
    assert neg01.status_code == 401
    assert neg01.json()["error"]["code"] == "AUTH_REQUIRED"
    assert neg01.headers["X-Content-Type-Options"] == "nosniff"
    assert neg01.headers["X-Frame-Options"] == "DENY"
    assert neg01.headers["Cache-Control"] == "no-store"

    # NEG-20 invalid credentials rejected with 401
    neg20 = await anon.post(
        "/api/v1/auth/login", json={"username": "ops_1_e2e", "password": "WrongPassword!"}
    )
    assert neg20.status_code == 401
    assert neg20.json()["error"]["code"] == "AUTH_INVALID_CREDENTIALS"

    # Public Portal reachable anonymously
    pub_prices = await anon.get("/api/v1/public/prices")
    assert pub_prices.status_code == 200

    ops1, c_ops1 = await _login(transport, username="ops_1_e2e", password="E2ePass#2026")
    ops2, c_ops2 = await _login(transport, username="ops_2_e2e", password="E2ePass#2026")
    fin1, c_fin1 = await _login(transport, username="fin_1_e2e", password="E2ePass#2026")
    fin2, c_fin2 = await _login(transport, username="fin_2_e2e", password="E2ePass#2026")
    dir_c, c_dir = await _login(transport, username="dir_e2e", password="E2ePass#2026")
    coop_c, c_coop = await _login(transport, username="coop_e2e", password="E2ePass#2026")
    sys_c, c_sys = await _login(transport, username="sys_e2e", password="E2ePass#2026")

    try:
        # NEG-15 invalid CSRF blocked
        bad_csrf = await ops1.post(
            "/api/v1/prices",
            headers={"X-CSRF-Token": "invalid-csrf-token"},
            json={},
        )
        assert bad_csrf.status_code == 403
        assert bad_csrf.json()["error"]["code"] == "AUTH_CSRF_INVALID"

        # Master Data: Farmer, Farm, Mill, Vehicle, Driver
        farmer = (
            await coop_c.post(
                "/api/v1/farmers",
                headers={"X-CSRF-Token": c_coop},
                json={
                    "farmer_code": "FRM-E2E-1",
                    "full_name": "Petani E2E",
                    "contact_phone": "0813111222",
                    "cooperative_id": b11_env["coop_id"],
                },
            )
        ).json()["data"]
        farm_bad = await coop_c.post(
            "/api/v1/farms",
            headers={"X-CSRF-Token": c_coop},
            json={
                "farmer_id": farmer["id"],
                "farm_code": "KBN-E2E-1",
                "farm_name": "Kebun E2E",
                "area_hectares": "2.5000",
                "village": "Makmur",
                "district": "Kerinci",
                "latitude": "0.402100",
                "longitude": None,
            },
        )
        assert farm_bad.status_code == 422
        assert farm_bad.json()["error"]["code"] == "VAL_INVALID_COORDINATES"

        farm = (
            await coop_c.post(
                "/api/v1/farms",
                headers={"X-CSRF-Token": c_coop},
                json={
                    "farmer_id": farmer["id"],
                    "farm_code": "KBN-E2E-1",
                    "farm_name": "Kebun E2E",
                    "area_hectares": "2.5000",
                    "village": "Makmur",
                    "district": "Kerinci",
                    "latitude": "0.402100",
                    "longitude": "101.860400",
                },
            )
        ).json()["data"]
        mill = (
            await ops1.post(
                "/api/v1/mills",
                headers={"X-CSRF-Token": c_ops1},
                json={
                    "mill_company_id": b11_env["mc_id"],
                    "mill_code": "PKS-E2E-1",
                    "mill_name": "PKS E2E Pelalawan",
                    "address": "Pelalawan",
                    "district": "Kerinci",
                    "regency": "Pelalawan",
                    "province": "Riau",
                    "latitude": "0.405000",
                    "longitude": "101.865000",
                    "contact_phone": "07611234",
                    "partnership_status": "ACTIVE",
                    "is_public": True,
                },
            )
        ).json()["data"]
        veh = (
            await ops1.post(
                "/api/v1/vehicles",
                headers={"X-CSRF-Token": c_ops1},
                json={
                    "plate_number": "BM 1111 E2E",
                    "vehicle_type": "TRUCK",
                    "nominal_capacity_kg": "15000.000",
                },
            )
        ).json()["data"]
        drv = (
            await ops1.post(
                "/api/v1/drivers",
                headers={"X-CSRF-Token": c_ops1},
                json={
                    "full_name": "Sopir E2E",
                    "contact_phone": "0812333444",
                    "driver_reference": "SIM-E2E-01",
                },
            )
        ).json()["data"]

        # Create MILL_OPERATOR bound to this mill via admin user management endpoint
        pks_user_resp = await sys_c.post(
            "/api/v1/admin/users",
            headers={"X-CSRF-Token": c_sys},
            json={
                "username": "pks_e2e_op",
                "password": "PksPass#2026",
                "role_code": "MILL_OPERATOR",
                "scope_type": "MILL",
                "mill_id": mill["id"],
            },
        )
        assert pks_user_resp.status_code == 201
        pks_c, c_pks = await _login(transport, username="pks_e2e_op", password="PksPass#2026")

        # Pricing SM-01 -> public portal visible
        now = b11_env["now"]
        price_draft = (
            await ops1.post(
                "/api/v1/prices",
                headers={"X-CSRF-Token": c_ops1},
                json={
                    "mill_id": mill["id"],
                    "price_category_id": str(deterministic_category_id("SWADAYA_STD")),
                    "source_id": str(deterministic_source_id("MILL_OFFICIAL")),
                    "price_per_kg": "2850.00",
                    "effective_from": (now - timedelta(hours=1)).isoformat(),
                    "effective_until": (now + timedelta(days=5)).isoformat(),
                },
            )
        ).json()["data"]
        assert (
            await ops1.post(
                f"/api/v1/prices/{price_draft['id']}/submit", headers={"X-CSRF-Token": c_ops1}
            )
        ).status_code == 200
        assert (
            await ops2.post(
                f"/api/v1/prices/{price_draft['id']}/verify",
                headers={"X-CSRF-Token": c_ops2},
                json={"decision": "APPROVE"},
            )
        ).status_code == 200
        assert (
            await ops1.post(
                f"/api/v1/prices/{price_draft['id']}/publish", headers={"X-CSRF-Token": c_ops1}
            )
        ).status_code == 200
        pub_after = await anon.get("/api/v1/public/prices")
        assert pub_after.status_code == 200
        assert any(p["id"] == price_draft["id"] for p in pub_after.json()["data"])

        # TBS Receiving SM-02 + weighing + validate
        rcp = (
            await coop_c.post(
                "/api/v1/receipts",
                headers={"X-CSRF-Token": c_coop, "Idempotency-Key": str(uuid4())},
                json={
                    "farmer_id": farmer["id"],
                    "farm_id": farm["id"],
                    "received_at": now.isoformat(),
                },
            )
        ).json()["data"]
        assert (
            await coop_c.post(
                f"/api/v1/receipts/{rcp['id']}/weighing",
                headers={"X-CSRF-Token": c_coop},
                json={
                    "gross_weight_kg": "12000.000",
                    "tare_weight_kg": "2000.000",
                    "version": rcp["version"],
                },
            )
        ).status_code == 200
        assert (
            await coop_c.post(
                f"/api/v1/receipts/{rcp['id']}/validate",
                headers={"X-CSRF-Token": c_coop},
            )
        ).status_code == 200

        # Contract & Quota
        ctr = (
            await ops1.post(
                "/api/v1/contracts",
                headers={"X-CSRF-Token": c_ops1},
                json={
                    "mill_id": mill["id"],
                    "contract_number": "KTR-E2E-001",
                    "start_date": now.date().isoformat(),
                    "end_date": (now.date() + timedelta(days=30)).isoformat(),
                    "price_rule_type": "FIXED",
                    "agreed_price_per_kg": "2850.00",
                    "business_model_code": "PRINCIPAL",
                    "perumda_role": "SELLER",
                    "seller_party_id": b11_env["p_perumda"],
                    "buyer_party_id": b11_env["p_mc"],
                    "payment_terms": "14 hari",
                    "initial_quota_kg": "20000.000",
                },
            )
        ).json()["data"]
        assert (
            await dir_c.post(
                f"/api/v1/contracts/{ctr['id']}/approve",
                headers={"X-CSRF-Token": c_dir},
            )
        ).status_code == 200

        # Logistics e-DO SM-05 -> QR arrival
        do = (
            await coop_c.post(
                "/api/v1/delivery-orders",
                headers={"X-CSRF-Token": c_coop},
                json={
                    "mill_id": mill["id"],
                    "contract_id": ctr["id"],
                    "vehicle_id": veh["id"],
                    "driver_id": drv["id"],
                    "receipt_ids": [rcp["id"]],
                },
            )
        ).json()["data"]
        do_issued = (
            await coop_c.post(
                f"/api/v1/delivery-orders/{do['id']}/issue",
                headers={"X-CSRF-Token": c_coop, "Idempotency-Key": str(uuid4())},
                json={"version": do["version"], "confirm_lock_allocations": True},
            )
        ).json()["data"]
        in_transit = await coop_c.post(
            f"/api/v1/delivery-orders/{do['id']}/status",
            headers={"X-CSRF-Token": c_coop},
            json={"target_status": "IN_TRANSIT", "version": do_issued["version"]},
        )
        assert in_transit.status_code == 200
        qr_res = await pks_c.post(
            "/api/v1/delivery-orders/verify-qr",
            headers={"X-CSRF-Token": c_pks},
            json={"qr_token_or_edo_number": do_issued["qr_verification_token"]},
        )
        assert qr_res.status_code == 200
        assert qr_res.json()["data"]["status"] == "ARRIVED"

        # Evidence upload + Mill Weighing SM-06 verify -> RECEIVED
        png_bytes = b"\x89PNG\r\n\x1a\n" + b"0" * 64
        proof = (
            await pks_c.post(
                "/api/v1/files",
                headers={"X-CSRF-Token": c_pks},
                data={"classification": "MILL_TICKET_PROOF"},
                files={"file": ("wb-e2e.png", png_bytes, "image/png")},
            )
        ).json()["data"]
        tkt = (
            await pks_c.post(
                "/api/v1/mill-tickets",
                headers={"X-CSRF-Token": c_pks, "Idempotency-Key": str(uuid4())},
                json={
                    "delivery_order_id": do["id"],
                    "ticket_number": "WB-E2E-001",
                    "gross_weight_kg": "14900.000",
                    "tare_weight_kg": "5000.000",
                    "weighed_at": now.isoformat(),
                    "proof_file_id": proof["id"],
                    "grading_items": [],
                },
            )
        ).json()["data"]
        assert (
            await pks_c.post(
                f"/api/v1/mill-tickets/{tkt['id']}/verify",
                headers={"X-CSRF-Token": c_pks},
            )
        ).status_code == 200

        # Reconciliation SM-07 -> MATCHED -> simulation allocations
        rec_case = (
            await ops1.post(
                "/api/v1/reconciliations",
                headers={"X-CSRF-Token": c_ops1, "Idempotency-Key": str(uuid4())},
                json={"delivery_order_id": do["id"]},
            )
        ).json()["data"]
        assert rec_case["status"] == "MATCHED"
        assert (
            await ops1.post(
                f"/api/v1/reconciliations/{rec_case['id']}/allocations",
                headers={"X-CSRF-Token": c_ops1},
                json={
                    "mode": "SIMULATION",
                    "allocation_policy_version_id": rec_case["rule_version_id"],
                },
            )
        ).status_code == 200

        # Finance AR Invoice -> Verify (SOD-04) -> Issue -> INBOUND Payment -> Verify (SOD-06) -> PAID
        ar_inv = (
            await fin1.post(
                "/api/v1/invoices",
                headers={"X-CSRF-Token": c_fin1},
                json={
                    "invoice_type": "ACCOUNTS_RECEIVABLE",
                    "creditor_party_id": b11_env["p_perumda"],
                    "debtor_party_id": b11_env["p_mc"],
                    "reconciliation_case_id": rec_case["id"],
                    "invoice_date": now.date().isoformat(),
                },
            )
        ).json()["data"]
        assert (
            await fin2.post(
                f"/api/v1/invoices/{ar_inv['id']}/verify",
                headers={"X-CSRF-Token": c_fin2},
                json={"decision": "APPROVE"},
            )
        ).status_code == 200
        assert (
            await fin1.post(
                f"/api/v1/invoices/{ar_inv['id']}/issue",
                headers={"X-CSRF-Token": c_fin1},
            )
        ).status_code == 200

        # NEG-04 SYSTEM_ADMIN blocked on payment approve
        assert (
            await sys_c.post(
                f"/api/v1/payments/{ar_inv['id']}/approve",
                headers={"X-CSRF-Token": c_sys, "Idempotency-Key": str(uuid4())},
                json={"decision": "APPROVED", "reason": "Admin dilarang BR-SYS-002"},
            )
        ).status_code == 403

        pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
        pay_proof = (
            await fin1.post(
                "/api/v1/files",
                headers={"X-CSRF-Token": c_fin1},
                data={"classification": "PAYMENT_PROOF"},
                files={"file": ("pay-e2e.pdf", pdf_bytes, "application/pdf")},
            )
        ).json()["data"]
        pay = (
            await fin1.post(
                "/api/v1/payments",
                headers={"X-CSRF-Token": c_fin1, "Idempotency-Key": str(uuid4())},
                json={
                    "invoice_id": ar_inv["id"],
                    "payment_direction": "INBOUND",
                    "payer_party_id": b11_env["p_mc"],
                    "payee_party_id": b11_env["p_perumda"],
                    "amount": "28215000.00",
                    "payment_date": now.date().isoformat(),
                    "payment_method": "BANK_TRANSFER_MANUAL",
                    "payment_reference": "TRF-E2E-AR-001",
                    "proof_file_id": pay_proof["id"],
                },
            )
        ).json()["data"]
        assert (
            await fin2.post(
                f"/api/v1/payments/{pay['id']}/verify",
                headers={"X-CSRF-Token": c_fin2},
                json={"decision": "VERIFIED"},
            )
        ).status_code == 200

        # Reporting & Admin Observability endpoints verify E2E data coherently
        fin_rep = await fin1.get("/api/v1/reports/finance")
        assert fin_rep.status_code == 200
        assert fin_rep.json()["data"]["ar_cash_collected_total"] == "28215000.00"
        assert fin_rep.json()["data"]["is_net_profit"] is False

        audit_log = await dir_c.get("/api/v1/admin/audit-events?page=1&page_size=20")
        assert audit_log.status_code == 200
        assert len(audit_log.json()["data"]) >= 5

        sys_health = await sys_c.get("/api/v1/admin/system-health")
        assert sys_health.status_code == 200
        assert sys_health.json()["data"]["health"]["status"] == "ok"
        await pks_c.aclose()
    finally:
        for c in (anon, ops1, ops2, fin1, fin2, dir_c, coop_c, sys_c):
            await c.aclose()


@pytest.mark.asyncio
async def test_b11_concurrent_load_and_postgresql_explain_analyze(b11_env: dict) -> None:
    transport = httpx.ASGITransport(app=b11_env["app"])
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as anon:
        # Warm cache once then execute 50 concurrent read requests across core endpoints
        assert (await anon.get("/api/v1/public/prices")).status_code == 200
        started = time.perf_counter()
        responses = await asyncio.gather(
            *[
                anon.get(
                    "/api/v1/public/prices"
                    if i % 3 == 0
                    else ("/api/v1/public/mills" if i % 3 == 1 else "/health/ready")
                )
                for i in range(50)
            ]
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        assert all(r.status_code == 200 for r in responses)
        assert elapsed_ms < 5000.0

    # Real PostgreSQL EXPLAIN ANALYZE on priority indexed queries (DBD §20.3)
    queries = (
        "SELECT id, receipt_number, status FROM tbs_receipts WHERE status <> 'CANCELLED' ORDER BY received_at DESC LIMIT 20",
        "SELECT id, delivery_order_number, status FROM delivery_orders WHERE status = 'ISSUED' ORDER BY created_at DESC LIMIT 20",
        "SELECT id, status, calculated_at FROM reconciliation_cases WHERE is_current IS TRUE AND status = 'MATCHED'",
        "SELECT invoice_type, status, COALESCE(SUM(total_amount), 0) FROM invoices GROUP BY invoice_type, status",
        "SELECT id, event_type, occurred_at FROM audit_events ORDER BY occurred_at DESC LIMIT 20",
    )
    async with b11_env["engine"].connect() as conn:
        for q in queries:
            plan_rows = (
                await conn.execute(text(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {q}"))
            ).scalar_one()
            exec_ms = float(plan_rows[0]["Execution Time"])
            assert exec_ms < 250.0
