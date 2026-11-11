"""Reproducible, idempotent Faker seeder for isolated demo database `agroniaga_demo`.

Strict safety guarantees:
- Loads config solely from `--env-file` (default: `backend/.env.demo`), never `backend/.env`.
- Aborts unless PostgreSQL DB name is `agroniaga_demo` and Redis DB index is `/2`.
- Populates ONLY when demo data is absent; re-runs never duplicate or overwrite data.
- Explicit destructive reset requires `--reset-demo --confirm-reset agroniaga_demo`.
"""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import asyncio
import json
import random
import secrets
import shutil
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import UUID, uuid5

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

if sys.platform == "win32" and isinstance(
    asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy
):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.core.audit import AuditEventModel, AuditRecordInput, append_audit_event
from app.core.config import Settings
from app.core.database import build_async_engine, build_session_factory, dispose_database
from app.core.idempotency import SqlAlchemyIdempotencySlotAdapter
from app.core.logging import request_id_ctx
from app.core.observability import ObservabilityTracker
from app.core.redis import RedisClientManager
from app.core.system_rules import (
    RULE_FARMER_ALLOCATION_POLICY_ID,
    RULE_RECONCILIATION_TOLERANCE_ID,
    SystemRuleVersionModel,
    seed_baseline_system_rules,
)
from app.modules.admin.application.use_cases import AdminGovernanceService
from app.modules.admin.infrastructure.observability_adapter import (
    CoreSystemObservabilityAdapter,
)
from app.modules.admin.infrastructure.repository import SqlAlchemyAdminRepository
from app.modules.contracts.application.use_cases import ContractsService
from app.modules.contracts.domain.entities import (
    BusinessModelCode,
    ContractStatus,
    PerumdaRoleCode,
    PolicyClassification,
    PriceRuleType,
)
from app.modules.contracts.infrastructure.models import (
    ContractApprovalEventModel,
    ContractQuotaPeriodModel,
    TradeContractModel,
)
from app.modules.contracts.infrastructure.repository import SqlAlchemyContractsRepository
from app.modules.files.application.use_cases import FilesService
from app.modules.files.domain.entities import FileClassification
from app.modules.files.infrastructure.repository import SqlAlchemyFilesRepository
from app.modules.files.infrastructure.storage import LocalEvidenceStorageAdapter
from app.modules.finance.application.use_cases import FinanceService
from app.modules.finance.domain.entities import (
    InvoiceType,
    PaymentDirection,
    PaymentMethod,
)
from app.modules.finance.infrastructure.models import (
    InvoiceModel,
    PaymentApprovalModel,
    PaymentRecordModel,
)
from app.modules.finance.infrastructure.repository import SqlAlchemyFinanceRepository
from app.modules.identity_access.domain.entities import (
    AccessScopeEntity,
    AccountStatus,
    AuthenticatedPrincipal,
    RoleCode,
    ScopeType,
)
from app.modules.identity_access.infrastructure.models import (
    UserAccessScopeModel,
    UserAccountModel,
    UserRoleGrantModel,
    deterministic_role_id,
    seed_rbac_catalog,
)
from app.modules.identity_access.infrastructure.security_adapters import Argon2PasswordHasher
from app.modules.logistics.application.use_cases import LogisticsService
from app.modules.logistics.domain.entities import DeliveryOrderStatus
from app.modules.logistics.infrastructure.models import DeliveryOrderModel
from app.modules.logistics.infrastructure.repository import SqlAlchemyLogisticsRepository
from app.modules.master_data.infrastructure.models import (
    CooperativeMembershipModel,
    CooperativeModel,
    DriverModel,
    FarmerModel,
    FarmModel,
    MillCompanyModel,
    MillModel,
    PartyModel,
    PerumdaOfficeModel,
    VehicleModel,
)
from app.modules.mill_weighing.application.use_cases import MillWeighingService
from app.modules.mill_weighing.domain.entities import MillGradingDeductionType
from app.modules.mill_weighing.domain.rules import MillGradingInput
from app.modules.mill_weighing.infrastructure.models import MillWeighingTicketModel
from app.modules.mill_weighing.infrastructure.repository import SqlAlchemyMillWeighingRepository
from app.modules.pricing.application.use_cases import PricingService
from app.modules.pricing.domain.entities import VerifyDecision
from app.modules.pricing.infrastructure.cache_adapter import RedisPublicPricingInvalidator
from app.modules.pricing.infrastructure.models import (
    DisbunReferencePriceModel,
    MillPriceQuoteModel,
    deterministic_category_id,
    deterministic_source_id,
    seed_pricing_catalog,
)
from app.modules.pricing.infrastructure.repository import SqlAlchemyPricingRepository
from app.modules.public_portal.infrastructure.models import PublicNoticeModel, PublicPageModel
from app.modules.reconciliation.application.use_cases import ReconciliationService
from app.modules.reconciliation.domain.entities import (
    AllocationMode,
    DisputeDecision,
    ReconciliationStatus,
    WeightBasis,
)
from app.modules.reconciliation.infrastructure.models import (
    FarmerSettlementAllocationModel,
    ReconciliationCaseModel,
)
from app.modules.reconciliation.infrastructure.repository import SqlAlchemyReconciliationRepository
from app.modules.tbs_receiving.application.use_cases import TbsReceivingService
from app.modules.tbs_receiving.domain.entities import GradingDeductionType
from app.modules.tbs_receiving.domain.rules import GradingInputItem
from app.modules.tbs_receiving.infrastructure.models import (
    ReceiptWeighingRevisionModel,
    TbsReceiptModel,
)
from app.modules.tbs_receiving.infrastructure.repository import SqlAlchemyTbsReceivingRepository
from faker import Faker
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

DEMO_DB_NAME = "agroniaga_demo"
DEMO_REDIS_DB = "2"
DEMO_SEED = 20261111
DEMO_NS = UUID("de000000-1111-4000-8000-202611110001")
EXPECTED_ALEMBIC_HEAD = "0011_b10_reporting_indexes"

TINY_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc\xfc\xcf\xc0\x00"
    b"\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82"
)


def demo_uuid(tag: str) -> UUID:
    """Return reproducible deterministic UUIDv5 within the demo namespace."""
    return uuid5(DEMO_NS, tag)


def _strip_quotes(raw: str) -> str:
    val = raw.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
        return val[1:-1]
    return val


def load_isolated_demo_settings(env_file: Path) -> Settings:
    """Load Settings explicitly from `.env.demo` without reading dev/test `.env`."""
    if not env_file.is_file():
        raise SystemExit(
            f"[ABORT] File konfigurasi demo tidak ditemukan: {env_file}. "
            "Jalankan .\\scripts\\demo-setup.ps1 terlebih dahulu."
        )

    parsed: dict[str, Any] = {}
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        clean_key = key.strip()
        clean_val = _strip_quotes(val)
        parsed[clean_key] = (
            json.loads(clean_val) if clean_key == "CORS_ALLOWED_ORIGINS" else clean_val
        )

    for forbidden_key in ("TEST_DATABASE_URL", "TEST_REDIS_URL"):
        parsed.pop(forbidden_key, None)

    settings = Settings(_env_file=None, **parsed)  # type: ignore[call-arg]
    dsn = settings.DATABASE_URL.get_secret_value().replace("+psycopg", "")
    db_name = urlparse(dsn).path.lstrip("/")
    redis_db = urlparse(settings.REDIS_URL.get_secret_value()).path.lstrip("/")
    if db_name != DEMO_DB_NAME:
        raise SystemExit(
            f"[ABORT] Target PostgreSQL database harus '{DEMO_DB_NAME}', bukan '{db_name}'."
        )
    if redis_db != DEMO_REDIS_DB:
        raise SystemExit(f"[ABORT] Target Redis DB harus '/{DEMO_REDIS_DB}', bukan '/{redis_db}'.")
    return settings


@dataclass(frozen=True, slots=True)
class ActorSpec:
    tag: str
    username: str
    role: RoleCode
    scope_type: ScopeType
    target_tag: str | None
    label: str
    description: str


