"""Pure reporting date-range validation, scope keys, and BR-MRG-005 margin helpers."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from app.core.exceptions import AppError, ErrorCode
from app.modules.identity_access.domain.entities import RoleCode

FINANCE_SIMULATION_MARGIN_LABEL = "Kontribusi Kotor Niaga (Data Simulasi - Bukan Laba Bersih)"
REPORTING_SIMULATION_NOTICE = (
    "Metrik dashboard mengecualikan transaksi CANCELLED dan menandai "
    "angka simulasi sampai SOP disahkan."
)


def resolve_report_date_window(
    date_from: date | None,
    date_to: date | None,
    *,
    today: date | None = None,
) -> tuple[date, date]:
    """Resolve inclusive reporting date window and reject inverted bounds (422)."""
    anchor = today or datetime.now(UTC).date()
    end_d = date_to or anchor
    start_d = date_from or (end_d - timedelta(days=30))
    if start_d > end_d:
        raise AppError(
            ErrorCode.VAL_INVALID_DATE_RANGE,
            details=[
                {
                    "field": "date_from",
                    "reason": "Tanggal awal tidak boleh melewati tanggal akhir.",
                    "code": ErrorCode.VAL_INVALID_DATE_RANGE.value,
                }
            ],
        )
    return start_d, end_d


def compute_gross_contribution_simulation(
    *,
    ar_billed_total: Decimal,
    ap_approved_unpaid_total: Decimal,
    ap_verified_paid_total: Decimal,
) -> Decimal | None:
    """Compute simulation gross contribution only when both revenue and cost exist (BR-MRG-005)."""
    total_ap_obligations = ap_approved_unpaid_total + ap_verified_paid_total
    if ar_billed_total <= Decimal("0.00") or total_ap_obligations <= Decimal("0.00"):
        return None
    return (ar_billed_total - total_ap_obligations).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def build_report_scope_key(
    *,
    role_code: RoleCode,
    farmer_ids: set[UUID] | None,
    coop_ids: set[UUID] | None,
    mill_ids: set[UUID] | None,
) -> str:
    """Build deterministic scope identifier so cached dashboards never leak across roles/tenants."""
    f_part = ",".join(sorted(str(x) for x in farmer_ids)) if farmer_ids is not None else "ALL"
    c_part = ",".join(sorted(str(x) for x in coop_ids)) if coop_ids is not None else "ALL"
    m_part = ",".join(sorted(str(x) for x in mill_ids)) if mill_ids is not None else "ALL"
    return f"{role_code.value}:f={f_part}:c={c_part}:m={m_part}"
