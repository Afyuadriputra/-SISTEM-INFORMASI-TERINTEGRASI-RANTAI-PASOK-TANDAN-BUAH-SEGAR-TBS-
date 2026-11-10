"""Pure business formulas & invariants for SM-07, SM-08, BR-REC-009, SOD-03 & Allocations."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from uuid import UUID

from app.core.exceptions import AppError, ErrorCode
from app.modules.reconciliation.domain.entities import (
    DisputeDecision,
    ReconciliationStatus,
    WeightBasis,
)


@dataclass(frozen=True, slots=True)
class ReconciliationComputation:
    origin_weight_kg: Decimal
    mill_weight_kg: Decimal
    difference_weight_kg: Decimal
    difference_percent: Decimal
    is_negative_difference: bool
    resulting_status: ReconciliationStatus


@dataclass(frozen=True, slots=True)
class AllocationLineInput:
    receipt_id: UUID
    farmer_id: UUID
    farmer_name: str
    origin_weight_kg: Decimal


@dataclass(frozen=True, slots=True)
class ComputedAllocationLine:
    receipt_id: UUID
    farmer_id: UUID
    farmer_name: str
    allocation_basis_weight_kg: Decimal
    agreed_weight_kg: Decimal
    gross_amount: Decimal
    deduction_amount: Decimal
    net_amount: Decimal


def assert_equivalent_weight_basis(weight_basis: WeightBasis) -> None:
    """Enforce FR-REC-002 comparable pre-grading net weights on origin vs PKS ticket."""
    if weight_basis != WeightBasis.NET_WEIGHT_BEFORE_GRADING:
        raise AppError(ErrorCode.REC_INVALID_WEIGHT_BASIS)


def compute_reconciliation_diff(
    *,
    origin_weight_kg: Decimal,
    mill_weight_kg: Decimal,
    tolerance_percent: Decimal,
) -> ReconciliationComputation:
    """Compute canonical diff = origin - mill and detect tolerance breach or BR-REC-009 surplus."""
    if origin_weight_kg <= Decimal("0") or mill_weight_kg < Decimal("0"):
        raise AppError(ErrorCode.REC_INVALID_WEIGHT_BASIS)

    diff_kg = (origin_weight_kg - mill_weight_kg).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    diff_pct = (diff_kg / origin_weight_kg * Decimal("100")).quantize(
        Decimal("0.0001"), rounding=ROUND_HALF_UP
    )
    is_negative = diff_kg < Decimal("0")

    if is_negative or diff_pct > tolerance_percent:
        status = ReconciliationStatus.DISPUTE_HOLD
    else:
        status = ReconciliationStatus.MATCHED

    return ReconciliationComputation(
        origin_weight_kg=origin_weight_kg.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP),
        mill_weight_kg=mill_weight_kg.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP),
        difference_weight_kg=diff_kg,
        difference_percent=diff_pct,
        is_negative_difference=is_negative,
        resulting_status=status,
    )


def validate_dispute_reason(reason: str | None) -> str:
    cleaned = reason.strip() if reason else ""
    if len(cleaned) < 5:
        raise AppError(
            ErrorCode.REC_DISPUTE_REASON_REQUIRED,
            details=[
                {
                    "field": "reason",
                    "reason": (
                        "Alasan pemeriksaan atau keputusan sengketa wajib minimal 5 karakter."
                    ),
                    "code": ErrorCode.REC_DISPUTE_REASON_REQUIRED.value,
                }
            ],
        )
    return cleaned


def resolve_settlement_weight(
    *,
    decision: DisputeDecision,
    final_outcome: ReconciliationStatus,
    origin_weight_kg: Decimal,
    mill_weight_kg: Decimal,
    agreed_raw: str | None,
) -> Decimal | None:
    """Resolve authoritative final weight for SM-08 without mutating raw origin/mill records."""
    if final_outcome == ReconciliationStatus.CANCELLED:
        return None
    if decision == DisputeDecision.KEEP_ORIGIN_WEIGHT:
        return origin_weight_kg
    if decision == DisputeDecision.ACCEPT_MILL_WEIGHT:
        return mill_weight_kg
    if decision == DisputeDecision.AGREED_SETTLEMENT_WEIGHT:
        if agreed_raw is None or not agreed_raw.strip():
            raise AppError(ErrorCode.VAL_REQUIRED_FIELD)
        try:
            val = Decimal(agreed_raw.strip())
        except InvalidOperation as exc:
            raise AppError(ErrorCode.VAL_INVALID_DECIMAL_PRECISION) from exc
        if not val.is_finite() or val <= Decimal("0"):
            raise AppError(ErrorCode.REC_INVALID_WEIGHT_BASIS)
        return val.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    raise AppError(
        ErrorCode.REC_INVALID_STATE_TRANSITION,
        details={"current_status": ReconciliationStatus.UNDER_REVIEW.value},
    )


def assert_can_resolve_dispute(
    *,
    current_status: ReconciliationStatus,
    reviewer_ids: set[UUID],
    actor_id: UUID,
    non_approver_admin: bool,
) -> None:
    """Enforce SM-08 status, BR-SYS-002 approver ban, and SOD-03 checker != reviewer."""
    if non_approver_admin:
        raise AppError(ErrorCode.AUTH_OPERATION_FORBIDDEN)
    if current_status != ReconciliationStatus.UNDER_REVIEW:
        raise AppError(
            ErrorCode.REC_INVALID_STATE_TRANSITION,
            details={"current_status": current_status.value},
        )
    if actor_id in reviewer_ids:
        raise AppError(
            ErrorCode.AUTH_CONFLICT_OF_DUTIES,
            details={"sod_rule": "SOD-03"},
        )


def compute_proportional_allocations(
    *,
    lines: list[AllocationLineInput],
    target_total_weight_kg: Decimal,
    unit_price_per_kg: Decimal,
) -> list[ComputedAllocationLine]:
    """Compute exact proportional farmer shares with deterministic last-line rounding balance."""
    if not lines:
        raise AppError(ErrorCode.REC_INVALID_WEIGHT_BASIS)
    total_basis = sum((ln.origin_weight_kg for ln in lines), start=Decimal("0.000"))
    if total_basis <= Decimal("0") or target_total_weight_kg <= Decimal("0"):
        raise AppError(ErrorCode.REC_INVALID_WEIGHT_BASIS)

    total_money = (target_total_weight_kg * unit_price_per_kg).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    allocated_weights: list[Decimal] = []
    allocated_amounts: list[Decimal] = []

    running_w = Decimal("0.000")
    running_m = Decimal("0.00")

    for idx, ln in enumerate(lines):
        if idx < len(lines) - 1:
            share_w = (target_total_weight_kg * ln.origin_weight_kg / total_basis).quantize(
                Decimal("0.001"), rounding=ROUND_HALF_UP
            )
            share_m = (share_w * unit_price_per_kg).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            running_w += share_w
            running_m += share_m
        else:
            share_w = (target_total_weight_kg - running_w).quantize(
                Decimal("0.001"), rounding=ROUND_HALF_UP
            )
            share_m = (total_money - running_m).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        allocated_weights.append(share_w)
        allocated_amounts.append(share_m)

    sum_w = sum(allocated_weights, start=Decimal("0.000"))
    sum_m = sum(allocated_amounts, start=Decimal("0.00"))
    if sum_w != target_total_weight_kg or sum_m != total_money:
        raise AppError(
            ErrorCode.REC_ALLOCATION_IMBALANCE,
            details={
                "expected_total": f"{total_money:.2f}",
                "allocated_total": f"{sum_m:.2f}",
            },
        )
    if any(w < Decimal("0") for w in allocated_weights) or any(
        m < Decimal("0") for m in allocated_amounts
    ):
        raise AppError(
            ErrorCode.REC_ALLOCATION_IMBALANCE,
            details={
                "expected_total": f"{total_money:.2f}",
                "allocated_total": f"{sum_m:.2f}",
            },
        )

    return [
        ComputedAllocationLine(
            receipt_id=ln.receipt_id,
            farmer_id=ln.farmer_id,
            farmer_name=ln.farmer_name,
            allocation_basis_weight_kg=ln.origin_weight_kg.quantize(
                Decimal("0.001"), rounding=ROUND_HALF_UP
            ),
            agreed_weight_kg=allocated_weights[i],
            gross_amount=allocated_amounts[i],
            deduction_amount=Decimal("0.00"),
            net_amount=allocated_amounts[i],
        )
        for i, ln in enumerate(lines)
    ]