ACTOR_SPECS: tuple[ActorSpec, ...] = (
    ActorSpec(
        "user-petani-01",
        "demo_petani_01",
        RoleCode.FARMER,
        ScopeType.FARMER,
        "farmer-001",
        "Petani Swadaya #1 (Primer)",
        "Melihat kebun, penerimaan, & pembayaran Jalur C pribadi PET-DEMO-001",
    ),
    ActorSpec(
        "user-petani-02",
        "demo_petani_02",
        RoleCode.FARMER,
        ScopeType.FARMER,
        "farmer-002",
        "Petani Swadaya #2 (Cross-Scope)",
        "Akun uji isolasi antar petani PET-DEMO-002",
    ),
    ActorSpec(
        "user-kop-01",
        "demo_kop_op_01",
        RoleCode.COOPERATIVE_OPERATOR,
        ScopeType.COOPERATIVE,
        "coop-01",
        "Operator Koperasi #1 (Pelalawan Jaya)",
        "Penerimaan TBS, grading simulasi, & e-DO untuk KOP-DEMO-01",
    ),
    ActorSpec(
        "user-kop-02",
        "demo_kop_op_02",
        RoleCode.COOPERATIVE_OPERATOR,
        ScopeType.COOPERATIVE,
        "coop-02",
        "Operator Koperasi #2 (Cross-Scope Ukui)",
        "Akun uji isolasi antar koperasi KOP-DEMO-02",
    ),
    ActorSpec(
        "user-ops-01",
        "demo_perumda_ops_01",
        RoleCode.PERUMDA_OPERATIONS,
        ScopeType.PERUMDA_GLOBAL,
        None,
        "Staf Operasional Perumda #1 (Maker)",
        "Input master PKS, draft harga, kontrak, dan trigger rekonsiliasi",
    ),
    ActorSpec(
        "user-ops-02",
        "demo_perumda_ops_02",
        RoleCode.PERUMDA_OPERATIONS,
        ScopeType.PERUMDA_GLOBAL,
        None,
        "Staf Operasional Perumda #2 (Checker)",
        "Verifikasi & publikasi harga (Maker != Checker) serta klarifikasi sengketa",
    ),
    ActorSpec(
        "user-fin-01",
        "demo_perumda_fin_01",
        RoleCode.PERUMDA_FINANCE,
        ScopeType.PERUMDA_GLOBAL,
        None,
        "Staf Keuangan Perumda #1 (Maker)",
        "Penyusunan draf faktur AR/AP & pencatatan bukti bayar simulasi",
    ),
    ActorSpec(
        "user-fin-02",
        "demo_perumda_fin_02",
        RoleCode.PERUMDA_FINANCE,
        ScopeType.PERUMDA_GLOBAL,
        None,
        "Staf Keuangan Perumda #2 (Checker)",
        "Verifikasi faktur & verifikasi akhir bukti pembayaran (Maker != Checker)",
    ),
    ActorSpec(
        "user-mill-01",
        "demo_mill_op_01",
        RoleCode.MILL_OPERATOR,
        ScopeType.MILL,
        "mill-01",
        "Petugas PKS #1 (PKS-DEMO-01)",
        "Verifikasi QR kedatangan & tiket timbang untuk PKS-DEMO-01",
    ),
    ActorSpec(
        "user-mill-02",
        "demo_mill_op_02",
        RoleCode.MILL_OPERATOR,
        ScopeType.MILL,
        "mill-02",
        "Petugas PKS #2 (Cross-Mill PKS-DEMO-02)",
        "Akun uji isolasi antar PKS (PKS-DEMO-02)",
    ),
    ActorSpec(
        "user-dir-01",
        "demo_director_01",
        RoleCode.DIRECTOR,
        ScopeType.PERUMDA_GLOBAL,
        None,
        "Direksi Perumda (Approver)",
        "Dashboard eksekutif, persetujuan kontrak, putusan sengketa, & otorisasi bayar",
    ),
    ActorSpec(
        "user-sys-01",
        "demo_sys_admin_01",
        RoleCode.SYSTEM_ADMIN,
        ScopeType.PERUMDA_GLOBAL,
        None,
        "Administrator Sistem (Non-Approver)",
        "Kelola akun/RBAC, versi aturan simulasi/draft, & CCTV Digital audit",
    ),
)

COOP_NAMES: tuple[tuple[str, str, str, str], ...] = (
    (
        "KOP-DEMO-01",
        "KUD Demo Pelalawan Sawit Jaya",
        "Jl. Lintas Timur KM 70, Pangkalan Kerinci",
        "Pelalawan",
    ),
    (
        "KOP-DEMO-02",
        "KUD Demo Ukui Tani Makmur",
        "Jl. Poros Ukui Blok C, Ukui",
        "Ukui",
    ),
    (
        "KOP-DEMO-03",
        "KUD Demo Sorek Harapan Bersama",
        "Jl. Lintas Timur KM 98, Pangkalan Kuras",
        "Pangkalan Kuras",
    ),
    (
        "KOP-DEMO-04",
        "KUD Demo Bunut Subur Mandiri",
        "Jl. Raya Bunut KM 14, Bunut",
        "Bunut",
    ),
)

MILL_SPECS: tuple[
    tuple[str, str, str, str, str, bool, Decimal | None, Decimal | None], ...
] = (
    (
        "PKS-DEMO-01",
        "PKS Demo Pangkalan Kerinci Sejahtera",
        "PT Demo Agro Pelalawan 01",
        "Pangkalan Kerinci",
        "Jl. Industri Sawit Demo Kav. 1, Pangkalan Kerinci",
        True,
        Decimal("0.415200"),
        Decimal("101.868400"),
    ),
    (
        "PKS-DEMO-02",
        "PKS Demo Langgam Jaya Lestari",
        "PT Demo Langgam Palm 02",
        "Langgam",
        "Jl. Koridor Langgam Demo KM 12, Langgam",
        True,
        Decimal("0.289100"),
        Decimal("101.732400"),
    ),
    (
        "PKS-DEMO-03",
        "PKS Demo Sorek Satu Utama",
        "PT Demo Sorek Nabati 03",
        "Pangkalan Kuras",
        "Jl. Lintas Timur Demo KM 94, Pangkalan Kuras",
        True,
        Decimal("0.154800"),
        Decimal("102.042100"),
    ),
    (
        "PKS-DEMO-04",
        "PKS Demo Ukui Mitra Mandiri",
        "PT Demo Ukui Sejahtera 04",
        "Ukui",
        "Jl. Lintas Ukui Demo Blok D, Ukui",
        True,
        None,
        None,
    ),
    (
        "PKS-DEMO-05",
        "PKS Demo Rahasia Internal",
        "PT Demo Sawit Tertutup 05",
        "Kerumutan",
        "Jalur Operasional Internal Demo KM 21, Kerumutan",
        False,
        None,
        None,
    ),
)

COOP_FARMER_QUOTAS: tuple[int, ...] = (20, 15, 15, 10)
VILLAGES_BY_COOP: tuple[tuple[str, ...], ...] = (
    ("Makmur", "Kuala Terusan", "Rantau Baru", "Delik"),
    ("Ukui Satu", "Lubuk Kembang Sari", "Air Hitam", "Silikuan Hulu"),
    ("Sorek Satu", "Kesuma", "Betung", "Beringin Indah"),
    ("Bunut", "Pangkalan Bunut", "Lubuk Mandian Gajah", "Sungai Buluh"),
)


def make_principal(
    spec: ActorSpec,
    *,
    user_id: UUID,
    target_id: UUID | None,
    linked_party_id: UUID | None,
) -> AuthenticatedPrincipal:
    """Build service-layer principal representing a seeded demo account."""
    perms_by_role: dict[RoleCode, frozenset[str]] = {
        RoleCode.FARMER: frozenset(
            {
                "auth.session.read",
                "farmers.read",
                "farms.read",
                "tbs.receipts.read",
                "payments.read",
            }
        ),
        RoleCode.COOPERATIVE_OPERATOR: frozenset(
            {
                "auth.session.read",
                "farmers.read",
                "farmers.write",
                "farms.read",
                "farms.write",
                "tbs.receipts.read",
                "tbs.receipts.create",
                "tbs.receipts.weigh",
                "tbs.receipts.validate",
                "delivery_orders.read",
                "delivery_orders.create",
                "delivery_orders.issue",
                "delivery_orders.cancel",
                "payments.read",
            }
        ),
        RoleCode.PERUMDA_OPERATIONS: frozenset(
            {
                "auth.session.read",
                "mills.read",
                "mills.write",
                "prices.read",
                "prices.create",
                "prices.verify",
                "prices.publish",
                "contracts.read",
                "contracts.create",
                "delivery_orders.read",
                "reconciliations.read",
                "reconciliations.calculate",
                "reconciliations.review",
                "files.upload",
                "reports.read",
            }
        ),
        RoleCode.PERUMDA_FINANCE: frozenset(
            {
                "auth.session.read",
                "contracts.read",
                "reconciliations.read",
                "invoices.read",
                "invoices.create",
                "invoices.verify",
                "invoices.issue",
                "payments.read",
                "payments.record",
                "payments.verify",
                "files.upload",
                "reports.read",
                "reports.finance",
            }
        ),
        RoleCode.MILL_OPERATOR: frozenset(
            {
                "auth.session.read",
                "delivery_orders.read",
                "delivery_orders.verify_qr",
                "mill_tickets.read",
                "mill_tickets.create",
                "mill_tickets.verify",
                "files.upload",
            }
        ),
        RoleCode.DIRECTOR: frozenset(
            {
                "auth.session.read",
                "contracts.read",
                "contracts.approve",
                "reconciliations.read",
                "reconciliations.resolve",
                "invoices.read",
                "payments.read",
                "payments.approve",
                "reports.read",
                "reports.finance",
                "admin.rules.create",
            }
        ),
        RoleCode.SYSTEM_ADMIN: frozenset(
            {
                "auth.session.read",
                "admin.users.read",
                "admin.users.write",
                "admin.rules.read",
                "admin.rules.create",
                "admin.audit.read",
                "admin.system.read",
            }
        ),
    }
    return AuthenticatedPrincipal(
        session_id=demo_uuid(f"session:{spec.username}"),
        user_id=user_id,
        username=spec.username,
        email=f"{spec.username}@demo.example.invalid",
        display_name=spec.label,
        linked_party_id=linked_party_id,
        status=AccountStatus.ACTIVE,
        roles=(spec.role,),
        access_scopes=(
            AccessScopeEntity(
                id=demo_uuid(f"scope:{spec.username}"),
                scope_type=spec.scope_type,
                farmer_id=target_id if spec.scope_type == ScopeType.FARMER else None,
                cooperative_id=target_id if spec.scope_type == ScopeType.COOPERATIVE else None,
                mill_id=target_id if spec.scope_type == ScopeType.MILL else None,
            ),
        ),
        permissions=perms_by_role[spec.role],
        last_login_at=None,
        non_approver_admin=spec.role == RoleCode.SYSTEM_ADMIN,
    )


async def _verify_live_db_and_alembic(engine: AsyncEngine) -> None:
    async with engine.connect() as conn:
        current_db = str((await conn.execute(text("SELECT current_database()"))).scalar_one())
        if current_db != DEMO_DB_NAME:
            raise SystemExit(f"[ABORT] PostgreSQL current_database() adalah '{current_db}'.")
        rev = (
            await conn.execute(text("SELECT version_num FROM alembic_version"))
        ).scalar_one_or_none()
        if rev != EXPECTED_ALEMBIC_HEAD:
            raise SystemExit(
                f"[ABORT] Skema Alembic harus '{EXPECTED_ALEMBIC_HEAD}', ditemukan '{rev}'. "
                "Jalankan migrasi Alembic ke agroniaga_demo terlebih dahulu."
            )


