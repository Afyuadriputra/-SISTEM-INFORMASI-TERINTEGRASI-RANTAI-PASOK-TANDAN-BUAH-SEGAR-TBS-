"""Pure business invariants for RBAC, resource scopes, and BR-SYS-002 Separation of Duties."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.core.exceptions import AppError, ErrorCode
from app.modules.identity_access.domain.entities import (
    AccountStatus,
    AuthenticatedPrincipal,
    RoleCode,
    ScopeType,
)


@dataclass(frozen=True, slots=True)
class PermissionSpec:
    """Canonical permission metadata aligned with contracts/role-permissions.yaml."""

    code: str
    module: str
    resource: str
    action: str
    description: str


CANONICAL_PERMISSIONS: tuple[PermissionSpec, ...] = (
    PermissionSpec("public.prices.read", "public_portal", "public_prices", "read", "Harga publik"),
    PermissionSpec("public.mills.read", "public_portal", "public_mills", "read", "Direktori PKS"),
    PermissionSpec("public.profile.read", "public_portal", "public_profile", "read", "Profil"),
    PermissionSpec("auth.session.read", "identity_access", "auth_session", "read", "Profil sesi"),
    PermissionSpec("farmers.read", "master_data", "farmers", "read", "Baca data petani"),
    PermissionSpec("farmers.write", "master_data", "farmers", "write", "Kelola data petani"),
    PermissionSpec("farms.read", "master_data", "farms", "read", "Baca data kebun"),
    PermissionSpec("farms.write", "master_data", "farms", "write", "Kelola data kebun"),
    PermissionSpec("cooperatives.read", "master_data", "cooperatives", "read", "Baca koperasi"),
    PermissionSpec("mills.read", "master_data", "mills", "read", "Baca master PKS internal"),
    PermissionSpec("mills.write", "master_data", "mills", "write", "Kelola master PKS & is_public"),
    PermissionSpec("vehicles.read", "master_data", "vehicles", "read", "Baca armada angkutan"),
    PermissionSpec("vehicles.write", "master_data", "vehicles", "write", "Tambah kendaraan"),
    PermissionSpec("drivers.read", "master_data", "drivers", "read", "Baca daftar sopir"),
    PermissionSpec("drivers.write", "master_data", "drivers", "write", "Tambah sopir operasional"),
    PermissionSpec("prices.read", "pricing", "mill_price_quotes", "read", "Baca harga internal"),
    PermissionSpec("prices.create", "pricing", "mill_price_quotes", "create", "Buat draf harga"),
    PermissionSpec("prices.submit", "pricing", "mill_price_quotes", "submit", "Ajukan verifikasi"),
    PermissionSpec("prices.verify", "pricing", "mill_price_quotes", "verify", "Verifikasi harga"),
    PermissionSpec(
        "prices.publish", "pricing", "mill_price_quotes", "publish", "Publikasikan harga"
    ),
    PermissionSpec("prices.revoke", "pricing", "mill_price_quotes", "revoke", "Cabut publikasi"),
    PermissionSpec("receipts.read", "tbs_receiving", "tbs_receipts", "read", "Baca penerimaan TBS"),
    PermissionSpec("receipts.create", "tbs_receiving", "tbs_receipts", "create", "Catat TBS masuk"),
    PermissionSpec(
        "receipts.weigh", "tbs_receiving", "tbs_receipts", "weigh", "Catat timbang & grade"
    ),
    PermissionSpec("receipts.validate", "tbs_receiving", "tbs_receipts", "validate", "Sahkan TBS"),
    PermissionSpec("receipts.cancel", "tbs_receiving", "tbs_receipts", "cancel", "Batalkan TBS"),
    PermissionSpec("contracts.read", "contracts", "trade_contracts", "read", "Baca kontrak niaga"),
    PermissionSpec("contracts.write", "contracts", "trade_contracts", "write", "Buat draf kontrak"),
    PermissionSpec(
        "contracts.approve", "contracts", "trade_contracts", "approve", "Aktifkan kontrak"
    ),
    PermissionSpec(
        "quotas.reserve", "contracts", "quota_reservations", "reserve", "Reservasi kuota"
    ),
    PermissionSpec(
        "quotas.consume", "contracts", "quota_reservations", "consume", "Konversi kuota"
    ),
    PermissionSpec(
        "quotas.release", "contracts", "quota_reservations", "release", "Lepas reservasi"
    ),
    PermissionSpec("delivery_orders.read", "logistics", "delivery_orders", "read", "Baca e-DO"),
    PermissionSpec("delivery_orders.create", "logistics", "delivery_orders", "create", "Draf e-DO"),
    PermissionSpec(
        "delivery_orders.issue", "logistics", "delivery_orders", "issue", "Terbitkan e-DO"
    ),
    PermissionSpec(
        "delivery_orders.transition", "logistics", "delivery_orders", "transition", "Status e-DO"
    ),
    PermissionSpec(
        "delivery_orders.cancel", "logistics", "delivery_orders", "cancel", "Batal e-DO"
    ),
    PermissionSpec(
        "delivery_orders.verify_arrival",
        "logistics",
        "delivery_orders",
        "verify_arrival",
        "Verifikasi tiba PKS",
    ),
    PermissionSpec(
        "mill_tickets.read", "mill_weighing", "mill_weighing_tickets", "read", "Baca tiket"
    ),
    PermissionSpec(
        "mill_tickets.create", "mill_weighing", "mill_weighing_tickets", "create", "Catat tiket"
    ),
    PermissionSpec(
        "mill_tickets.verify",
        "mill_weighing",
        "mill_weighing_tickets",
        "verify",
        "Verifikasi tiket",
    ),
    PermissionSpec(
        "reconciliations.read",
        "reconciliation",
        "reconciliation_cases",
        "read",
        "Baca rekonsiliasi",
    ),
    PermissionSpec(
        "reconciliations.calculate",
        "reconciliation",
        "reconciliation_cases",
        "calculate",
        "Hitung selisih",
    ),
    PermissionSpec(
        "reconciliations.review", "reconciliation", "dispute_reviews", "review", "Review sengketa"
    ),
    PermissionSpec(
        "reconciliations.resolve",
        "reconciliation",
        "dispute_reviews",
        "resolve",
        "Selesaikan sengketa",
    ),
    PermissionSpec(
        "allocations.compute",
        "reconciliation",
        "farmer_settlement_allocations",
        "compute",
        "Hitung alokasi petani",
    ),
    PermissionSpec("invoices.read", "reconciliation", "invoices", "read", "Baca faktur AR/AP"),
    PermissionSpec("invoices.create", "reconciliation", "invoices", "create", "Buat draf faktur"),
    PermissionSpec("invoices.verify", "reconciliation", "invoices", "verify", "Verifikasi faktur"),
    PermissionSpec("invoices.issue", "reconciliation", "invoices", "issue", "Terbitkan faktur"),
    PermissionSpec("payments.read", "reconciliation", "payment_records", "read", "Baca pembayaran"),
    PermissionSpec(
        "payments.approve", "reconciliation", "payment_approvals", "approve", "Setujui pembayaran"
    ),
    PermissionSpec(
        "payments.record", "reconciliation", "payment_records", "record", "Catat bukti bayar"
    ),
    PermissionSpec(
        "payments.verify", "reconciliation", "payment_records", "verify", "Verifikasi bukti bayar"
    ),
    PermissionSpec("files.upload", "core", "file_assets", "upload", "Unggah metadata berkas bukti"),
    PermissionSpec("files.read", "core", "file_assets", "read", "Unduh/baca berkas bukti"),
    PermissionSpec(
        "reports.operational.read",
        "reporting",
        "reports",
        "read_operational",
        "Laporan operasional",
    ),
    PermissionSpec(
        "reports.finance.read", "reporting", "finance_reports", "read_finance", "Laporan keuangan"
    ),
    PermissionSpec("admin.users.read", "identity_access", "user_accounts", "read", "Baca pengguna"),
    PermissionSpec(
        "admin.users.write", "identity_access", "user_accounts", "write", "Kelola pengguna"
    ),
    PermissionSpec(
        "admin.rules.read", "audit", "system_rule_versions", "read", "Baca versi aturan"
    ),
    PermissionSpec("admin.rules.write", "audit", "system_rule_versions", "write", "Tambah aturan"),
    PermissionSpec("admin.audit.read", "audit", "audit_events", "read", "Baca audit append-only"),
    PermissionSpec("admin.health.read", "audit", "system_health", "read", "Baca CCTV Digital"),
)


ROLE_METADATA: dict[RoleCode, tuple[str, str]] = {
    RoleCode.FARMER: ("Petani Swadaya", "Melihat kebun, penerimaan, dan alokasi pribadinya."),
    RoleCode.COOPERATIVE_OPERATOR: (
        "Operator Koperasi",
        "Mengelola petani/kebun, penerimaan TBS, timbang, dan e-DO koperasinya.",
    ),
    RoleCode.PERUMDA_OPERATIONS: (
        "Staf Operasional Perumda",
        "Mengelola PKS mitra, harga multi-PKS, kontrak & kuota, logistik, dan rekonsiliasi.",
    ),
    RoleCode.PERUMDA_FINANCE: (
        "Staf Keuangan Perumda",
        "Mengelola faktur AR/AP, pengajuan persetujuan, dan verifikasi pembayaran.",
    ),
    RoleCode.MILL_OPERATOR: (
        "Petugas PKS",
        "Memverifikasi kedatangan e-DO & mencatat tiket timbang PKS.",
    ),
    RoleCode.DIRECTOR: (
        "Direksi Perumda",
        "Mengawasi dashboard eksekutif, menyetujui kontrak, dispute, dan pembayaran.",
    ),
    RoleCode.SYSTEM_ADMIN: (
        "Administrator Sistem",
        "Mengelola akun, role/scope, aturan teknis, log audit, dan CCTV Digital (BR-SYS-002).",
    ),
}


ROLE_PERMISSIONS_MAP: dict[RoleCode, frozenset[str]] = {
    RoleCode.FARMER: frozenset(
        {
            "public.prices.read",
            "public.mills.read",
            "public.profile.read",
            "auth.session.read",
            "farmers.read",
            "farms.read",
            "prices.read",
            "receipts.read",
            "delivery_orders.read",
            "payments.read",
            "reports.operational.read",
        }
    ),
    RoleCode.COOPERATIVE_OPERATOR: frozenset(
        {
            "public.prices.read",
            "public.mills.read",
            "public.profile.read",
            "auth.session.read",
            "farmers.read",
            "farmers.write",
            "farms.read",
            "farms.write",
            "cooperatives.read",
            "mills.read",
            "vehicles.read",
            "vehicles.write",
            "drivers.read",
            "drivers.write",
            "prices.read",
            "receipts.read",
            "receipts.create",
            "receipts.weigh",
            "receipts.validate",
            "receipts.cancel",
            "delivery_orders.read",
            "delivery_orders.create",
            "delivery_orders.issue",
            "delivery_orders.transition",
            "delivery_orders.cancel",
            "mill_tickets.read",
            "reconciliations.read",
            "payments.read",
            "reports.operational.read",
        }
    ),
    RoleCode.PERUMDA_OPERATIONS: frozenset(
        {
            "public.prices.read",
            "public.mills.read",
            "public.profile.read",
            "auth.session.read",
            "farmers.read",
            "farmers.write",
            "farms.read",
            "farms.write",
            "cooperatives.read",
            "mills.read",
            "mills.write",
            "vehicles.read",
            "vehicles.write",
            "drivers.read",
            "drivers.write",
            "prices.read",
            "prices.create",
            "prices.submit",
            "prices.verify",
            "prices.publish",
            "prices.revoke",
            "receipts.read",
            "contracts.read",
            "contracts.write",
            "quotas.reserve",
            "quotas.consume",
            "quotas.release",
            "delivery_orders.read",
            "delivery_orders.create",
            "delivery_orders.issue",
            "delivery_orders.transition",
            "delivery_orders.cancel",
            "mill_tickets.read",
            "reconciliations.read",
            "reconciliations.calculate",
            "reconciliations.review",
            "reconciliations.resolve",
            "allocations.compute",
            "invoices.read",
            "files.upload",
            "files.read",
            "admin.rules.read",
            "admin.rules.write",
            "reports.operational.read",
        }
    ),
    RoleCode.PERUMDA_FINANCE: frozenset(
        {
            "public.prices.read",
            "public.mills.read",
            "public.profile.read",
            "auth.session.read",
            "cooperatives.read",
            "mills.read",
            "prices.read",
            "receipts.read",
            "contracts.read",
            "delivery_orders.read",
            "mill_tickets.read",
            "reconciliations.read",
            "allocations.compute",
            "invoices.read",
            "invoices.create",
            "invoices.verify",
            "invoices.issue",
            "payments.read",
            "payments.record",
            "payments.verify",
            "files.upload",
            "files.read",
            "reports.operational.read",
            "reports.finance.read",
        }
    ),
    RoleCode.MILL_OPERATOR: frozenset(
        {
            "public.prices.read",
            "public.mills.read",
            "public.profile.read",
            "auth.session.read",
            "mills.read",
            "vehicles.read",
            "delivery_orders.read",
            "delivery_orders.verify_arrival",
            "mill_tickets.read",
            "mill_tickets.create",
            "mill_tickets.verify",
            "files.upload",
            "files.read",
            "reports.operational.read",
        }
    ),
    RoleCode.DIRECTOR: frozenset(
        {
            "public.prices.read",
            "public.mills.read",
            "public.profile.read",
            "auth.session.read",
            "farmers.read",
            "farms.read",
            "cooperatives.read",
            "mills.read",
            "prices.read",
            "prices.verify",
            "receipts.read",
            "contracts.read",
            "contracts.approve",
            "delivery_orders.read",
            "mill_tickets.read",
            "reconciliations.read",
            "reconciliations.resolve",
            "invoices.read",
            "invoices.verify",
            "payments.read",
            "payments.approve",
            "files.read",
            "admin.rules.read",
            "admin.rules.write",
            "admin.audit.read",
            "reports.operational.read",
            "reports.finance.read",
        }
    ),
    RoleCode.SYSTEM_ADMIN: frozenset(
        {
            "auth.session.read",
            "admin.users.read",
            "admin.users.write",
            "admin.rules.read",
            "admin.rules.write",
            "admin.audit.read",
            "admin.health.read",
        }
    ),
}


ROLE_ALLOWED_SCOPES: dict[RoleCode, frozenset[ScopeType]] = {
    RoleCode.FARMER: frozenset({ScopeType.FARMER}),
    RoleCode.COOPERATIVE_OPERATOR: frozenset({ScopeType.COOPERATIVE}),
    RoleCode.PERUMDA_OPERATIONS: frozenset({ScopeType.PERUMDA_GLOBAL}),
    RoleCode.PERUMDA_FINANCE: frozenset({ScopeType.PERUMDA_GLOBAL}),
    RoleCode.MILL_OPERATOR: frozenset({ScopeType.MILL}),
    RoleCode.DIRECTOR: frozenset({ScopeType.PERUMDA_GLOBAL}),
    RoleCode.SYSTEM_ADMIN: frozenset({ScopeType.PERUMDA_GLOBAL}),
}


# Business approval permissions strictly denied to SYSTEM_ADMIN (BR-SYS-002).
APPROVER_FORBIDDEN_PERMISSIONS: frozenset[str] = frozenset(
    {
        "prices.verify",
        "contracts.approve",
        "reconciliations.resolve",
        "invoices.verify",
        "payments.approve",
        "payments.verify",
    }
)


def is_non_approver_admin(roles: tuple[RoleCode, ...] | list[RoleCode]) -> bool:
    """Return True when actor holds SYSTEM_ADMIN (BR-SYS-002)."""
    return RoleCode.SYSTEM_ADMIN in roles


def compute_effective_permissions(
    roles: tuple[RoleCode, ...], db_permissions: frozenset[str]
) -> frozenset[str]:
    """Compute effective permissions from active role grants with BR-SYS-002 guardrail."""
    effective = set(db_permissions)
    if not effective:
        for role in roles:
            effective.update(ROLE_PERMISSIONS_MAP.get(role, frozenset()))
    if is_non_approver_admin(roles):
        # Enforce BR-SYS-002 even if DB rows were altered improperly.
        effective.difference_update(APPROVER_FORBIDDEN_PERMISSIONS)
    return frozenset(effective)


def validate_scope_binding(
    scope_type: ScopeType,
    farmer_id: UUID | None,
    cooperative_id: UUID | None,
    mill_id: UUID | None,
) -> None:
    """Ensure exactly the matching FK target is populated for a given scope_type (DBD §6.6)."""
    if scope_type == ScopeType.FARMER:
        if farmer_id is None or cooperative_id is not None or mill_id is not None:
            raise AppError(
                ErrorCode.VAL_INVALID_FORMAT,
                "Scope FARMER wajib menunjuk tepat satu farmer_id tanpa target lain.",
            )
    elif scope_type == ScopeType.COOPERATIVE:
        if cooperative_id is None or farmer_id is not None or mill_id is not None:
            raise AppError(
                ErrorCode.VAL_INVALID_FORMAT,
                "Scope COOPERATIVE wajib menunjuk tepat satu cooperative_id tanpa target lain.",
            )
    elif scope_type == ScopeType.MILL:
        if mill_id is None or farmer_id is not None or cooperative_id is not None:
            raise AppError(
                ErrorCode.VAL_INVALID_FORMAT,
                "Scope MILL wajib menunjuk tepat satu mill_id tanpa target lain.",
            )
    elif scope_type == ScopeType.PERUMDA_GLOBAL:
        if farmer_id is not None or cooperative_id is not None or mill_id is not None:
            raise AppError(
                ErrorCode.VAL_INVALID_FORMAT,
                "Scope PERUMDA_GLOBAL tidak boleh terikat ke farmer_id/cooperative_id/mill_id.",
            )


def validate_role_scope_assignment(
    role_code: RoleCode,
    scope_type: ScopeType,
    farmer_id: UUID | None,
    cooperative_id: UUID | None,
    mill_id: UUID | None,
) -> None:
    """Enforce allowed role-to-scope compatibility and target ID invariants."""
    validate_scope_binding(scope_type, farmer_id, cooperative_id, mill_id)
    allowed_scopes = ROLE_ALLOWED_SCOPES[role_code]
    if scope_type not in allowed_scopes:
        raise AppError(
            ErrorCode.VAL_INVALID_FORMAT,
            f"Peran {role_code.value} tidak diizinkan menggunakan scope {scope_type.value}.",
        )


def validate_new_password(raw_password: str, username: str) -> None:
    """Validate plaintext password policy prior to Argon2id hashing."""
    stripped = raw_password.strip()
    if len(stripped) < 10:
        raise AppError(
            ErrorCode.VAL_INVALID_FORMAT,
            "Kata sandi minimal 10 karakter non-spasi.",
        )
    if raw_password.lower() == username.lower():
        raise AppError(
            ErrorCode.VAL_INVALID_FORMAT,
            "Kata sandi tidak boleh sama dengan username.",
        )


def check_login_account_status(status: AccountStatus) -> None:
    """Reject INACTIVE or LOCKED accounts with generic 401 message (TRD §12.3)."""
    if status != AccountStatus.ACTIVE:
        raise AppError(ErrorCode.AUTH_INVALID_CREDENTIALS)


def assert_authorized(
    principal: AuthenticatedPrincipal,
    *,
    allowed_roles: tuple[RoleCode, ...] | frozenset[RoleCode] | None = None,
    required_permissions: tuple[str, ...] | frozenset[str] = (),
) -> None:
    """Default-deny server RBAC check with explicit BR-SYS-002 approver ban."""
    if is_non_approver_admin(principal.roles) and any(
        perm in APPROVER_FORBIDDEN_PERMISSIONS for perm in required_permissions
    ):
        raise AppError(ErrorCode.AUTH_OPERATION_FORBIDDEN)

    if allowed_roles is not None and not any(role in allowed_roles for role in principal.roles):
        if is_non_approver_admin(principal.roles) and any(
            role != RoleCode.SYSTEM_ADMIN for role in allowed_roles
        ):
            raise AppError(ErrorCode.AUTH_OPERATION_FORBIDDEN)
        raise AppError(ErrorCode.AUTH_ACCESS_DENIED)

    for perm in required_permissions:
        if perm not in principal.permissions:
            raise AppError(ErrorCode.AUTH_ACCESS_DENIED)


def has_global_scope(principal: AuthenticatedPrincipal) -> bool:
    """Return True when principal holds active PERUMDA_GLOBAL isolation grant."""
    return any(s.scope_type == ScopeType.PERUMDA_GLOBAL for s in principal.access_scopes)


def allowed_farmer_ids(principal: AuthenticatedPrincipal) -> set[UUID]:
    """Return assigned farmer UUIDs for FARMER-scoped principals."""
    return {
        s.farmer_id
        for s in principal.access_scopes
        if s.scope_type == ScopeType.FARMER and s.farmer_id is not None
    }


def allowed_cooperative_ids(principal: AuthenticatedPrincipal) -> set[UUID]:
    """Return assigned cooperative UUIDs for COOPERATIVE-scoped principals."""
    return {
        s.cooperative_id
        for s in principal.access_scopes
        if s.scope_type == ScopeType.COOPERATIVE and s.cooperative_id is not None
    }


def allowed_mill_ids(principal: AuthenticatedPrincipal) -> set[UUID]:
    """Return assigned mill UUIDs for MILL-scoped principals."""
    return {
        s.mill_id
        for s in principal.access_scopes
        if s.scope_type == ScopeType.MILL and s.mill_id is not None
    }


def assert_farmer_scope(principal: AuthenticatedPrincipal, farmer_id: UUID) -> None:
    """Reject cross-farmer access unless global or authorized cooperative handler."""
    if has_global_scope(principal):
        return
    if farmer_id not in allowed_farmer_ids(principal):
        raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)


def assert_cooperative_scope(principal: AuthenticatedPrincipal, cooperative_id: UUID) -> None:
    """Reject cross-cooperative access for COOPERATIVE-scoped users."""
    if has_global_scope(principal):
        return
    if cooperative_id not in allowed_cooperative_ids(principal):
        raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)


def assert_mill_scope(
    principal: AuthenticatedPrincipal,
    mill_id: UUID,
    *,
    error_code: ErrorCode = ErrorCode.AUTH_SCOPE_FORBIDDEN,
) -> None:
    """Reject cross-mill access for MILL-scoped operators."""
    if has_global_scope(principal):
        return
    if mill_id not in allowed_mill_ids(principal):
        raise AppError(error_code)
