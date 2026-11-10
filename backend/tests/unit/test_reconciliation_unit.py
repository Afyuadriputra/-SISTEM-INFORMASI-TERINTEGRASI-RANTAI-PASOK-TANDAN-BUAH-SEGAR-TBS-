"""Unit tests for Reconciliation math, negative surplus BR-REC-009, SOD-03 & allocations (B8)."""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest
from app.core.exceptions import AppError, ErrorCode
from app.modules.reconciliation.domain.entities import (
    ReconciliationStatus,
    WeightBasis,
)
from app.modules.reconciliation.domain.rules import (
    AllocationLineInput,
    assert_can_resolve_dispute,
    assert_equivalent_weight_basis,
    compute_proportional_allocations,
    compute_reconciliation_diff,
)


def test_reconciliation_diff_normal_exceeded_and_negative_surplus() -> None:
    matched = compute_reconciliation_diff(
        origin_weight_kg=Decimal("10000.000"),
        mill_weight_kg=Decimal("9900.000"),
        tolerance_percent=Decimal("1.5000"),
    )
    assert matched.difference_weight_kg == Decimal("100.000")
    assert matched.difference_percent == Decimal("1.0000")
    assert matched.is_negative_difference is False
    assert matched.resulting_status == ReconciliationStatus.MATCHED

    exceeded = compute_reconciliation_diff(
        origin_weight_kg=Decimal("10000.000"),
        mill_weight_kg=Decimal("9600.000"),
        tolerance_percent=Decimal("1.5000"),
    )
    assert exceeded.difference_weight_kg == Decimal("400.000")
    assert exceeded.difference_percent == Decimal("4.0000")
    assert exceeded.resulting_status == ReconciliationStatus.DISPUTE_HOLD

    negative = compute_reconciliation_diff(
        origin_weight_kg=Decimal("10000.000"),
        mill_weight_kg=Decimal("10150.000"),
        tolerance_percent=Decimal("1.5000"),
    )
    assert negative.difference_weight_kg == Decimal("-150.000")
    assert negative.is_negative_difference is True
    assert negative.resulting_status == ReconciliationStatus.DISPUTE_HOLD


def test_zero_origin_unequal_basis_and_sod03_guards() -> None:
    with pytest.raises(AppError) as exc_basis:
        assert_equivalent_weight_basis(WeightBasis.NET_WEIGHT_AFTER_GRADING)
    assert exc_basis.value.code == ErrorCode.REC_INVALID_WEIGHT_BASIS

    with pytest.raises(AppError) as exc_zero:
        compute_reconciliation_diff(
            origin_weight_kg=Decimal("0.000"),
            mill_weight_kg=Decimal("1000.000"),
            tolerance_percent=Decimal("1.5000"),
        )
    assert exc_zero.value.code == ErrorCode.REC_INVALID_WEIGHT_BASIS

    rev_id = uuid4()
    with pytest.raises(AppError) as exc_sod:
        assert_can_resolve_dispute(
            current_status=ReconciliationStatus.UNDER_REVIEW,
            reviewer_ids={rev_id},
            actor_id=rev_id,
            non_approver_admin=False,
        )
    assert exc_sod.value.code == ErrorCode.AUTH_CONFLICT_OF_DUTIES

    assert_can_resolve_dispute(
        current_status=ReconciliationStatus.UNDER_REVIEW,
        reviewer_ids={rev_id},
        actor_id=uuid4(),
        non_approver_admin=False,
    )


def test_proportional_allocations_preserve_exact_totals_even_on_odd_splits() -> None:
    lines = [
        AllocationLineInput(uuid4(), uuid4(), "A", Decimal("3000.000")),
        AllocationLineInput(uuid4(), uuid4(), "B", Decimal("2000.000")),
        AllocationLineInput(uuid4(), uuid4(), "C", Decimal("5000.000")),
    ]
    res = compute_proportional_allocations(
        lines=lines,
        target_total_weight_kg=Decimal("9900.000"),
        unit_price_per_kg=Decimal("2850.00"),
    )
    assert [r.agreed_weight_kg for r in res] == [
        Decimal("2970.000"),
        Decimal("1980.000"),
        Decimal("4950.000"),
    ]
    assert sum(r.net_amount for r in res) == Decimal("28215000.00")

    # Test indivisible weight rounding residue stability (3 equal thirds of 1000.000 kg -> 333.333 + 333.333 + 333.334).
    thirds = [AllocationLineInput(uuid4(), uuid4(), f"F{i}", Decimal("1000.000")) for i in range(3)]
    res_thirds = compute_proportional_allocations(
        lines=thirds,
        target_total_weight_kg=Decimal("1000.000"),
        unit_price_per_kg=Decimal("2850.00"),
    )
    assert sum(r.agreed_weight_kg for r in res_thirds) == Decimal("1000.000")
    assert sum(r.net_amount for r in res_thirds) == Decimal("2850000.00")
