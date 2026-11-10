"""Pure pricing invariants: SM-01 transitions, Maker!=Checker SOD-01, period overlap, Decimals."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from uuid import UUID

from app.core.exceptions import AppError, ErrorCode
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal
from app.modules.identity_access.domain.rules import is_non_approver_admin
from app.modules.pricing.domain.entities import PriceQuoteStatus

_PRICE_PATTERN = re.compile(r"^-?\d{1,16}\.\d{2}$")


@dataclass(frozen=True, slots=True)
class SeedPriceSourceSpec:
    code: str
    name: str
    source_type: str
    description: str


@dataclass(frozen=True, slots=True)
class SeedPriceCategorySpec:
    code: str
    name: str
    description: str
    unit: str
    quality_basis: str
    age_group: str | None


CANONICAL_PRICE_SOURCES: tuple[SeedPriceSourceSpec, ...] = (
    SeedPriceSourceSpec(
        "DISBUN_RIAU",
        "Dinas Perkebunan Provinsi Riau",
        "DISBUN",
        "Penetapan harga resmi berkala Disbun Riau",
    ),
    SeedPriceSourceSpec(
        "MILL_OFFICIAL",
        "Informasi Resmi PKS Mitra",
        "MILL_OFFICIAL",
        "Informasi harga beli resmi dari PKS mitra Perumda",
    ),
    SeedPriceSourceSpec(
        "MILL_DOCUMENT",
        "Dokumen Papan Harga PKS",
        "MILL_DOCUMENT",
        "Surat edaran / papan harga resmi PKS mitra",
    ),
    SeedPriceSourceSpec(
        "VERIFIED_MANUAL",
        "Verifikasi Manual Petugas",
        "VERIFIED_MANUAL",
        "Input manual terverifikasi checker Perumda",
    ),
)

CANONICAL_PRICE_CATEGORIES: tuple[SeedPriceCategorySpec, ...] = (
    SeedPriceCategorySpec(
        "SWADAYA_STD",
        "TBS Sawit Swadaya Standar",
        "Kategori umum buah matang swadaya",
        "IDR/kg",
        "Buah matang panen normal, sortasi standar koperasi",
        None,
    ),
    SeedPriceCategorySpec(
        "PLASMA_KONTRAK",
        "TBS Mitra Plasma (Non-Comparable)",
        "Kategori khusus mitra plasma",
        "IDR/kg",
        "Kontrak kemitraan plasma khusus, tidak dibandingkan langsung dg swadaya",
        "10-20 tahun",
    ),
    SeedPriceCategorySpec(
        "DISBUN_10_20",
        "Referensi Disbun Umur 10-20 Tahun",
        "Kategori acuan Disbun kelompok umur produktif",
        "IDR/kg",
        "Penetapan indeks K resmi Disbun Riau",
        "10-20 tahun",
    ),
)


def parse_positive_price_per_kg(raw: str) -> Decimal:
    """Validate DecimalPriceString format and enforce strictly positive IDR/kg (BR-PRC-001)."""
    stripped = raw.strip()
    if not _PRICE_PATTERN.match(stripped):
        raise AppError(
            ErrorCode.VAL_INVALID_DECIMAL_PRECISION,
            details=[
                {
                    "field": "price_per_kg",
                    "reason": (
                        "Gunakan format angka desimal 2 angka di belakang koma (mis. 2920.00)."
                    ),
                    "code": ErrorCode.VAL_INVALID_DECIMAL_PRECISION.value,
                }
            ],
        )
    try:
        value = Decimal(stripped)
    except InvalidOperation as exc:
        raise AppError(ErrorCode.VAL_INVALID_DECIMAL_PRECISION) from exc
    if not value.is_finite() or value <= Decimal("0"):
        raise AppError(ErrorCode.PRICE_INVALID_AMOUNT)
    return value


def validate_price_period(effective_from: datetime, effective_until: datetime | None) -> None:
    """Reject inverted or zero-length price validity windows (PRICE_INVALID_PERIOD)."""
    if effective_until is not None and effective_until <= effective_from:
        raise AppError(ErrorCode.PRICE_INVALID_PERIOD)


def assert_can_edit_draft(status: PriceQuoteStatus) -> None:
    """Only DRAFT quotes may be edited; PUBLISHED triggers PRICE_ALREADY_PUBLISHED."""
    if status == PriceQuoteStatus.PUBLISHED:
        raise AppError(ErrorCode.PRICE_ALREADY_PUBLISHED)
    if status != PriceQuoteStatus.DRAFT:
        raise AppError(
            ErrorCode.PRICE_INVALID_STATE_TRANSITION,
            details={"current_status": status.value, "requested_action": "UPDATE_DRAFT"},
        )


def assert_can_submit(status: PriceQuoteStatus) -> None:
    if status != PriceQuoteStatus.DRAFT:
        raise AppError(
            ErrorCode.PRICE_INVALID_STATE_TRANSITION,
            details={"current_status": status.value, "requested_action": "SUBMIT"},
        )


def assert_can_verify(
    status: PriceQuoteStatus, *, submitted_by: UUID, actor: AuthenticatedPrincipal
) -> None:
    """Enforce SM-01 VERIFY precondition + SOD-01 Maker!=Checker + BR-SYS-002."""
    if is_non_approver_admin(actor.roles):
        raise AppError(ErrorCode.AUTH_OPERATION_FORBIDDEN)
    if status != PriceQuoteStatus.PENDING_VERIFICATION:
        raise AppError(
            ErrorCode.PRICE_INVALID_STATE_TRANSITION,
            details={"current_status": status.value, "requested_action": "VERIFY"},
        )
    if actor.user_id == submitted_by:
        raise AppError(
            ErrorCode.AUTH_CONFLICT_OF_DUTIES,
            details={"rule": "SOD-01", "submitted_by": str(submitted_by)},
        )


def assert_can_publish(status: PriceQuoteStatus) -> None:
    """Enforce VERIFIED status before publication (PRICE_NOT_VERIFIED / ALREADY_PUBLISHED)."""
    if status == PriceQuoteStatus.PUBLISHED:
        raise AppError(ErrorCode.PRICE_ALREADY_PUBLISHED)
    if status != PriceQuoteStatus.VERIFIED:
        raise AppError(
            ErrorCode.PRICE_NOT_VERIFIED,
            details={"current_status": status.value},
        )


def assert_can_revoke(status: PriceQuoteStatus) -> None:
    if status != PriceQuoteStatus.PUBLISHED:
        raise AppError(
            ErrorCode.PRICE_INVALID_STATE_TRANSITION,
            details={"current_status": status.value, "requested_action": "REVOKE"},
        )


def periods_overlap(
    start_a: datetime,
    end_a: datetime | None,
    start_b: datetime,
    end_b: datetime | None,
) -> bool:
    """Return True when half-open validity intervals [start, end) intersect."""
    a_before_b = end_a is not None and end_a <= start_b
    b_before_a = end_b is not None and end_b <= start_a
    return not (a_before_b or b_before_a)
