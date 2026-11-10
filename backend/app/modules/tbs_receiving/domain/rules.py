"""Pure business calculations and invariants for weighing, grading, and SM-02 (DBD §9)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from app.core.exceptions import AppError, ErrorCode
from app.core.weight_primitives import parse_weighing_pair
from app.modules.tbs_receiving.domain.entities import GradingDeductionType, ReceiptStatus

_PCT_OR_VAL_PATTERN = re.compile(r"^-?\d{1,12}\.\d{1,4}$")

__all__ = [
    "ComputedGradingItem",
    "GradingInputItem",
    "assert_can_cancel_receipt",
    "assert_receipt_mutable",
    "compute_grading_deductions",
    "parse_weighing_pair",
]


@dataclass(frozen=True, slots=True)
class GradingInputItem:
    grading_category: str
    measurement_value_raw: str
    deduction_type: GradingDeductionType
    deduction_value_raw: str
    calculation_basis: str
    notes: str | None


@dataclass(frozen=True, slots=True)
class ComputedGradingItem:
    grading_category: str
    measurement_value: Decimal
    deduction_type: GradingDeductionType
    deduction_value: Decimal
    deduction_weight_kg: Decimal | None
    deduction_amount: Decimal | None
    calculation_basis: str
    notes: str | None


def _parse_grading_decimal(raw: str, field_name: str) -> Decimal:
    cleaned = raw.strip()
    if not _PCT_OR_VAL_PATTERN.match(cleaned):
        raise AppError(
            ErrorCode.TBS_INVALID_GRADING_DEDUCTION,
            details=[
                {
                    "field": field_name,
                    "reason": "Format angka grading tidak valid.",
                    "code": ErrorCode.TBS_INVALID_GRADING_DEDUCTION.value,
                }
            ],
        )
    try:
        val = Decimal(cleaned)
    except InvalidOperation as exc:
        raise AppError(ErrorCode.TBS_INVALID_GRADING_DEDUCTION) from exc
    if not val.is_finite() or val < Decimal("0"):
        raise AppError(ErrorCode.TBS_INVALID_GRADING_DEDUCTION)
    return val


def compute_grading_deductions(
    *,
    base_net_weight_kg: Decimal,
    items: list[GradingInputItem],
) -> tuple[list[ComputedGradingItem], Decimal]:
    """Compute weight/value deductions strictly from raw net weight to prevent double deduction."""
    seen_categories: set[str] = set()
    computed: list[ComputedGradingItem] = []
    total_weight_deduction = Decimal("0.000")

    for item in items:
        cat_clean = " ".join(item.grading_category.strip().split())
        cat_key = cat_clean.lower()
        if not cat_clean or cat_key in seen_categories:
            raise AppError(
                ErrorCode.TBS_INVALID_GRADING_DEDUCTION,
                details=[
                    {
                        "field": "grading_category",
                        "reason": (
                            "Kategori grading kosong atau terduplikasi (cegah potongan ganda)."
                        ),
                        "code": ErrorCode.TBS_INVALID_GRADING_DEDUCTION.value,
                    }
                ],
            )
        seen_categories.add(cat_key)

        measurement = _parse_grading_decimal(item.measurement_value_raw, "measurement_value")
        ded_val = _parse_grading_decimal(item.deduction_value_raw, "deduction_value")
        basis = item.calculation_basis.strip()
        if not basis:
            basis = "NET_WEIGHT_BEFORE_GRADING"
        if (
            item.deduction_type
            in (
                GradingDeductionType.WEIGHT_PERCENT,
                GradingDeductionType.WEIGHT_KG,
            )
            and basis != "NET_WEIGHT_BEFORE_GRADING"
        ):
            raise AppError(
                ErrorCode.TBS_INVALID_GRADING_DEDUCTION,
                details=[
                    {
                        "field": "calculation_basis",
                        "reason": (
                            "Potongan berat harus dihitung dari NET_WEIGHT_BEFORE_GRADING "
                            "untuk mencegah potongan ganda."
                        ),
                        "code": ErrorCode.TBS_INVALID_GRADING_DEDUCTION.value,
                    }
                ],
            )
        if item.deduction_type == GradingDeductionType.VALUE_AMOUNT and basis not in (
            "NET_WEIGHT_BEFORE_GRADING",
            "FIXED_AMOUNT",
        ):
            raise AppError(
                ErrorCode.TBS_INVALID_GRADING_DEDUCTION,
                details=[
                    {
                        "field": "calculation_basis",
                        "reason": "Dasar potongan nilai tidak valid.",
                        "code": ErrorCode.TBS_INVALID_GRADING_DEDUCTION.value,
                    }
                ],
            )

        ded_weight: Decimal | None = None
        ded_amount: Decimal | None = None

        if item.deduction_type == GradingDeductionType.WEIGHT_PERCENT:
            if ded_val > Decimal("100"):
                raise AppError(ErrorCode.TBS_INVALID_GRADING_DEDUCTION)
            ded_weight = (base_net_weight_kg * ded_val / Decimal("100")).quantize(
                Decimal("0.001"), rounding=ROUND_HALF_UP
            )
            total_weight_deduction += ded_weight
        elif item.deduction_type == GradingDeductionType.WEIGHT_KG:
            ded_weight = ded_val.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
            total_weight_deduction += ded_weight
        elif item.deduction_type == GradingDeductionType.VALUE_AMOUNT:
            ded_amount = ded_val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        computed.append(
            ComputedGradingItem(
                grading_category=cat_clean,
                measurement_value=measurement.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
                deduction_type=item.deduction_type,
                deduction_value=ded_val.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
                deduction_weight_kg=ded_weight,
                deduction_amount=ded_amount,
                calculation_basis=basis,
                notes=item.notes.strip() if item.notes else None,
            )
        )

    if total_weight_deduction > base_net_weight_kg:
        raise AppError(
            ErrorCode.TBS_INVALID_GRADING_DEDUCTION,
            details=[
                {
                    "field": "items",
                    "reason": "Akumulasi potongan berat melebihi berat netto timbangan.",
                    "code": ErrorCode.TBS_INVALID_GRADING_DEDUCTION.value,
                }
            ],
        )

    after_grading = (base_net_weight_kg - total_weight_deduction).quantize(
        Decimal("0.001"), rounding=ROUND_HALF_UP
    )
    return computed, after_grading


def assert_receipt_mutable(status: ReceiptStatus) -> None:
    """Enforce BSD §8.4 lock once allocated, shipped, closed, or cancelled."""
    if status in (ReceiptStatus.ALLOCATED, ReceiptStatus.SHIPPED, ReceiptStatus.CLOSED):
        raise AppError(
            ErrorCode.TBS_RECEIPT_LOCKED,
            details={"current_status": status.value, "delivery_order_id": None},
        )
    if status == ReceiptStatus.CANCELLED:
        raise AppError(
            ErrorCode.TBS_INVALID_STATE_TRANSITION,
            details={"current_status": status.value},
        )


def assert_can_cancel_receipt(status: ReceiptStatus) -> None:
    if status in (ReceiptStatus.ALLOCATED, ReceiptStatus.SHIPPED, ReceiptStatus.CLOSED):
        raise AppError(
            ErrorCode.TBS_RECEIPT_LOCKED,
            details={"current_status": status.value, "delivery_order_id": None},
        )
    if status not in (ReceiptStatus.DRAFT, ReceiptStatus.VALIDATED):
        raise AppError(
            ErrorCode.TBS_INVALID_STATE_TRANSITION,
            details={"current_status": status.value},
        )
