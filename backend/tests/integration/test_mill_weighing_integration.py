"""PostgreSQL integration tests for Mill Weighing, Revisions, File Upload & Quota Consume (B7)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from app.core.config import Settings
from app.core.database import build_async_engine, build_session_factory, dispose_database
from app.core.system_rules import RULE_BUSINESS_MODEL_POLICY_ID, seed_baseline_system_rules
from app.main import create_app
from app.modules.contracts.infrastructure.models import (
    ContractQuotaPeriodModel,
    QuotaReservationModel,
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
from app.modules.logistics.infrastructure.models import DeliveryOrderModel
from app.modules.master_data.infrastructure.models import (
    CooperativeModel,
    DriverModel,
    MillCompanyModel,
    MillModel,
    PartyModel,
    VehicleModel,
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
async def b7_env(
    test_db_url: str | None, test_redis_url: str | None, tmp_path: Path
) -> AsyncIterator[dict]:
    assert test_db_url and test_redis_url
    assert test_redis_url.endswith("/1")

    cfg = Settings(LOG_JSON=False, FILE_STORAGE_DIR=str(tmp_path / "evidence"))
    engine = build_async_engine(cfg, dsn_override=test_db_url)
    sf = build_session_factory(engine)
    redis_client = Redis.from_url(test_redis_url, decode_responses=True)

    now = datetime.now(UTC)
    hasher = Argon2PasswordHasher()
    pw_hash = await hasher.hash_password("MillPass#2026")

    p_perumda, p_mc, p_coop_a, p_coop_b = uuid4(), uuid4(), uuid4(), uuid4()
    mc_id, mill_a_id, mill_b_id, coop_a_id, coop_b_id = uuid4(), uuid4(), uuid4(), uuid4(), uuid4()
    veh_id, drv_id = uuid4(), uuid4()
    contract_id, qp_id = uuid4(), uuid4()
    do_arrived_id, do_arrived_2_id, do_ready_id = uuid4(), uuid4(), uuid4()

    async with sf() as session:
        async with session.begin():
            await session.execute(
                text(
                    "TRUNCATE TABLE audit_events, idempotency_records, auth_sessions, "
                    "user_access_scopes, user_role_grants, user_accounts, "
                    "mill_grading_items, mill_weighing_tickets, file_assets, "
                    "delivery_status_events, delivery_order_lines, delivery_orders, "
                    "contract_approval_events, quota_reservations, contract_quota_periods, "
                    "trade_contracts, farms, cooperative_memberships, farmers, cooperatives, "
                    "mills, mill_companies, vehicles, drivers, parties RESTART IDENTITY CASCADE"
                )
            )
            await seed_rbac_catalog(session)
            await seed_baseline_system_rules(session)

            for pid, ptype, pname in (
                (p_perumda, "PERUMDA", "Perumda Tuah Sekata"),
                (p_mc, "MILL_COMPANY", "PT Sawit Lestari"),
                (p_coop_a, "COOPERATIVE", "KUD A"),
                (p_coop_b, "COOPERATIVE", "KUD B"),
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
                    id=coop_a_id,
                    party_id=p_coop_a,
                    cooperative_code="KOP-B7-A",
                    cooperative_name="KUD A",
                    address="Pelalawan",
                    contact_phone="081111",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            session.add(
                CooperativeModel(
                    id=coop_b_id,
                    party_id=p_coop_b,
                    cooperative_code="KOP-B7-B",
                    cooperative_name="KUD B",
                    address="Pelalawan",
                    contact_phone="082222",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            session.add(
                MillCompanyModel(
                    id=mc_id,
                    party_id=p_mc,
                    company_code="MC-B7-01",
                    company_name="PT Sawit Lestari",
                    contact_phone="0761111",
                    address="Pekanbaru",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()

            for mid, code, name in (
                (mill_a_id, "PKS-B7-A", "PKS A"),
                (mill_b_id, "PKS-B7-B", "PKS B"),
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
                        contact_phone="0761001",
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
                    plate_number="BM 7777 MK",
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
                    full_name="Sopir B7",
                    contact_phone="0812333",
                    driver_reference="SIM-B7",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )

            actors = (
                ("mill_a", RoleCode.MILL_OPERATOR, ScopeType.MILL, None, mill_a_id),
                ("mill_b", RoleCode.MILL_OPERATOR, ScopeType.MILL, None, mill_b_id),
                ("coop_a", RoleCode.COOPERATIVE_OPERATOR, ScopeType.COOPERATIVE, coop_a_id, None),
                ("coop_b", RoleCode.COOPERATIVE_OPERATOR, ScopeType.COOPERATIVE, coop_b_id, None),
                ("ops_b7", RoleCode.PERUMDA_OPERATIONS, ScopeType.PERUMDA_GLOBAL, None, None),
            )
            ops_uid = uuid4()
            for idx, (uname, role, stype, cid, mid) in enumerate(actors):
                uid = ops_uid if uname == "ops_b7" else uuid4()
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
                        mill_id=mid,
                        granted_by=None,
                        created_at=now,
                        revoked_at=None,
                    )
                )
                if idx == 0:
                    await session.flush()

            session.add(
                TradeContractModel(
                    id=contract_id,
                    contract_number="KTR-B7-MAIN",
                    mill_id=mill_a_id,
                    start_date=now.date() - timedelta(days=2),
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
            session.add(
                ContractQuotaPeriodModel(
                    id=qp_id,
                    contract_id=contract_id,
                    period_start=now.date() - timedelta(days=2),
                    period_end=now.date() + timedelta(days=30),
                    quota_limit_kg=Decimal("100000.000"),
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()

            for do_id, num, do_status in (
                (do_arrived_id, "EDO-B7-001", "ARRIVED"),
                (do_arrived_2_id, "EDO-B7-002", "ARRIVED"),
                (do_ready_id, "EDO-B7-003", "READY"),
            ):
                session.add(
                    DeliveryOrderModel(
                        id=do_id,
                        delivery_order_number=num,
                        cooperative_id=coop_a_id,
                        mill_id=mill_a_id,
                        contract_id=contract_id,
                        vehicle_id=veh_id,
                        driver_id=drv_id,
                        total_origin_weight_kg=Decimal("10000.000"),
                        status=do_status,
                        issued_at=now,
                        departed_at=now if do_status == "ARRIVED" else None,
                        arrived_at=now if do_status == "ARRIVED" else None,
                        completed_at=None,
                        qr_verification_token=f"QR-{num}",
                        qr_reference_hash=f"HASH-{num}",
                        created_by=ops_uid,
                        version=3,
                        created_at=now,
                        updated_at=now,
                    )
                )
            await session.flush()
            session.add(
                QuotaReservationModel(
                    id=uuid4(),
                    quota_period_id=qp_id,
                    delivery_order_id=do_arrived_id,
                    reserved_weight_kg=Decimal("10000.000"),
                    consumed_weight_kg=Decimal("0.000"),
                    status="RESERVED",
                    reserved_at=now,
                    released_at=None,
                    consumed_at=None,
                )
            )

    await redis_client.flushdb()
    app = create_app(settings=cfg, db_dsn_override=test_db_url, redis_url_override=test_redis_url)
    async with app.router.lifespan_context(app):
        yield {
            "app": app,
            "sf": sf,
            "contract_id": str(contract_id),
            "do_arrived_id": str(do_arrived_id),
            "do_arrived_2_id": str(do_arrived_2_id),
            "do_ready_id": str(do_ready_id),
        }

    await redis_client.aclose()
    await dispose_database(engine)


async def test_b7_proof_upload_ticket_revisions_duplicates_and_verification(b7_env: dict) -> None:
    transport = httpx.ASGITransport(app=b7_env["app"])
    mill_a, csrf_ma = await _login(transport, username="mill_a", password="MillPass#2026")
    mill_b, csrf_mb = await _login(transport, username="mill_b", password="MillPass#2026")
    coop_a, _ = await _login(transport, username="coop_a", password="MillPass#2026")
    coop_b, _ = await _login(transport, username="coop_b", password="MillPass#2026")
    ops, _ = await _login(transport, username="ops_b7", password="MillPass#2026")

    try:
        # 1. Spoofed SVG masquerading as PNG -> rejected 422 VAL_INVALID_FORMAT.
        bad_file = await mill_a.post(
            "/api/v1/files",
            data={"classification": "MILL_TICKET_PROOF"},
            files={"file": ("evil.png", b"<svg onload=alert(1)>", "image/png")},
            headers={"X-CSRF-Token": csrf_ma},
        )
        assert bad_file.status_code == 422
        assert bad_file.json()["error"]["code"] == "VAL_INVALID_FORMAT"

        # 2. Valid PDF upload succeeds 201 and traverses safely normalized filename.
        pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF"
        ok_file = await mill_a.post(
            "/api/v1/files",
            data={"classification": "MILL_TICKET_PROOF"},
            files={"file": ("../../slip #9941.pdf", pdf_bytes, "application/pdf")},
            headers={"X-CSRF-Token": csrf_ma},
        )
        assert ok_file.status_code == 201
        proof_id = ok_file.json()["data"]["id"]
        assert "/" not in ok_file.json()["data"]["original_filename"]

        # Mill B cannot download Mill A's proof file -> 403 AUTH_SCOPE_FORBIDDEN.
        cross_dl = await mill_b.get(f"/api/v1/files/{proof_id}")
        assert cross_dl.status_code == 403
        assert (await mill_a.get(f"/api/v1/files/{proof_id}")).content == pdf_bytes

        # 3. Unknown e-DO -> 404; READY e-DO -> 409 MILL_EDO_NOT_ELIGIBLE; Mill B -> 403.
        assert (
            await mill_a.post(
                "/api/v1/mill-tickets",
                json={
                    "delivery_order_id": str(uuid4()),
                    "ticket_number": "WB-404",
                    "gross_weight_kg": "17000.000",
                    "tare_weight_kg": "7000.000",
                    "weighed_at": "2026-11-10T03:40:00Z",
                },
                headers={"X-CSRF-Token": csrf_ma, "Idempotency-Key": "tk-404-001"},
            )
        ).status_code == 404

        not_arrived = await mill_a.post(
            "/api/v1/mill-tickets",
            json={
                "delivery_order_id": b7_env["do_ready_id"],
                "ticket_number": "WB-READY",
                "gross_weight_kg": "17000.000",
                "tare_weight_kg": "7000.000",
                "weighed_at": "2026-11-10T03:40:00Z",
            },
            headers={"X-CSRF-Token": csrf_ma, "Idempotency-Key": "tk-ready-001"},
        )
        assert not_arrived.status_code == 409
        assert not_arrived.json()["error"]["code"] == "MILL_EDO_NOT_ELIGIBLE"

        wrong_mill = await mill_b.post(
            "/api/v1/mill-tickets",
            json={
                "delivery_order_id": b7_env["do_arrived_id"],
                "ticket_number": "WB-CROSS",
                "gross_weight_kg": "17000.000",
                "tare_weight_kg": "7000.000",
                "weighed_at": "2026-11-10T03:40:00Z",
            },
            headers={"X-CSRF-Token": csrf_mb, "Idempotency-Key": "tk-wrong-mill"},
        )
        assert wrong_mill.status_code == 403
        assert wrong_mill.json()["error"]["code"] == "MILL_EDO_MILL_MISMATCH"

        # 4. Create valid ticket rev 1 (`17340 - 7490 = 9850.000 kg`).
        t_payload = {
            "delivery_order_id": b7_env["do_arrived_id"],
            "ticket_number": "WB-PKC-2026-9941",
            "gross_weight_kg": "17340.000",
            "tare_weight_kg": "7490.000",
            "weighed_at": "2026-11-10T03:40:00Z",
            "proof_file_id": proof_id,
            "grading_items": [
                {
                    "grading_category": "Sortasi PKS (Simulasi)",
                    "deduction_type": "WEIGHT_PERCENT",
                    "deduction_value": "2.0000",
                    "calculation_basis": "MILL_NET_WEIGHT",
                    "notes": "Catatan mutu",
                }
            ],
        }
        t1_resp = await mill_a.post(
            "/api/v1/mill-tickets",
            json=t_payload,
            headers={"X-CSRF-Token": csrf_ma, "Idempotency-Key": "create-tk-001"},
        )
        assert t1_resp.status_code == 201
        t1 = t1_resp.json()["data"]
        assert t1["net_weight_kg"] == "9850.000"
        assert t1["revision_number"] == 1
        assert t1["is_current"] is True

        # Idempotent replay matches exact ticket.
        t1_replay = await mill_a.post(
            "/api/v1/mill-tickets",
            json=t_payload,
            headers={"X-CSRF-Token": csrf_ma, "Idempotency-Key": "create-tk-001"},
        )
        assert t1_replay.status_code == 201
        assert t1_replay.json()["meta"]["idempotency_replayed"] is True
        assert t1_replay.json()["data"]["id"] == t1["id"]

        # Duplicate ticket_number on second e-DO within same mill rejected 409 MILL_DUPLICATE_TICKET.
        dup_num = await mill_a.post(
            "/api/v1/mill-tickets",
            json={
                **t_payload,
                "delivery_order_id": b7_env["do_arrived_2_id"],
            },
            headers={"X-CSRF-Token": csrf_ma, "Idempotency-Key": "create-tk-dupnum"},
        )
        assert dup_num.status_code == 409
        assert dup_num.json()["error"]["code"] == "MILL_DUPLICATE_TICKET"

        # 5. Revise ticket rev 1 -> rev 2 (`net = 9900.000`), verify old row preserved is_current=false.
        rev2_resp = await mill_a.patch(
            f"/api/v1/mill-tickets/{t1['id']}",
            json={
                "gross_weight_kg": "17340.000",
                "tare_weight_kg": "7440.000",
                "proof_file_id": proof_id,
                "correction_reason": "Koreksi input tara dari slip WB-PKC-2026-9941",
            },
            headers={"X-CSRF-Token": csrf_ma},
        )
        assert rev2_resp.status_code == 200
        t2 = rev2_resp.json()["data"]
        assert t2["revision_number"] == 2
        assert t2["previous_ticket_id"] == t1["id"]
        assert t2["net_weight_kg"] == "9900.000"
        assert (await mill_a.get(f"/api/v1/mill-tickets/{t1['id']}")).json()["data"][
            "is_current"
        ] is False

        # Cross-coop isolation: Coop A reads ticket 200, Coop B blocked 403.
        assert (await coop_a.get(f"/api/v1/mill-tickets/{t2['id']}")).status_code == 200
        assert (await coop_b.get(f"/api/v1/mill-tickets/{t2['id']}")).status_code == 403

        # 6. Verify ticket -> VERIFIED, e-DO ARRIVED -> RECEIVED, quota RESERVED -> CONSUMED!
        ver_resp = await mill_a.post(
            f"/api/v1/mill-tickets/{t2['id']}/verify",
            headers={"X-CSRF-Token": csrf_ma},
        )
        assert ver_resp.status_code == 200
        assert ver_resp.json()["data"]["status"] == "VERIFIED"

        do_after = (await ops.get(f"/api/v1/delivery-orders/{b7_env['do_arrived_id']}")).json()[
            "data"
        ]
        assert do_after["status"] == "RECEIVED"

        q_after = (await ops.get(f"/api/v1/contracts/{b7_env['contract_id']}/quota")).json()[
            "data"
        ][0]
        assert q_after["consumed_weight_kg"] == "9900.000"
        assert q_after["active_reserved_kg"] == "0.000"
        assert q_after["available_quota_kg"] == "90100.000"

        # Once e-DO completed, ticket cannot be revised -> 409 MILL_TICKET_ALREADY_FINAL.
        async with b7_env["sf"]() as session:
            async with session.begin():
                await session.execute(
                    text("UPDATE delivery_orders SET status = 'COMPLETED' WHERE id = :did"),
                    {"did": b7_env["do_arrived_id"]},
                )
        final_rev = await mill_a.patch(
            f"/api/v1/mill-tickets/{t2['id']}",
            json={
                "gross_weight_kg": "17500.000",
                "tare_weight_kg": "7440.000",
                "correction_reason": "Ubah pasca selesai",
            },
            headers={"X-CSRF-Token": csrf_ma},
        )
        assert final_rev.status_code == 409
        assert final_rev.json()["error"]["code"] == "MILL_TICKET_ALREADY_FINAL"
    finally:
        await mill_a.aclose()
        await mill_b.aclose()
        await coop_a.aclose()
        await coop_b.aclose()
        await ops.aclose()
