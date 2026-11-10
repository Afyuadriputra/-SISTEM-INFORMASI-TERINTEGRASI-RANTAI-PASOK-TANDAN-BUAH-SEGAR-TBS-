"""PostgreSQL integration tests for Contracts SM-03, SOD-02, Quota Concurrency & Release (B5)."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import httpx
import pytest
from app.core.config import Settings
from app.core.database import build_async_engine, build_session_factory, dispose_database
from app.core.system_rules import seed_baseline_system_rules
from app.main import create_app
from app.modules.contracts.infrastructure.models import QuotaReservationModel
from app.modules.contracts.infrastructure.quota_ops import (
    consume_quota_reservation_in_tx,
    release_quota_reservation_in_tx,
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
async def b5_env(test_db_url: str | None, test_redis_url: str | None) -> AsyncIterator[dict]:
    assert test_db_url and test_redis_url
    assert test_redis_url.endswith("/1")

    cfg = Settings(LOG_JSON=False)
    engine = build_async_engine(cfg, dsn_override=test_db_url)
    sf = build_session_factory(engine)
    redis_client = Redis.from_url(test_redis_url, decode_responses=True)

    now = datetime.now(UTC)
    hasher = Argon2PasswordHasher()
    pw_hash = await hasher.hash_password("ContractPass#2026")

    p_perumda, p_mc, p_coop = uuid4(), uuid4(), uuid4()
    mc_id, mill_id = uuid4(), uuid4()

    async with sf() as session:
        async with session.begin():
            await session.execute(
                text(
                    "TRUNCATE TABLE audit_events, idempotency_records, auth_sessions, "
                    "user_access_scopes, user_role_grants, user_accounts, "
                    "contract_approval_events, quota_reservations, contract_quota_periods, "
                    "trade_contracts, mills, mill_companies, parties "
                    "RESTART IDENTITY CASCADE"
                )
            )
            await seed_rbac_catalog(session)
            await seed_baseline_system_rules(session)

            for pid, ptype, pname in (
                (p_perumda, "PERUMDA", "Perumda Tuah Sekata"),
                (p_mc, "MILL_COMPANY", "PT Sawit Lestari"),
                (p_coop, "COOPERATIVE", "KUD Tani Sejahtera"),
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
                MillCompanyModel(
                    id=mc_id,
                    party_id=p_mc,
                    company_code="MC-LESTARI-01",
                    company_name="PT Sawit Lestari",
                    contact_phone="0761-889900",
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
                    mill_code="PKS-KTR-01",
                    mill_name="PKS Pangkalan Kerinci",
                    address="Pelalawan",
                    district="Pangkalan Kerinci",
                    regency="Pelalawan",
                    province="Riau",
                    latitude=Decimal("0.402100"),
                    longitude=Decimal("101.860400"),
                    contact_phone="0761-101-202",
                    partnership_status="ACTIVE",
                    is_public=True,
                    location_verified_at=now,
                    version=1,
                    created_at=now,
                    updated_at=now,
                )
            )

            actors = (
                ("ops_contract", RoleCode.PERUMDA_OPERATIONS, ScopeType.PERUMDA_GLOBAL, None),
                ("dir_approver", RoleCode.DIRECTOR, ScopeType.PERUMDA_GLOBAL, None),
                ("sys_admin", RoleCode.SYSTEM_ADMIN, ScopeType.PERUMDA_GLOBAL, None),
                ("mill_op", RoleCode.MILL_OPERATOR, ScopeType.MILL, mill_id),
            )
            for uname, role, stype, mid in actors:
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
                        cooperative_id=None,
                        mill_id=mid,
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
            "mill_id": str(mill_id),
            "p_perumda": str(p_perumda),
            "p_mc": str(p_mc),
            "p_coop": str(p_coop),
        }

    await redis_client.aclose()
    await dispose_database(engine)


async def test_b5_contract_lifecycle_privacy_sod_and_expired_block(b5_env: dict) -> None:
    transport = httpx.ASGITransport(app=b5_env["app"])
    ops, csrf_ops = await _login(transport, username="ops_contract", password="ContractPass#2026")
    director, csrf_dir = await _login(
        transport, username="dir_approver", password="ContractPass#2026"
    )
    sys_admin, csrf_adm = await _login(
        transport, username="sys_admin", password="ContractPass#2026"
    )
    mill_op, _ = await _login(transport, username="mill_op", password="ContractPass#2026")

    today = datetime.now(UTC).date()
    try:
        # 1. Invalid PRINCIPAL with represented_party_id -> 422 CONTRACT_BUSINESS_MODEL_UNCONFIRMED.
        bad_model = await ops.post(
            "/api/v1/contracts",
            json={
                "contract_number": "KTR-BAD-001",
                "mill_id": b5_env["mill_id"],
                "start_date": (today - timedelta(days=5)).isoformat(),
                "end_date": (today + timedelta(days=30)).isoformat(),
                "price_rule_type": "FIXED",
                "agreed_price_per_kg": "2850.00",
                "business_model_code": "PRINCIPAL",
                "perumda_role": "SELLER",
                "seller_party_id": b5_env["p_perumda"],
                "buyer_party_id": b5_env["p_mc"],
                "represented_party_id": b5_env["p_coop"],
                "payment_terms": "14 hari kerja",
                "initial_quota_kg": "100000.000",
            },
            headers={"X-CSRF-Token": csrf_ops},
        )
        assert bad_model.status_code == 422
        assert bad_model.json()["error"]["code"] == "CONTRACT_BUSINESS_MODEL_UNCONFIRMED"

        # 2. UNCONFIRMED contract succeeds with PENDING_SOP classification & PENDING_APPROVAL.
        unconf_resp = await ops.post(
            "/api/v1/contracts",
            json={
                "contract_number": "KTR-UNCONF-001",
                "mill_id": b5_env["mill_id"],
                "start_date": (today - timedelta(days=2)).isoformat(),
                "end_date": (today + timedelta(days=30)).isoformat(),
                "price_rule_type": "REFERENCE_FORMULA",
                "agreed_price_per_kg": None,
                "business_model_code": "UNCONFIRMED",
                "perumda_role": "UNCONFIRMED",
                "seller_party_id": b5_env["p_coop"],
                "buyer_party_id": b5_env["p_mc"],
                "payment_terms": "Menunggu SOP Principal/Agent",
                "initial_quota_kg": "20000.000",
            },
            headers={"X-CSRF-Token": csrf_ops},
        )
        assert unconf_resp.status_code == 201
        unconf_c = unconf_resp.json()["data"]
        assert unconf_c["status"] == "PENDING_APPROVAL"
        assert unconf_c["policy_classification"] == "PENDING_SOP"

        # 3. Confidentiality guard: MILL_OPERATOR / non-Perumda cannot list contracts (403).
        sec_read = await mill_op.get("/api/v1/contracts")
        assert sec_read.status_code == 403
        assert sec_read.json()["error"]["code"] == "AUTH_ACCESS_DENIED"

        # 4. SYSTEM_ADMIN cannot approve contracts (BR-SYS-002 -> AUTH_OPERATION_FORBIDDEN).
        adm_approve = await sys_admin.post(
            f"/api/v1/contracts/{unconf_c['id']}/approve",
            headers={"X-CSRF-Token": csrf_adm},
        )
        assert adm_approve.status_code == 403
        assert adm_approve.json()["error"]["code"] == "AUTH_OPERATION_FORBIDDEN"

        # 5. Cannot reserve quota while contract still PENDING_APPROVAL -> 409 CONTRACT_NOT_ACTIVE.
        unapproved_res = await ops.post(
            f"/api/v1/contracts/{unconf_c['id']}/reservations",
            json={
                "quota_period_id": unconf_c["quota_periods"][0]["id"],
                "delivery_order_id": str(uuid4()),
                "reserved_weight_kg": "5000.000",
            },
            headers={"X-CSRF-Token": csrf_ops, "Idempotency-Key": "res-unapproved-001"},
        )
        assert unapproved_res.status_code == 409
        assert unapproved_res.json()["error"]["code"] == "CONTRACT_NOT_ACTIVE"

        # 6. Expired contract (end_date yesterday) approved -> reservation fails CONTRACT_EXPIRED.
        exp_resp = await ops.post(
            "/api/v1/contracts",
            json={
                "contract_number": "KTR-EXP-001",
                "mill_id": b5_env["mill_id"],
                "start_date": (today - timedelta(days=30)).isoformat(),
                "end_date": (today - timedelta(days=1)).isoformat(),
                "price_rule_type": "FIXED",
                "agreed_price_per_kg": "2800.00",
                "business_model_code": "PRINCIPAL",
                "perumda_role": "SELLER",
                "seller_party_id": b5_env["p_perumda"],
                "buyer_party_id": b5_env["p_mc"],
                "payment_terms": "14 hari",
                "initial_quota_kg": "50000.000",
            },
            headers={"X-CSRF-Token": csrf_ops},
        )
        assert exp_resp.status_code == 201
        exp_c = exp_resp.json()["data"]
        assert (
            await director.post(
                f"/api/v1/contracts/{exp_c['id']}/approve",
                headers={"X-CSRF-Token": csrf_dir},
            )
        ).status_code == 200

        res_exp = await ops.post(
            f"/api/v1/contracts/{exp_c['id']}/reservations",
            json={
                "quota_period_id": exp_c["quota_periods"][0]["id"],
                "delivery_order_id": str(uuid4()),
                "reserved_weight_kg": "1000.000",
            },
            headers={"X-CSRF-Token": csrf_ops, "Idempotency-Key": "res-expired-001"},
        )
        assert res_exp.status_code == 409
        assert res_exp.json()["error"]["code"] == "CONTRACT_EXPIRED"
    finally:
        await ops.aclose()
        await director.aclose()
        await sys_admin.aclose()
        await mill_op.aclose()


async def test_b5_concurrent_quota_reservation_consumption_and_release(b5_env: dict) -> None:
    transport = httpx.ASGITransport(app=b5_env["app"])
    ops, csrf_ops = await _login(transport, username="ops_contract", password="ContractPass#2026")
    director, csrf_dir = await _login(
        transport, username="dir_approver", password="ContractPass#2026"
    )
    today = datetime.now(UTC).date()

    try:
        create_resp = await ops.post(
            "/api/v1/contracts",
            json={
                "contract_number": "KTR-AGRO-2026-001",
                "mill_id": b5_env["mill_id"],
                "start_date": date(today.year, 1, 1).isoformat(),
                "end_date": (today + timedelta(days=45)).isoformat(),
                "price_rule_type": "FIXED",
                "agreed_price_per_kg": "2850.00",
                "business_model_code": "PRINCIPAL",
                "perumda_role": "SELLER",
                "seller_party_id": b5_env["p_perumda"],
                "buyer_party_id": b5_env["p_mc"],
                "payment_terms": "14 hari kerja (Simulasi)",
                "initial_quota_kg": "100000.000",
            },
            headers={"X-CSRF-Token": csrf_ops},
        )
        assert create_resp.status_code == 201
        c_data = create_resp.json()["data"]
        c_id = c_data["id"]
        qp_id = c_data["quota_periods"][0]["id"]

        # Activate via Director.
        app_resp = await director.post(
            f"/api/v1/contracts/{c_id}/approve",
            headers={"X-CSRF-Token": csrf_dir},
        )
        assert app_resp.status_code == 200
        assert app_resp.json()["data"]["status"] == "ACTIVE"

        # Seed 3 valid delivery_orders rows satisfying FK quota_reservations.delivery_order_id.
        do_seed, do_a, do_b = uuid4(), uuid4(), uuid4()
        now_dt = datetime.now(UTC)
        async with b5_env["sf"]() as session:
            async with session.begin():
                coop_id, veh_id, drv_id = uuid4(), uuid4(), uuid4()
                session.add(
                    CooperativeModel(
                        id=coop_id,
                        party_id=UUID(b5_env["p_coop"]),
                        cooperative_code="KOP-B5-DO",
                        cooperative_name="KUD B5",
                        address="Pelalawan",
                        contact_phone="0812000",
                        status="ACTIVE",
                        created_at=now_dt,
                        updated_at=now_dt,
                    )
                )
                session.add(
                    VehicleModel(
                        id=veh_id,
                        plate_number="BM 5555 KQ",
                        vehicle_type="TRUCK",
                        nominal_capacity_kg=Decimal("10000.000"),
                        status="ACTIVE",
                        created_at=now_dt,
                        updated_at=now_dt,
                    )
                )
                session.add(
                    DriverModel(
                        id=drv_id,
                        full_name="Sopir B5",
                        contact_phone="0812999",
                        driver_reference="SIM-B5",
                        status="ACTIVE",
                        created_at=now_dt,
                        updated_at=now_dt,
                    )
                )
                await session.flush()
                actor_creator = (
                    await session.execute(
                        text("SELECT created_by FROM trade_contracts WHERE id = :cid"),
                        {"cid": UUID(c_id)},
                    )
                ).scalar_one()
                for idx, do_uuid in enumerate((do_seed, do_a, do_b), start=1):
                    session.add(
                        DeliveryOrderModel(
                            id=do_uuid,
                            delivery_order_number=f"EDO-B5-SEED-{idx}",
                            cooperative_id=coop_id,
                            mill_id=UUID(b5_env["mill_id"]),
                            contract_id=UUID(c_id),
                            vehicle_id=veh_id,
                            driver_id=drv_id,
                            total_origin_weight_kg=Decimal("10000.000"),
                            status="DRAFT",
                            issued_at=None,
                            departed_at=None,
                            arrived_at=None,
                            completed_at=None,
                            qr_verification_token=None,
                            qr_reference_hash=None,
                            created_by=actor_creator,
                            version=1,
                            created_at=now_dt,
                            updated_at=now_dt,
                        )
                    )

        # Seed 75,000.000 kg reserved via initial call so available = 25,000.000 kg.
        r_seed = await ops.post(
            f"/api/v1/contracts/{c_id}/reservations",
            json={
                "quota_period_id": qp_id,
                "delivery_order_id": str(do_seed),
                "reserved_weight_kg": "75000.000",
            },
            headers={"X-CSRF-Token": csrf_ops, "Idempotency-Key": "res-seed-75t"},
        )
        assert r_seed.status_code == 201

        # Two parallel requests each asking 20,000.000 kg against 25,000.000 available!
        resp_a, resp_b = await asyncio.gather(
            ops.post(
                f"/api/v1/contracts/{c_id}/reservations",
                json={
                    "quota_period_id": qp_id,
                    "delivery_order_id": str(do_a),
                    "reserved_weight_kg": "20000.000",
                },
                headers={"X-CSRF-Token": csrf_ops, "Idempotency-Key": "race-quota-req-a"},
            ),
            ops.post(
                f"/api/v1/contracts/{c_id}/reservations",
                json={
                    "quota_period_id": qp_id,
                    "delivery_order_id": str(do_b),
                    "reserved_weight_kg": "20000.000",
                },
                headers={"X-CSRF-Token": csrf_ops, "Idempotency-Key": "race-quota-req-b"},
            ),
        )
        codes = sorted([resp_a.status_code, resp_b.status_code])
        assert codes == [201, 409]
        loser = resp_a if resp_a.status_code == 409 else resp_b
        winner = resp_a if resp_a.status_code == 201 else resp_b
        winner_key = "race-quota-req-a" if resp_a.status_code == 201 else "race-quota-req-b"
        winner_do = str(do_a) if resp_a.status_code == 201 else str(do_b)
        assert loser.json()["error"]["code"] == "CONTRACT_QUOTA_EXCEEDED"

        # Verify total active reserved never exceeded 100,000 kg (75k + 20k = 95k).
        q_status = await ops.get(f"/api/v1/contracts/{c_id}/quota")
        assert q_status.status_code == 200
        qp_dto = q_status.json()["data"][0]
        assert qp_dto["active_reserved_kg"] == "95000.000"
        assert qp_dto["available_quota_kg"] == "5000.000"

        # Replay winner's Idempotency-Key returns same reservation without duplicating reserve.
        replay = await ops.post(
            f"/api/v1/contracts/{c_id}/reservations",
            json={
                "quota_period_id": qp_id,
                "delivery_order_id": winner_do,
                "reserved_weight_kg": "20000.000",
            },
            headers={"X-CSRF-Token": csrf_ops, "Idempotency-Key": winner_key},
        )
        assert replay.status_code == 201
        assert replay.json()["meta"]["idempotency_replayed"] is True
        assert replay.json()["data"]["id"] == winner.json()["data"]["id"]

        # Test consumption + double-consumption prevention + quota release.
        actor_uuid = uuid4()
        async with b5_env["sf"]() as session:
            async with session.begin():
                # Insert dummy actor reference using existing dir user id from contract approved_by.
                actor_uuid = UUID(app_resp.json()["data"]["approved_by"])
                await consume_quota_reservation_in_tx(
                    session,
                    delivery_order_id=UUID(winner_do),
                    consumed_weight_kg=Decimal("19800.000"),
                    actor_id=actor_uuid,
                )

        # Second consumption of the same DO raises CONTRACT_CONCURRENT_CONFLICT.
        from app.core.exceptions import AppError as CoreAppError

        async with b5_env["sf"]() as session:
            async with session.begin():
                with pytest.raises(CoreAppError) as exc_dbl:
                    await consume_quota_reservation_in_tx(
                        session,
                        delivery_order_id=UUID(winner_do),
                        consumed_weight_kg=Decimal("19800.000"),
                        actor_id=actor_uuid,
                    )
                assert exc_dbl.value.code.value == "CONTRACT_CONCURRENT_CONFLICT"

        # Release initial 75,000 kg reservation -> available increases by 75,000 kg!
        async with b5_env["sf"]() as session:
            async with session.begin():
                await release_quota_reservation_in_tx(
                    session,
                    delivery_order_id=do_seed,
                    actor_id=actor_uuid,
                    reason="Simulasi pembatalan e-DO sebelum kirim",
                )

        q_after = (await ops.get(f"/api/v1/contracts/{c_id}/quota")).json()["data"][0]
        assert q_after["consumed_weight_kg"] == "19800.000"
        assert q_after["active_reserved_kg"] == "0.000"
        assert q_after["available_quota_kg"] == "80200.000"

        async with b5_env["sf"]() as session:
            res_count = int(
                (
                    await session.execute(select(func.count()).select_from(QuotaReservationModel))
                ).scalar_one()
            )
            assert res_count == 2
    finally:
        await ops.aclose()
        await director.aclose()