async def _already_seeded(session: AsyncSession) -> bool:
    demo_users = int(
        (
            await session.execute(
                select(func.count())
                .select_from(UserAccountModel)
                .where(UserAccountModel.username.like("demo_%"))
            )
        ).scalar_one()
    )
    receipts = int(
        (await session.execute(select(func.count()).select_from(TbsReceiptModel))).scalar_one()
    )
    mills = int((await session.execute(select(func.count()).select_from(MillModel))).scalar_one())
    return demo_users > 0 or receipts > 0 or mills > 0


async def _collect_summary(session: AsyncSession) -> dict[str, int]:
    tables: tuple[tuple[str, Any], ...] = (
        ("mill_companies", MillCompanyModel),
        ("mills", MillModel),
        ("cooperatives", CooperativeModel),
        ("farmers", FarmerModel),
        ("farms", FarmModel),
        ("vehicles", VehicleModel),
        ("drivers", DriverModel),
        ("user_accounts", UserAccountModel),
        ("mill_price_quotes", MillPriceQuoteModel),
        ("disbun_reference_prices", DisbunReferencePriceModel),
        ("trade_contracts", TradeContractModel),
        ("tbs_receipts", TbsReceiptModel),
        ("delivery_orders", DeliveryOrderModel),
        ("mill_weighing_tickets", MillWeighingTicketModel),
        ("reconciliation_cases", ReconciliationCaseModel),
        ("farmer_settlement_allocations", FarmerSettlementAllocationModel),
        ("invoices", InvoiceModel),
        ("payment_approvals", PaymentApprovalModel),
        ("payment_records", PaymentRecordModel),
        ("audit_events", AuditEventModel),
    )
    counts: dict[str, int] = {}
    for label, model in tables:
        counts[label] = int(
            (await session.execute(select(func.count()).select_from(model))).scalar_one()
        )
    return counts


async def _reset_demo_db(
    sf: async_sessionmaker[AsyncSession],
    redis_mgr: RedisClientManager,
    storage_dir: Path,
) -> None:
    async with sf() as session:
        async with session.begin():
            db_name = (await session.execute(text("SELECT current_database()"))).scalar_one()
            if db_name != DEMO_DB_NAME:
                raise SystemExit(
                    f"[ABORTED] Target koneksi aktif bukan {DEMO_DB_NAME}: {db_name!r}"
                )
            rows = (
                await session.execute(
                    text(
                        "SELECT tablename FROM pg_tables "
                        "WHERE schemaname = 'public' AND tablename <> 'alembic_version' "
                        "ORDER BY tablename"
                    )
                )
            ).scalars().all()
            if rows:
                quoted = ", ".join(f'"{name}"' for name in rows)
                await session.execute(text(f"TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE"))
    await redis_mgr.client.flushdb()

    def _clear_storage() -> None:
        if storage_dir.exists():
            shutil.rmtree(storage_dir)
        storage_dir.mkdir(parents=True, exist_ok=True)

    await asyncio.to_thread(_clear_storage)


def _write_credentials_file(cred_path: Path, *, password: str, settings: Settings) -> None:
    lines = [
        "# KREDENSIAL DEMO LOKAL (GITIGNORED — JANGAN COMMIT KE GIT)",
        f"# Generated: {datetime.now(UTC).isoformat()}",
        f"# Database Target: {DEMO_DB_NAME} | Redis Target: /{DEMO_REDIS_DB}",
        "# Aplikasi: http://localhost:5173 | API Health: http://127.0.0.1:8000/health/ready",
        "",
        f"Password Bersama Semua Akun Demo (Argon2id): {password}",
        "",
        f"{'Username':<22} | {'Role':<22} | {'Scope':<15} | Deskripsi",
        "-" * 105,
    ]
    for spec in ACTOR_SPECS:
        lines.append(
            f"{spec.username:<22} | {spec.role.value:<22} | "
            f"{spec.scope_type.value:<15} | {spec.description}"
        )
    lines.append("")
    lines.append(f"Cookie Session Name: {settings.SESSION_COOKIE_NAME}")
    cred_path.write_text("\n".join(lines), encoding="utf-8")


