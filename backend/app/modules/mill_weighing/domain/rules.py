"""Pure domain validation for Mill Tickets, Grading & SM-06 invariants."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from app.core.exceptions import AppError, ErrorCode
from app.modules.mill_weighing.domain.entities import (
    MillGradingDeductionType,
    MillTicketStatus,
)

_VAL_PATTERN = re.compile(r"^-?\d{1,12}\.\d{1,4}$")


@dataclass(frozen=True, slots=True)
class MillGradingInput:
    grading_category: str
    deduction_type: MillGradingDeductionType
    deduction_value_raw: str
    calculation_basis: str
    notes: str | None


@dataclass(frozen=True, slots=True)
class ValidatedMillGradingItem:
    grading_category: str
    deduction_type: MillGradingDeductionType
    deduction_value: Decimal
    calculation_basis: str
    notes: str | None


def validate_mill_grading_items(items: list[MillGradingInput]) -> list[ValidatedMillGradingItem]:
    """Ensure non-negative, non-duplicate mill grading entries without double deduction."""
    seen: set[str] = set()
    validated: list[ValidatedMillGradingItem] = []
    for item in items:
        cat_clean = " ".join(item.grading_category.strip().split())
        key = cat_clean.lower()
        if not cat_clean or key in seen:
            raise AppError(
                ErrorCode.TBS_INVALID_GRADING_DEDUCTION,
                details=[
                    {
                        "field": "grading_category",
                        "reason": "Kategori grading PKS kosong atau terduplikasi.",
                        "code": ErrorCode.TBS_INVALID_GRADING_DEDUCTION.value,
                    }
                ],
            )
        seen.add(key)
        cleaned = item.deduction_value_raw.strip()
        if not _VAL_PATTERN.match(cleaned):
            raise AppError(
                ErrorCode.TBS_INVALID_GRADING_DEDUCTION,
                details=[
                    {
                        "field": "deduction_value",
                        "reason": "Format nilai potongan grading PKS tidak valid.",
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
        if item.deduction_type == MillGradingDeductionType.WEIGHT_PERCENT and val > Decimal("100"):
            raise AppError(ErrorCode.TBS_INVALID_GRADING_DEDUCTION)

        basis = item.calculation_basis.strip() or "MILL_NET_WEIGHT"
        if item.deduction_type in (
            MillGradingDeductionType.WEIGHT_PERCENT,
            MillGradingDeductionType.WEIGHT_KG,
        ) and basis not in ("MILL_NET_WEIGHT", "NET_WEIGHT_BEFORE_GRADING"):
            raise AppError(ErrorCode.TBS_INVALID_GRADING_DEDUCTION)

        validated.append(
            ValidatedMillGradingItem(
                grading_category=cat_clean,
                deduction_type=item.deduction_type,
                deduction_value=val.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
                calculation_basis=basis,
                notes=item.notes.strip() if item.notes else None,
            )
        )
    return validated


def assert_ticket_can_revise(*, is_current: bool, do_completed: bool) -> None:
    if not is_current or do_completed:
        raise AppError(ErrorCode.MILL_TICKET_ALREADY_FINAL)


def assert_ticket_can_verify(
    *, is_current: bool, status: MillTicketStatus, do_completed: bool
) -> None:
    if not is_current or do_completed:
        raise AppError(ErrorCode.MILL_TICKET_ALREADY_FINAL)
    if status != MillTicketStatus.SUBMITTED:
        raise AppError(ErrorCode.MILL_TICKET_ALREADY_FINAL)