async def _populate_master_and_users(
    sf: async_sessionmaker[AsyncSession],
    *,
    faker: Faker,
    rng: random.Random,
    demo_password: str,
    now: datetime,
) -> dict[str, Any]:
    pw_hash = await Argon2PasswordHasher().hash_password(demo_password)
    refs: dict[str, Any] = {
        "party_perumda": demo_uuid("party-perumda"),
        "coops": [],
        "coop_parties": {},
        "farmers": [],
        "farmer_parties": {},
        "farmer_coop": {},
        "farmer_farms": {},
        "mill_companies": [],
        "mill_company_parties": {},
        "mills": [],
        "mill_to_company_party": {},
        "vehicles": [],
        "vehicle_plates": [],
        "drivers": [],
        "targets": {},
        "principals": {},
    }

    async with sf() as session:
        async with session.begin():
            await seed_rbac_catalog(session)
            await seed_baseline_system_rules(session)
            await seed_pricing_catalog(session)

            # 1. Perumda Party & 2 Public Offices
            session.add(
                PartyModel(
                    id=refs["party_perumda"],
                    party_type="PERUMDA",
                    display_name="Perumda Tuah Sekata Unit Agro Niaga (DEMO)",
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
            )
            await session.flush()

            session.add(
                PerumdaOfficeModel(
                    id=demo_uuid("office-01"),
                    party_id=refs["party_perumda"],
                    office_name="Kantor Pusat Unit Agro Niaga Demo (Pelalawan)",
                    address="Jl. Maharaja Indra Demo No. 12, Pangkalan Kerinci, Pelalawan",
                    latitude=Decimal("0.405500"),
                    longitude=Decimal("101.860100"),
                    public_contact="(0761) 493-0001",
                    is_public=True,
                    created_at=now,
                    updated_at=now,
                )
            )
            session.add(
                PerumdaOfficeModel(
                    id=demo_uuid("office-02"),
                    party_id=refs["party_perumda"],
                    office_name="Pos Koordinasi Lapangan Demo Sorek",
                    address="Jl. Lintas Timur Demo KM 95, Pangkalan Kuras, Pelalawan",
                    latitude=Decimal("0.158200"),
                    longitude=Decimal("102.039500"),
                    public_contact="(0761) 493-0002",
                    is_public=True,
                    created_at=now,
                    updated_at=now,
                )
            )

            # 2. Mill Companies (5) & Mills (5)
            for idx, (mcode, mname, cname, dist, addr, is_pub, lat, lon) in enumerate(
                MILL_SPECS, 1
            ):
                mc_party_id = demo_uuid(f"party-mc-{idx:02d}")
                mc_id = demo_uuid(f"mc-{idx:02d}")
                mill_id = demo_uuid(f"mill-{idx:02d}")
                session.add(
                    PartyModel(
                        id=mc_party_id,
                        party_type="MILL_COMPANY",
                        display_name=cname,
                        status="ACTIVE",
                        created_at=now,
                        updated_at=now,
                    )
                )
                await session.flush()
                session.add(
                    MillCompanyModel(
                        id=mc_id,
                        party_id=mc_party_id,
                        company_code=f"PT-DEMO-{idx:02d}",
                        company_name=cname,
                        contact_phone=f"0761-8800{idx:02d}",
                        address=addr,
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
                        mill_code=mcode,
                        mill_name=mname,
                        address=addr,
                        district=dist,
                        regency="Pelalawan",
                        province="Riau",
                        latitude=lat,
                        longitude=lon,
                        location_verified_at=now if lat is not None else None,
                        contact_phone=f"0761-8891{idx:02d}" if is_pub else None,
                        partnership_status="ACTIVE",
                        is_public=is_pub,
                        version=1,
                        created_at=now,
                        updated_at=now,
                    )
                )
                refs["mill_companies"].append(mc_id)
                refs["mill_company_parties"][mc_id] = mc_party_id
                refs["mills"].append(mill_id)
                refs["mill_to_company_party"][mill_id] = mc_party_id
                refs["targets"][f"mill-{idx:02d}"] = mill_id

            # 3. Cooperatives (4)
            for idx, (ccode, cname, addr, _dist) in enumerate(COOP_NAMES, 1):
                cparty_id = demo_uuid(f"party-coop-{idx:02d}")
                coop_id = demo_uuid(f"coop-{idx:02d}")
                session.add(
                    PartyModel(
                        id=cparty_id,
                        party_type="COOPERATIVE",
                        display_name=cname,
                        status="ACTIVE",
                        created_at=now,
                        updated_at=now,
                    )
                )
                await session.flush()
                session.add(
                    CooperativeModel(
                        id=coop_id,
                        party_id=cparty_id,
                        cooperative_code=ccode,
                        cooperative_name=cname,
                        address=addr,
                        contact_phone=f"0812-7000-01{idx:02d}",
                        status="ACTIVE",
                        created_at=now,
                        updated_at=now,
                    )
                )
                refs["coops"].append(coop_id)
                refs["coop_parties"][coop_id] = cparty_id
                refs["targets"][f"coop-{idx:02d}"] = coop_id

            # 4. Farmers (60), Memberships (60), Farms (75)
            farmer_idx = 0
            farm_idx = 0
            for coop_num, quota in enumerate(COOP_FARMER_QUOTAS):
                coop_id = refs["coops"][coop_num]
                district = COOP_NAMES[coop_num][3]
                villages = VILLAGES_BY_COOP[coop_num]
                for _ in range(quota):
                    farmer_idx += 1
                    f_id = demo_uuid(f"farmer-{farmer_idx:03d}")
                    fp_id = demo_uuid(f"party-farmer-{farmer_idx:03d}")
                    fcode = f"PET-DEMO-{farmer_idx:03d}"
                    full_name = f"{faker.name()} (Demo)"
                    phone_num = f"0813-65{farmer_idx:02d}-{rng.randint(1000, 9999)}"
                    session.add(
                        PartyModel(
                            id=fp_id,
                            party_type="FARMER",
                            display_name=full_name,
                            status="ACTIVE",
                            created_at=now,
                            updated_at=now,
                        )
                    )
                    await session.flush()
                    session.add(
                        FarmerModel(
                            id=f_id,
                            party_id=fp_id,
                            farmer_code=fcode,
                            full_name=full_name,
                            contact_phone=phone_num,
                            identity_reference=f"KTP-DEMO-{farmer_idx:04d}",
                            status="ACTIVE",
                            version=1,
                            created_at=now,
                            updated_at=now,
                        )
                    )
                    await session.flush()
                    session.add(
                        CooperativeMembershipModel(
                            id=demo_uuid(f"mbr-{farmer_idx:03d}"),
                            cooperative_id=coop_id,
                            farmer_id=f_id,
                            membership_number=f"MBR-DEMO-{farmer_idx:03d}",
                            joined_at=now - timedelta(days=rng.randint(45, 365)),
                            status="ACTIVE",
                        )
                    )
                    refs["farmers"].append(f_id)
                    refs["farmer_parties"][f_id] = fp_id
                    refs["farmer_coop"][f_id] = coop_id
                    refs["targets"][f"farmer-{farmer_idx:03d}"] = f_id

                    num_farms = 2 if farmer_idx <= 15 else 1
                    farm_list: list[UUID] = []
                    for sub in range(num_farms):
                        farm_idx += 1
                        fb_id = demo_uuid(f"farm-{farm_idx:03d}")
                        has_coords = (farm_idx % 5) != 0
                        lat_v = (
                            Decimal(f"{rng.uniform(0.11, 0.46):.6f}") if has_coords else None
                        )
                        lon_v = (
                            Decimal(f"{rng.uniform(101.68, 102.20):.6f}") if has_coords else None
                        )
                        session.add(
                            FarmModel(
                                id=fb_id,
                                farmer_id=f_id,
                                farm_code=f"KBN-DEMO-{farm_idx:03d}",
                                farm_name=f"Kebun Demo Blok {chr(65 + sub)} #{farmer_idx:02d}",
                                area_hectares=Decimal(f"{rng.uniform(1.5, 6.2):.4f}"),
                                planting_year=rng.choice([2012, 2014, 2016, 2018, 2020]),
                                stdb_number=f"STDB-DEMO-{farm_idx:04d}" if has_coords else None,
                                village=villages[(farm_idx - 1) % len(villages)],
                                district=district,
                                latitude=lat_v,
                                longitude=lon_v,
                                verification_status="VERIFIED" if has_coords else "UNVERIFIED",
                                version=1,
                                created_at=now,
                                updated_at=now,
                            )
                        )
                        farm_list.append(fb_id)
                    refs["farmer_farms"][f_id] = farm_list

            # 5. Vehicles (12) & Drivers (12)
            for idx in range(1, 13):
                vid = demo_uuid(f"vehicle-{idx:02d}")
                did = demo_uuid(f"driver-{idx:02d}")
                plate = f"BM {8100 + idx} DEM"
                cap = Decimal(rng.choice(["8000.000", "10000.000", "12000.000"]))
                session.add(
                    VehicleModel(
                        id=vid,
                        plate_number=plate,
                        vehicle_type=f"Dump Truck TBS {int(cap // 1000)} Ton (Demo)",
                        nominal_capacity_kg=cap,
                        status="ACTIVE",
                        created_at=now,
                        updated_at=now,
                    )
                )
                session.add(
                    DriverModel(
                        id=did,
                        full_name=f"{faker.name()} (Supir Demo)",
                        driver_reference=f"SIM-B2-DEM{idx:02d}",
                        contact_phone=f"0812-7700-{1000 + idx}",
                        status="ACTIVE",
                        created_at=now,
                        updated_at=now,
                    )
                )
                refs["vehicles"].append(vid)
                refs["vehicle_plates"].append(plate)
                refs["drivers"].append(did)

            await session.flush()

            # 6. 12 User Accounts (7 roles + maker/checker + cross-scope)
            for spec in ACTOR_SPECS:
                uid = demo_uuid(spec.tag)
                target_id = refs["targets"].get(spec.target_tag) if spec.target_tag else None
                linked_party = (
                    refs["farmer_parties"].get(target_id)
                    if spec.role == RoleCode.FARMER and target_id is not None
                    else None
                )
                session.add(
                    UserAccountModel(
                        id=uid,
                        username=spec.username,
                        email=f"{spec.username}@demo.example.invalid",
                        display_name=spec.label,
                        password_hash=pw_hash,
                        linked_party_id=linked_party,
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
                        id=demo_uuid(f"grant:{spec.tag}"),
                        user_id=uid,
                        role_id=deterministic_role_id(spec.role.value),
                        granted_by=None,
                        granted_at=now,
                        revoked_at=None,
                    )
                )
                session.add(
                    UserAccessScopeModel(
                        id=demo_uuid(f"userscope:{spec.tag}"),
                        user_id=uid,
                        scope_type=spec.scope_type.value,
                        farmer_id=target_id if spec.scope_type == ScopeType.FARMER else None,
                        cooperative_id=(
                            target_id if spec.scope_type == ScopeType.COOPERATIVE else None
                        ),
                        mill_id=target_id if spec.scope_type == ScopeType.MILL else None,
                        granted_by=None,
                        created_at=now,
                        revoked_at=None,
                    )
                )
                principal = make_principal(
                    spec, user_id=uid, target_id=target_id, linked_party_id=linked_party
                )
                refs["principals"][spec.username] = principal

            # 7. Public Pages & Public Notices
            ops1_id = refs["principals"]["demo_perumda_ops_01"].user_id
            session.add(
                PublicPageModel(
                    id=demo_uuid("pubpage-about"),
                    slug="about-agroniaga",
                    title="Tentang Unit Agro Niaga Perumda Tuah Sekata (Mode Demo)",
                    content=(
                        "MODE DEMO - DATA SINTETIS. Profil ini menunjukkan tata kelola rantai "
                        "pasok TBS Unit Agro Niaga. Unit Listrik dan Gas tidak termasuk sistem ini."
                    ),
                    publication_status="PUBLISHED",
                    published_at=now,
                    updated_by=ops1_id,
                    updated_at=now,
                )
            )
            session.add(
                PublicPageModel(
                    id=demo_uuid("pubpage-partnership"),
                    slug="partnership-info",
                    title="Informasi Kemitraan Pasokan TBS (Mode Demo)",
                    content=(
                        "MODE DEMO - DATA SINTETIS. Koperasi mitra resmi terhubung dengan PKS "
                        "mitra melalui pencatatan timbangan, kontrak berkuota, e-DO QR, dan "
                        "rekonsiliasi."
                    ),
                    publication_status="PUBLISHED",
                    published_at=now,
                    updated_by=ops1_id,
                    updated_at=now,
                )
            )
            notices = (
                (
                    "[DEMO] Transparansi Harga Acuan Disbun Riau (Simulasi)",
                    "Harga acuan Disbun Provinsi Riau ditampilkan terpisah dari kutipan PKS.",
                ),
                (
                    "[DEMO] Aturan Toleransi Susut Berat 1,5000% (SIMULATION_ONLY)",
                    "Toleransi rekonsiliasi 1,5000% dan alokasi petani memakai rule simulasi.",
                ),
                (
                    "[DEMO] Pemberitahuan Lingkungan Data Sintetis",
                    "Seluruh transaksi dan identitas pada lingkungan ini adalah data demo lokal.",
                ),
            )
            for idx, (title, body) in enumerate(notices, 1):
                session.add(
                    PublicNoticeModel(
                        id=demo_uuid(f"pubnotice-{idx:02d}"),
                        title=title,
                        body=body,
                        start_at=now - timedelta(days=5),
                        end_at=now + timedelta(days=30),
                        status="PUBLISHED",
                        created_by=ops1_id,
                        created_at=now,
                    )
                )

            # 8. 3 Disbun Reference Prices
            cat_disbun = deterministic_category_id("DISBUN_10_20")
            src_disbun = deterministic_source_id("DISBUN_RIAU")
            for idx, (days_ago, duration, price_str) in enumerate(
                ((2, 14, "2965.00"), (16, 14, "2940.00"), (30, 14, "2910.00")), 1
            ):
                session.add(
                    DisbunReferencePriceModel(
                        id=demo_uuid(f"disbun-{idx:02d}"),
                        price_source_id=src_disbun,
                        price_category_id=cat_disbun,
                        price_per_kg=Decimal(price_str),
                        effective_from=now - timedelta(days=days_ago),
                        effective_until=now - timedelta(days=days_ago) + timedelta(days=duration),
                        verification_status="PUBLISHED",
                        created_at=now - timedelta(days=days_ago),
                    )
                )

            append_audit_event(
                session,
                AuditRecordInput(
                    actor_id=refs["principals"]["demo_sys_admin_01"].user_id,
                    event_type="DEMO_MASTER_DATA_INITIALIZED",
                    module="admin",
                    resource_type="system_rule_versions",
                    resource_id=str(RULE_RECONCILIATION_TOLERANCE_ID),
                    new_state={"seed": DEMO_SEED, "target_db": DEMO_DB_NAME},
                    reason="Inisialisasi master data sintetis demo lokal",
                    occurred_at=now,
                ),
            )
    return refs


async def _populate_workflows(
    sf: async_sessionmaker[AsyncSession],
    engine: AsyncEngine,
    redis_mgr: RedisClientManager,
    settings: Settings,
    refs: dict[str, Any],
    *,
    rng: random.Random,
    now: datetime,
) -> None:
    idem = SqlAlchemyIdempotencySlotAdapter(sf)
    evidence_dir = str((BACKEND_ROOT / settings.FILE_STORAGE_DIR).resolve())
    files_svc = FilesService(
        repo=SqlAlchemyFilesRepository(sf),
        storage=LocalEvidenceStorageAdapter(evidence_dir),
    )
    pricing_svc = PricingService(
        repo=SqlAlchemyPricingRepository(sf),
        cache_invalidator=RedisPublicPricingInvalidator(redis_mgr),
    )
    receiving_svc = TbsReceivingService(repo=SqlAlchemyTbsReceivingRepository(sf), idempotency=idem)
    contracts_svc = ContractsService(repo=SqlAlchemyContractsRepository(sf), idempotency=idem)
    logistics_svc = LogisticsService(repo=SqlAlchemyLogisticsRepository(sf), idempotency=idem)
    mill_svc = MillWeighingService(repo=SqlAlchemyMillWeighingRepository(sf), idempotency=idem)
    rec_svc = ReconciliationService(repo=SqlAlchemyReconciliationRepository(sf), idempotency=idem)
    fin_svc = FinanceService(repo=SqlAlchemyFinanceRepository(sf), idempotency=idem)
    admin_svc = AdminGovernanceService(
        repo=SqlAlchemyAdminRepository(sf),
        observability=CoreSystemObservabilityAdapter(
            service_name=settings.APP_NAME,
            db_engine=engine,
            redis_manager=redis_mgr,
            tracker=ObservabilityTracker(),
        ),
    )

    p = refs["principals"]
    ops1, ops2 = p["demo_perumda_ops_01"], p["demo_perumda_ops_02"]
    fin1, fin2 = p["demo_perumda_fin_01"], p["demo_perumda_fin_02"]
    kop1, kop2 = p["demo_kop_op_01"], p["demo_kop_op_02"]
    mill1, mill2 = p["demo_mill_op_01"], p["demo_mill_op_02"]
    director = p["demo_director_01"]
    sys_admin = p["demo_sys_admin_01"]

    await admin_svc.create_rule_version(
        principal=sys_admin,
        rule_code="RECONCILIATION_WEIGHT_TOLERANCE",
        effective_from=now - timedelta(days=3),
        effective_until=now + timedelta(days=90),
        rule_config={"tolerance_percent": "1.5000", "negative_difference_holds": True},
        policy_classification=PolicyClassification.SIMULATION_ONLY,
        reason="Versi simulasi demo toleransi susut 1,5000%",
    )

    # Scenario A: 20 TBS Price Quotes
    # (8 active PUBLISHED, 4 EXPIRED, 3 VERIFIED, 2 PENDING, 2 DRAFT, 1 REJECTED)
    cat_swadaya = deterministic_category_id("SWADAYA_STD")
    cat_plasma = deterministic_category_id("PLASMA_KONTRAK")
    src_official = deterministic_source_id("MILL_OFFICIAL")
    src_manual = deterministic_source_id("VERIFIED_MANUAL")

    quote_specs: list[tuple[int, UUID, UUID, str, int, int, str]] = [
        (0, cat_swadaya, src_official, "2910.00", -3, 14, "PUBLISHED"),
        (0, cat_plasma, src_official, "2985.00", -3, 14, "PUBLISHED"),
        (1, cat_swadaya, src_official, "2885.00", -2, 14, "PUBLISHED"),
        (1, cat_plasma, src_manual, "2950.00", -2, 14, "PUBLISHED"),
        (2, cat_swadaya, src_official, "2870.00", -2, 14, "PUBLISHED"),
        (2, cat_plasma, src_official, "2935.00", -2, 14, "PUBLISHED"),
        (3, cat_swadaya, src_manual, "2850.00", -1, 14, "PUBLISHED"),
        (4, cat_swadaya, src_official, "2990.00", -1, 14, "PUBLISHED"),
        (0, cat_swadaya, src_official, "2840.00", -25, 10, "PUBLISHED"),
        (1, cat_swadaya, src_official, "2825.00", -25, 10, "PUBLISHED"),
        (2, cat_swadaya, src_official, "2810.00", -25, 10, "PUBLISHED"),
        (3, cat_swadaya, src_manual, "2795.00", -25, 10, "PUBLISHED"),
        (0, cat_swadaya, src_manual, "2920.00", 15, 14, "VERIFIED"),
        (1, cat_swadaya, src_manual, "2895.00", 15, 14, "VERIFIED"),
        (2, cat_plasma, src_manual, "2945.00", 15, 14, "VERIFIED"),
        (0, cat_swadaya, src_manual, "2930.00", 29, 14, "PENDING_VERIFICATION"),
        (3, cat_swadaya, src_manual, "2860.00", 29, 14, "PENDING_VERIFICATION"),
        (1, cat_swadaya, src_manual, "2900.00", 30, 14, "DRAFT"),
        (2, cat_swadaya, src_manual, "2875.00", 30, 14, "DRAFT"),
        (0, cat_swadaya, src_manual, "3150.00", 31, 14, "REJECTED"),
    ]
    for q_idx, (mill_idx, cat_id, src_id, price_str, start_off, dur_days, state) in enumerate(
        quote_specs, 1
    ):
        eff_from = now + timedelta(days=start_off)
        eff_until = eff_from + timedelta(days=dur_days)
        q = await pricing_svc.create_price_draft(
            principal=ops1,
            mill_id=refs["mills"][mill_idx],
            price_category_id=cat_id,
            source_id=src_id,
            price_per_kg_raw=price_str,
            effective_from=eff_from,
            effective_until=eff_until,
            source_document_id=None,
            notes=f"Kutipan demo #{q_idx:02d} ({state})",
        )
        if state != "DRAFT":
            q = await pricing_svc.submit_price(principal=ops1, price_quote_id=q.id)
        if state == "REJECTED":
            await pricing_svc.verify_or_reject_price(
                principal=ops2,
                price_quote_id=q.id,
                decision=VerifyDecision.REJECT,
                reason="Simulasi penolakan demo: harga melampaui batas wajar referensi",
            )
        elif state in ("VERIFIED", "PUBLISHED"):
            q = await pricing_svc.verify_or_reject_price(
                principal=ops2,
                price_quote_id=q.id,
                decision=VerifyDecision.APPROVE,
                reason="Terverifikasi dua tingkat (demo checker)",
            )
        if state == "PUBLISHED":
            await pricing_svc.publish_price(principal=ops2, price_quote_id=q.id)

    # Scenario C: 8 Trade Contracts (5 ACTIVE PRINCIPAL, 1 UNCONFIRMED, 1 PENDING_APPROVAL, 1 DRAFT)
    today = date.today()
    contract_defs: list[tuple[str, int, BusinessModelCode, PerumdaRoleCode, str, str, str]] = [
        (
            "KTR-DEMO-PRI-01",
            0,
            BusinessModelCode.PRINCIPAL,
            PerumdaRoleCode.SELLER,
            "2910.00",
            "120000.000",
            "ACTIVE",
        ),
        (
            "KTR-DEMO-NEAR-02",
            1,
            BusinessModelCode.PRINCIPAL,
            PerumdaRoleCode.SELLER,
            "2885.00",
            "24000.000",
            "ACTIVE",
        ),
        (
            "KTR-DEMO-PRI-03",
            2,
            BusinessModelCode.PRINCIPAL,
            PerumdaRoleCode.SELLER,
            "2870.00",
            "80000.000",
            "ACTIVE",
        ),
        (
            "KTR-DEMO-PRI-04",
            3,
            BusinessModelCode.PRINCIPAL,
            PerumdaRoleCode.SELLER,
            "2850.00",
            "60000.000",
            "ACTIVE",
        ),
        (
            "KTR-DEMO-PRIV-05",
            4,
            BusinessModelCode.PRINCIPAL,
            PerumdaRoleCode.SELLER,
            "2990.00",
            "40000.000",
            "ACTIVE",
        ),
        (
            "KTR-DEMO-UNC-06",
            0,
            BusinessModelCode.UNCONFIRMED,
            PerumdaRoleCode.UNCONFIRMED,
            "2890.00",
            "50000.000",
            "ACTIVE",
        ),
        (
            "KTR-DEMO-PEND-07",
            0,
            BusinessModelCode.PRINCIPAL,
            PerumdaRoleCode.SELLER,
            "2915.00",
            "45000.000",
            "PENDING_APPROVAL",
        ),
        (
            "KTR-DEMO-DRF-08",
            1,
            BusinessModelCode.PRINCIPAL,
            PerumdaRoleCode.SELLER,
            "2880.00",
            "35000.000",
            "DRAFT",
        ),
    ]
    contracts_by_code: dict[str, Any] = {}
    for cnum, mill_idx, bmc, prole, price_str, quota_str, target_state in contract_defs:
        mill_id = refs["mills"][mill_idx]
        buyer_party = refs["mill_to_company_party"][mill_id]
        if target_state == "DRAFT":
            c_id = demo_uuid(f"contract:{cnum}")
            async with sf() as session:
                async with session.begin():
                    session.add(
                        TradeContractModel(
                            id=c_id,
                            contract_number=cnum,
                            mill_id=mill_id,
                            start_date=today - timedelta(days=5),
                            end_date=today + timedelta(days=45),
                            price_rule_type=PriceRuleType.FIXED.value,
                            agreed_price_per_kg=Decimal(price_str),
                            grading_policy_reference="BSD-DEC-006-SIMULATION",
                            business_model_code=bmc.value,
                            perumda_role=prole.value,
                            seller_party_id=refs["party_perumda"],
                            buyer_party_id=buyer_party,
                            business_model_rule_version=RULE_RECONCILIATION_TOLERANCE_ID,
                            payment_terms="Pembayaran manual simulasi H+3 pasca rekonsiliasi",
                            status=ContractStatus.DRAFT.value,
                            created_by=ops1.user_id,
                            version=1,
                            created_at=now,
                            updated_at=now,
                        )
                    )
                    await session.flush()
                    session.add(
                        ContractQuotaPeriodModel(
                            id=demo_uuid(f"qp:{cnum}"),
                            contract_id=c_id,
                            period_start=today - timedelta(days=5),
                            period_end=today + timedelta(days=45),
                            quota_limit_kg=Decimal(quota_str),
                            status="ACTIVE",
                            created_at=now,
                            updated_at=now,
                        )
                    )
                    session.add(
                        ContractApprovalEventModel(
                            id=demo_uuid(f"caev:{cnum}"),
                            contract_id=c_id,
                            action="CREATE_DRAFT",
                            previous_status=ContractStatus.DRAFT.value,
                            new_status=ContractStatus.DRAFT.value,
                            actor_id=ops1.user_id,
                            reason="Draf awal kontrak demo",
                            created_at=now,
                        )
                    )
            contracts_by_code[cnum] = await contracts_svc.get_contract_detail(contract_id=c_id)
            continue

        contract = await contracts_svc.create_contract(
            principal=ops1,
            contract_number=cnum,
            mill_id=mill_id,
            start_date=today - timedelta(days=7),
            end_date=today + timedelta(days=30),
            price_rule_type=PriceRuleType.FIXED,
            agreed_price_per_kg_raw=price_str,
            business_model_code=bmc,
            perumda_role=prole,
            seller_party_id=refs["party_perumda"],
            buyer_party_id=buyer_party,
            agent_party_id=None,
            represented_party_id=None,
            payment_terms="Transfer bank manual terverifikasi H+3 (simulasi)",
            initial_quota_kg_raw=quota_str,
        )
        if target_state == "ACTIVE":
            contract = await contracts_svc.approve_contract(
                principal=director, contract_id=contract.id
            )
        contracts_by_code[cnum] = contract

    # Scenario B: 80 TBS Receipts distributed across Cooperatives 1..4
    receipts_by_coop: dict[UUID, list[Any]] = {cid: [] for cid in refs["coops"]}
    farmer_schedule: list[UUID] = list(refs["farmers"])
    extra_fids = [refs["farmers"][0]] * 5 + [refs["farmers"][i] for i in range(1, 16)]
    farmer_schedule.extend(extra_fids)

    p1_seen_count = 0
    for r_idx, fid in enumerate(farmer_schedule, 1):
        coop_id = refs["farmer_coop"][fid]
        farm_id = refs["farmer_farms"][fid][0]
        writer = (
            kop1 if coop_id == refs["coops"][0] else (kop2 if coop_id == refs["coops"][1] else ops1)
        )
        rcp, _ = await receiving_svc.create_receipt_draft(
            principal=writer,
            raw_idempotency_key=str(demo_uuid(f"idem-rcp-{r_idx:03d}")),
            farmer_id=fid,
            farm_id=farm_id,
            harvest_date=today - timedelta(days=rng.randint(0, 6)),
            received_at=now - timedelta(hours=r_idx),
            notes=f"Penerimaan TBS Demo #{r_idx:03d}",
        )
        if r_idx <= 75:
            if coop_id == refs["coops"][1]:
                # Keep KOP-DEMO-02 deterministic (2.600 kg net -> 20.800 / 24.000 kg ~87% quota)
                gross, tare = Decimal("3400.000"), Decimal("800.000")
            else:
                gross = Decimal(
                    rng.choice(["3200.000", "3800.000", "4200.000", "4600.000", "5100.000"])
                )
                tare = Decimal(rng.choice(["600.000", "800.000", "1000.000", "1100.000"]))
            if fid == refs["farmers"][0] and p1_seen_count < 2:
                gross, tare = Decimal("4000.000"), Decimal("1000.000")
                p1_seen_count += 1
            rcp = await receiving_svc.record_weighing(
                principal=writer,
                receipt_id=rcp.id,
                gross_weight_kg_raw=f"{gross:.3f}",
                tare_weight_kg_raw=f"{tare:.3f}",
                correction_reason=None,
                expected_version=rcp.version,
            )
            if r_idx in (2, 18, 35, 52):
                rcp = await receiving_svc.record_weighing(
                    principal=writer,
                    receipt_id=rcp.id,
                    gross_weight_kg_raw=f"{(gross + Decimal('50.000')):.3f}",
                    tare_weight_kg_raw=f"{tare:.3f}",
                    correction_reason="Koreksi penimbangan ulang timbangan koperasi (demo)",
                    expected_version=rcp.version,
                )
            if r_idx <= 52:
                rcp = await receiving_svc.record_grading(
                    principal=writer,
                    receipt_id=rcp.id,
                    items=[
                        GradingInputItem(
                            grading_category="Sortasi Mutu Simulasi (Brondolan/Basah)",
                            measurement_value_raw="2.0000",
                            deduction_type=GradingDeductionType.WEIGHT_PERCENT,
                            deduction_value_raw=rng.choice(["1.5000", "2.0000", "2.5000"]),
                            calculation_basis="NET_WEIGHT_BEFORE_GRADING",
                            notes="Aturan simulasi grading menunggu SOP resmi",
                        )
                    ],
                    expected_version=rcp.version,
                )
        if r_idx <= 70:
            rcp = await receiving_svc.validate_receipt(principal=writer, receipt_id=rcp.id)
            receipts_by_coop[coop_id].append(rcp)

    # Scenario D: 18 Delivery Orders from 48 validated receipts (zero duplicate allocation)
    edo_plan: list[tuple[int, str, int, int, str]] = [
        (0, "KTR-DEMO-PRI-01", 0, 3, "RECEIVED"),
        (0, "KTR-DEMO-PRI-01", 0, 2, "RECEIVED"),
        (1, "KTR-DEMO-NEAR-02", 1, 2, "RECEIVED"),
        (1, "KTR-DEMO-NEAR-02", 1, 2, "RECEIVED"),
        (0, "KTR-DEMO-UNC-06", 0, 2, "RECEIVED"),
        (2, "KTR-DEMO-PRI-03", 2, 3, "RECEIVED"),
        (0, "KTR-DEMO-PRI-01", 0, 3, "RECEIVED"),
        (2, "KTR-DEMO-PRI-03", 2, 3, "RECEIVED"),
        (0, "KTR-DEMO-PRI-01", 0, 3, "RECEIVED"),
        (3, "KTR-DEMO-PRI-04", 3, 3, "RECEIVED"),
        (1, "KTR-DEMO-NEAR-02", 1, 2, "RECEIVED"),
        (0, "KTR-DEMO-PRIV-05", 4, 2, "RECEIVED"),
        (0, "KTR-DEMO-PRI-01", 0, 3, "ARRIVED"),
        (1, "KTR-DEMO-NEAR-02", 1, 2, "ARRIVED"),
        (0, "KTR-DEMO-PRI-01", 0, 3, "IN_TRANSIT"),
        (2, "KTR-DEMO-PRI-03", 2, 4, "IN_TRANSIT"),
        (0, "KTR-DEMO-PRI-01", 0, 3, "READY"),
        (0, "KTR-DEMO-PRI-01", 0, 3, "DRAFT"),
    ]

    pool_by_coop: dict[UUID, list[Any]] = {
        cid: list(rows) for cid, rows in receipts_by_coop.items()
    }
    coop0_id = refs["coops"][0]
    p1_id = refs["farmers"][0]
    p1_pool = [r for r in pool_by_coop[coop0_id] if r.farmer_id == p1_id]
    other0_pool = [r for r in pool_by_coop[coop0_id] if r.farmer_id != p1_id]
    pool_by_coop[coop0_id] = other0_pool[:3] + p1_pool[:2] + other0_pool[3:] + p1_pool[2:]

    created_dos: list[tuple[int, Any, int, str]] = []
    for edo_idx, (coop_idx, contract_key, mill_idx, r_count, target_status) in enumerate(
        edo_plan, 1
    ):
        cid = refs["coops"][coop_idx]
        chosen_rcps = [pool_by_coop[cid].pop(0) for _ in range(r_count)]
        writer = kop1 if coop_idx == 0 else (kop2 if coop_idx == 1 else ops1)
        mill_actor = mill1 if mill_idx == 0 else (mill2 if mill_idx == 1 else ops1)
        mill_id = refs["mills"][mill_idx]
        contract_obj = contracts_by_code[contract_key]
        v_idx = (edo_idx - 1) % len(refs["vehicles"])
        vehicle_id = refs["vehicles"][v_idx]
        plate_number = refs["vehicle_plates"][v_idx]
        driver_id = refs["drivers"][(edo_idx - 1) % len(refs["drivers"])]

        do = await logistics_svc.create_draft(
            principal=writer,
            mill_id=mill_id,
            contract_id=contract_obj.id,
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            receipt_ids=[r.id for r in chosen_rcps],
        )
        if target_status != "DRAFT":
            do, _ = await logistics_svc.issue_delivery_order(
                principal=writer,
                raw_idempotency_key=str(demo_uuid(f"idem-edo-issue-{edo_idx:02d}")),
                delivery_order_id=do.id,
                expected_version=do.version,
                confirm_lock_allocations=True,
            )
        if target_status in ("IN_TRANSIT", "ARRIVED", "RECEIVED"):
            do = await logistics_svc.transition_status(
                principal=writer,
                delivery_order_id=do.id,
                target_status=DeliveryOrderStatus.IN_TRANSIT,
                reason="Armada demo berangkat menuju PKS mitra",
                expected_version=do.version,
            )
        if target_status in ("ARRIVED", "RECEIVED"):
            if do.qr_verification_token is None:
                raise SystemExit(f"[ERROR] Token QR tidak terbentuk untuk e-DO #{edo_idx}")
            do = await logistics_svc.verify_qr_arrival(
                principal=mill_actor,
                qr_token_or_edo_number=do.qr_verification_token,
                observed_plate_number=plate_number,
            )
        created_dos.append((edo_idx, do, mill_idx, contract_key))

    # Scenario E: 12 Mill Weighing Tickets & 10 Reconciliation Cases
    reconciled_cases: dict[int, Any] = {}
    for edo_idx, do, mill_idx, _contract_key in created_dos[:12]:
        mill_actor = mill1 if mill_idx == 0 else (mill2 if mill_idx == 1 else ops1)
        origin_kg = do.total_origin_weight_kg
        tare_kg = Decimal("8500.000")

        if edo_idx == 7:
            target_net = (origin_kg + Decimal("320.000")).quantize(Decimal("0.001"))
        elif edo_idx == 8:
            target_net = (origin_kg * Decimal("0.952")).quantize(Decimal("0.001"))
        elif edo_idx == 9:
            target_net = (origin_kg * Decimal("0.965")).quantize(Decimal("0.001"))
        elif edo_idx == 10:
            target_net = (origin_kg * Decimal("0.968")).quantize(Decimal("0.001"))
        else:
            target_net = (origin_kg * Decimal("0.992")).quantize(Decimal("0.001"))

        gross_kg = target_net + tare_kg
        slip_asset = await files_svc.upload_evidence(
            principal=mill_actor,
            classification=FileClassification.MILL_TICKET_PROOF,
            filename=f"slip-demo-edo-{edo_idx:02d}.png",
            declared_mime="image/png",
            content=TINY_PNG_BYTES,
        )
        ticket, _ = await mill_svc.create_ticket(
            principal=mill_actor,
            raw_idempotency_key=str(demo_uuid(f"idem-wt-{edo_idx:02d}")),
            delivery_order_id=do.id,
            ticket_number=f"WB-DEMO-{edo_idx:03d}",
            gross_weight_kg_raw=f"{gross_kg:.3f}",
            tare_weight_kg_raw=f"{tare_kg:.3f}",
            weighed_at=now - timedelta(hours=max(1, 14 - edo_idx)),
            proof_file_id=slip_asset.id,
            grading_items=[
                MillGradingInput(
                    grading_category="Sortasi Pabrik (Simulasi)",
                    deduction_type=MillGradingDeductionType.WEIGHT_PERCENT,
                    deduction_value_raw="1.5000",
                    calculation_basis="MILL_NET_WEIGHT",
                    notes="Grading pabrik demo berstatus simulasi",
                )
            ],
        )
        if edo_idx == 1:
            ticket = await mill_svc.revise_ticket(
                principal=mill_actor,
                ticket_id=ticket.id,
                gross_weight_kg_raw=f"{(gross_kg + Decimal('15.000')):.3f}",
                tare_weight_kg_raw=f"{tare_kg:.3f}",
                proof_file_id=slip_asset.id,
                correction_reason="Penyesuaian pembulatan nol jembatan timbang PKS (demo)",
            )

        if edo_idx <= 10:
            await mill_svc.verify_ticket(principal=mill_actor, ticket_id=ticket.id)
            rec, _ = await rec_svc.create_or_trigger(
                principal=ops1,
                raw_idempotency_key=str(demo_uuid(f"idem-rec-{edo_idx:02d}")),
                delivery_order_id=do.id,
                weight_basis=WeightBasis.NET_WEIGHT_BEFORE_GRADING,
            )
            if edo_idx in (9, 10):
                disp_file = await files_svc.upload_evidence(
                    principal=ops2,
                    classification=FileClassification.DISPUTE_EVIDENCE,
                    filename=f"sengketa-demo-{edo_idx:02d}.png",
                    declared_mime="image/png",
                    content=TINY_PNG_BYTES,
                )
                mid_wt = ((origin_kg + rec.mill_weight_kg) / Decimal("2")).quantize(
                    Decimal("0.001")
                )
                rec = await rec_svc.submit_review(
                    principal=ops2,
                    reconciliation_id=rec.id,
                    decision=DisputeDecision.AGREED_SETTLEMENT_WEIGHT,
                    reason="Pemeriksaan bukti foto segel & slip timbang demo terlampir",
                    evidence_file_id=disp_file.id,
                    proposed_settlement_weight_raw=f"{mid_wt:.3f}",
                )
            if edo_idx == 10:
                agreed_mid = ((origin_kg + rec.mill_weight_kg) / Decimal("2")).quantize(
                    Decimal("0.001")
                )
                rec = await rec_svc.resolve_dispute(
                    principal=director,
                    reconciliation_id=rec.id,
                    decision=DisputeDecision.AGREED_SETTLEMENT_WEIGHT,
                    final_outcome=ReconciliationStatus.RESOLVED,
                    agreed_settlement_weight_raw=f"{agreed_mid:.3f}",
                    reason="Putusan Direksi Demo: gunakan bobot tengah sepakat untuk pelunasan",
                    evidence_file_id=None,
                )
            if edo_idx in (2, 6):
                await rec_svc.compute_allocations(
                    principal=ops1,
                    reconciliation_id=rec.id,
                    mode=AllocationMode.SIMULATION,
                    allocation_policy_version_id=RULE_FARMER_ALLOCATION_POLICY_ID,
                )
            reconciled_cases[edo_idx] = (rec, do)

    # Scenario F: Invoices (AR & AP separated), Director Approval != PAID, & Synthetic Evidence
    case1, do1 = reconciled_cases[1]
    mill1_party = refs["mill_to_company_party"][do1.mill_id]
    coop1_party = refs["coop_parties"][do1.cooperative_id]
    ar1 = await fin_svc.create_invoice_draft(
        principal=fin1,
        invoice_type=InvoiceType.ACCOUNTS_RECEIVABLE,
        creditor_party_id=refs["party_perumda"],
        debtor_party_id=mill1_party,
        reconciliation_case_id=case1.id,
        invoice_date=today - timedelta(days=1),
        due_date=today + timedelta(days=14),
    )
    ar1 = await fin_svc.verify_invoice(
        principal=fin2, invoice_id=ar1.id, decision="APPROVE", reason="Verifikasi piutang AR demo"
    )
    await fin_svc.issue_invoice(principal=fin1, invoice_id=ar1.id)

    ap1 = await fin_svc.create_invoice_draft(
        principal=fin1,
        invoice_type=InvoiceType.ACCOUNTS_PAYABLE,
        creditor_party_id=coop1_party,
        debtor_party_id=refs["party_perumda"],
        reconciliation_case_id=case1.id,
        invoice_date=today - timedelta(days=1),
        due_date=today + timedelta(days=7),
    )
    ap1 = await fin_svc.verify_invoice(
        principal=fin2,
        invoice_id=ap1.id,
        decision="APPROVE",
        reason="Verifikasi kewajiban AP koperasi",
    )
    ap1 = await fin_svc.issue_invoice(principal=fin1, invoice_id=ap1.id)
    await fin_svc.approve_payment(
        principal=director,
        raw_idempotency_key=str(demo_uuid("idem-pay-app-1")),
        invoice_id=ap1.id,
        decision="APPROVED",
        reason="Otorisasi pencairan demo (APPROVED != PAID sebelum bukti transfer)",
    )

    # Case 2: AR ISSUED + AP (PET-DEMO-001 Jalur C) VERIFIED PAID SIMULATION
    case2, do2 = reconciled_cases[2]
    mill2_case_party = refs["mill_to_company_party"][do2.mill_id]
    farmer1_party = refs["farmer_parties"][refs["farmers"][0]]
    ar2 = await fin_svc.create_invoice_draft(
        principal=fin1,
        invoice_type=InvoiceType.ACCOUNTS_RECEIVABLE,
        creditor_party_id=refs["party_perumda"],
        debtor_party_id=mill2_case_party,
        reconciliation_case_id=case2.id,
        invoice_date=today - timedelta(days=2),
        due_date=today + timedelta(days=12),
    )
    ar2 = await fin_svc.verify_invoice(
        principal=fin2, invoice_id=ar2.id, decision="APPROVE", reason="AR case 2 terverifikasi"
    )
    await fin_svc.issue_invoice(principal=fin1, invoice_id=ar2.id)

    ap2 = await fin_svc.create_invoice_draft(
        principal=fin1,
        invoice_type=InvoiceType.ACCOUNTS_PAYABLE,
        creditor_party_id=farmer1_party,
        debtor_party_id=refs["party_perumda"],
        reconciliation_case_id=case2.id,
        invoice_date=today - timedelta(days=2),
        due_date=today + timedelta(days=5),
    )
    ap2 = await fin_svc.verify_invoice(
        principal=fin2,
        invoice_id=ap2.id,
        decision="APPROVE",
        reason="Verifikasi Jalur C petani PET-DEMO-001",
    )
    ap2 = await fin_svc.issue_invoice(principal=fin1, invoice_id=ap2.id)
    await fin_svc.approve_payment(
        principal=director,
        raw_idempotency_key=str(demo_uuid("idem-pay-app-2")),
        invoice_id=ap2.id,
        decision="APPROVED",
        reason="Persetujuan pembayaran simulasi PET-DEMO-001",
    )
    pay_proof_asset = await files_svc.upload_evidence(
        principal=fin1,
        classification=FileClassification.PAYMENT_PROOF,
        filename="bukti-transfer-simulasi-demo-002.png",
        declared_mime="image/png",
        content=TINY_PNG_BYTES,
    )
    pay2, _ = await fin_svc.record_payment(
        principal=fin1,
        raw_idempotency_key=str(demo_uuid("idem-pay-rec-2")),
        invoice_id=ap2.id,
        payment_direction=PaymentDirection.OUTBOUND,
        payer_party_id=refs["party_perumda"],
        payee_party_id=farmer1_party,
        amount_raw=f"{ap2.total_amount:.2f}",
        payment_date=today,
        payment_method=PaymentMethod.BANK_TRANSFER_MANUAL,
        payment_reference="SIM-DEMO-TRF-0002",
        proof_file_id=pay_proof_asset.id,
    )
    await fin_svc.verify_payment_record(
        principal=fin2,
        payment_id=pay2.id,
        decision="VERIFIED",
        reason="Verifikasi bukti transfer simulasi demo (non-perbankan)",
    )

    # Case 3: ISSUED AP waiting Director approval on /app/direksi/persetujuan
    case3, do3 = reconciled_cases[3]
    coop3_party = refs["coop_parties"][do3.cooperative_id]
    ap3 = await fin_svc.create_invoice_draft(
        principal=fin1,
        invoice_type=InvoiceType.ACCOUNTS_PAYABLE,
        creditor_party_id=coop3_party,
        debtor_party_id=refs["party_perumda"],
        reconciliation_case_id=case3.id,
        invoice_date=today,
        due_date=today + timedelta(days=10),
    )
    ap3 = await fin_svc.verify_invoice(
        principal=fin2,
        invoice_id=ap3.id,
        decision="APPROVE",
        reason="Siap diajukan otorisasi Direksi",
    )
    await fin_svc.issue_invoice(principal=fin1, invoice_id=ap3.id)

    # Case 10 (RESOLVED): PENDING_VERIFICATION invoice waiting finance checker
    case10, do10 = reconciled_cases[10]
    await fin_svc.create_invoice_draft(
        principal=fin1,
        invoice_type=InvoiceType.ACCOUNTS_RECEIVABLE,
        creditor_party_id=refs["party_perumda"],
        debtor_party_id=refs["mill_to_company_party"][do10.mill_id],
        reconciliation_case_id=case10.id,
        invoice_date=today,
        due_date=today + timedelta(days=14),
    )

    # Case 5 (UNCONFIRMED): Remains PENDING_SOP & never issued (FIN_POLICY_UNCONFIRMED)
    case5, do5 = reconciled_cases[5]
    await fin_svc.create_invoice_draft(
        principal=fin1,
        invoice_type=InvoiceType.ACCOUNTS_RECEIVABLE,
        creditor_party_id=refs["party_perumda"],
        debtor_party_id=refs["mill_to_company_party"][do5.mill_id],
        reconciliation_case_id=case5.id,
        invoice_date=today,
        due_date=today + timedelta(days=14),
    )


async def _verify_integrity(
    sf: async_sessionmaker[AsyncSession], redis_mgr: RedisClientManager
) -> None:
    pong = await redis_mgr.ping()
    if not pong:
        raise SystemExit("[VERIFY FAILED] Redis /2 tidak merespons PING.")
    async with sf() as session:
        counts = await _collect_summary(session)
        bad_weights = int(
            (
                await session.execute(
                    select(func.count())
                    .select_from(ReceiptWeighingRevisionModel)
                    .where(
                        (
                            ReceiptWeighingRevisionModel.tare_weight_kg
                            > ReceiptWeighingRevisionModel.gross_weight_kg
                        )
                        | (
                            ReceiptWeighingRevisionModel.net_weight_kg
                            != ReceiptWeighingRevisionModel.gross_weight_kg
                            - ReceiptWeighingRevisionModel.tare_weight_kg
                        )
                    )
                )
            ).scalar_one()
        )
        double_allocs = int(
            (
                await session.execute(
                    text(
                        "SELECT COUNT(*) FROM ("
                        "SELECT receipt_id FROM delivery_order_lines "
                        "WHERE allocation_status = 'ACTIVE' GROUP BY receipt_id HAVING COUNT(*) > 1"
                        ") t"
                    )
                )
            ).scalar_one()
        )
        unconf_issued = int(
            (
                await session.execute(
                    select(func.count())
                    .select_from(InvoiceModel)
                    .where(
                        InvoiceModel.business_model_code == "UNCONFIRMED",
                        InvoiceModel.status == "ISSUED",
                    )
                )
            ).scalar_one()
        )
        bad_rules = int(
            (
                await session.execute(
                    select(func.count())
                    .select_from(SystemRuleVersionModel)
                    .where(
                        SystemRuleVersionModel.rule_code == "RECONCILIATION_WEIGHT_TOLERANCE",
                        SystemRuleVersionModel.approval_status == "APPROVED",
                    )
                )
            ).scalar_one()
        )
        dispute_invoices = int(
            (
                await session.execute(
                    text(
                        "SELECT COUNT(*) FROM invoices i "
                        "JOIN reconciliation_cases r ON r.id = i.reconciliation_case_id "
                        "WHERE r.status IN ('DISPUTE_HOLD', 'UNDER_REVIEW')"
                    )
                )
            ).scalar_one()
        )
    if bad_weights or double_allocs or unconf_issued or bad_rules or dispute_invoices:
        raise SystemExit(
            f"[VERIFY FAILED] Invariant violation: bad_weights={bad_weights}, "
            f"double_allocs={double_allocs}, unconf_issued={unconf_issued}, "
            f"bad_rules={bad_rules}, dispute_invoices={dispute_invoices}"
        )
    print("DEMO_INTEGRITY_VERIFIED:", json.dumps(counts, indent=2))


async def main_async(
    args: argparse.Namespace,
    *,
    env_file: Path,
    storage_dir: Path,
    cred_path: Path,
) -> None:
    settings = load_isolated_demo_settings(env_file)
    engine = build_async_engine(settings)
    sf = build_session_factory(engine)
    redis_mgr = RedisClientManager(settings)

    try:
        await _verify_live_db_and_alembic(engine)

        if args.verify_only:
            async with sf() as session:
                if not await _already_seeded(session):
                    raise SystemExit(
                        "[VERIFY FAILED] Database agroniaga_demo belum memiliki data demo."
                    )
            await _verify_integrity(sf, redis_mgr)
            return

        if args.reset_demo:
            if args.confirm_reset != DEMO_DB_NAME:
                raise SystemExit(
                    f"[ABORT] Reset demo mewajibkan --confirm-reset {DEMO_DB_NAME}."
                )
            if not args.yes:
                prompt = (
                    f"Ketik '{DEMO_DB_NAME}' untuk konfirmasi reset demo & Redis /{DEMO_REDIS_DB}: "
                )
                answer = (await asyncio.to_thread(input, prompt)).strip()
                if answer != DEMO_DB_NAME:
                    raise SystemExit("[ABORT] Reset dibatalkan oleh pengguna.")
            await _reset_demo_db(sf, redis_mgr, storage_dir)
        else:
            async with sf() as session:
                if await _already_seeded(session):
                    counts = await _collect_summary(session)
                    print("DEMO_SEED_SKIPPED_ALREADY_POPULATED (data demo ada, tidak ditimpa):")
                    print(json.dumps(counts, indent=2))
                    if await asyncio.to_thread(cred_path.is_file):
                        print(f"Kredensial demo tersimpan di: {cred_path}")
                    return

        token = request_id_ctx.set("req_demo_seed_0001")
        try:
            Faker.seed(DEMO_SEED)
            faker = Faker("id_ID")
            rng = random.Random(DEMO_SEED)  # noqa: S311
            now = datetime.now(UTC)
            demo_password = f"Demo!{secrets.token_urlsafe(10)}a1"

            refs = await _populate_master_and_users(
                sf,
                faker=faker,
                rng=rng,
                demo_password=demo_password,
                now=now,
            )
            await _populate_workflows(sf, engine, redis_mgr, settings, refs, rng=rng, now=now)
            await redis_mgr.client.flushdb()
            await asyncio.to_thread(
                _write_credentials_file, cred_path, password=demo_password, settings=settings
            )
        finally:
            request_id_ctx.reset(token)

        await _verify_integrity(sf, redis_mgr)
        print(f"DEMO_CREDENTIALS_FILE: {cred_path}")
    finally:
        await redis_mgr.close()
        await dispose_database(engine)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seeder sintetis idempotent untuk agroniaga_demo.")
    parser.add_argument(
        "--env-file",
        default=str(BACKEND_ROOT / ".env.demo"),
        help="Path eksplisit ke file konfigurasi .env.demo",
    )
    parser.add_argument(
        "--reset-demo",
        action="store_true",
        help="Hapus & bangun ulang data HANYA pada agroniaga_demo + Redis /2.",
    )
    parser.add_argument(
        "--confirm-reset",
        default="",
        help=f"Wajib bernilai persis '{DEMO_DB_NAME}' saat menggunakan --reset-demo.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Lewati prompt interaktif setelah --confirm-reset agroniaga_demo diverifikasi.",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Verifikasi integritas & jumlah data demo tanpa mengubah database.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.reset_demo and args.confirm_reset != DEMO_DB_NAME:
        raise SystemExit(f"[ABORT] Reset demo mewajibkan --confirm-reset {DEMO_DB_NAME}.")
    env_file = Path(args.env_file).resolve()
    settings = load_isolated_demo_settings(env_file)
    storage_dir = (BACKEND_ROOT / settings.FILE_STORAGE_DIR).resolve()
    cred_path = (BACKEND_ROOT / ".demo-credentials.local.txt").resolve()
    asyncio.run(
        main_async(
            args,
            env_file=env_file,
            storage_dir=storage_dir,
            cred_path=cred_path,
        )
    )


if __name__ == "__main__":
    main()
