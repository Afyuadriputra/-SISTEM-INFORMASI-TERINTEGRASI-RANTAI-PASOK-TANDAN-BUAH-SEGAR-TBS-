"""Unit tests for pure domain weighing, grading, state transition, and idempotency primitives (B4)."""

from __future__ import annotations

from decimal import Decimal

import pytest
from app.core.exceptions import AppError, ErrorCode
from app.core.idempotency_primitives import compute_request_hash, validate_idempotency_key
from app.modules.tbs_receiving.domain.entities import GradingDeductionType, ReceiptStatus
from app.modules.tbs_receiving.domain.rules import (
    GradingInputItem,
    assert_can_cancel_receipt,
    assert_receipt_mutable,
    compute_grading_deductions,
    parse_weighing_pair,
)


def test_parse_weighing_pair_valid_exact_decimal() -> None:
    gross, tare, net = parse_weighing_pair("4200.000", "1200.000")
    assert gross == Decimal("4200.000")
    assert tare == Decimal("1200.000")
    assert net == Decimal("3000.000")


@pytest.mark.parametrize(
    ("gross_raw", "tare_raw", "expected_code"),
    [
        ("4200", "1200.000", ErrorCode.VAL_INVALID_DECIMAL_PRECISION),
        ("4200.00", "1200.000", ErrorCode.VAL_INVALID_DECIMAL_PRECISION),
        ("0.000", "0.000", ErrorCode.TBS_INVALID_WEIGHT),
        ("-100.000", "0.000", ErrorCode.TBS_INVALID_WEIGHT),
        ("4200.000", "-10.000", ErrorCode.TBS_INVALID_WEIGHT),
        ("1200.000", "1200.001", ErrorCode.TBS_INVALID_WEIGHT),
    ],
)
def test_parse_weighing_pair_rejects_invalid_weights(
    gross_raw: str, tare_raw: str, expected_code: ErrorCode
) -> None:
    with pytest.raises(AppError) as exc:
        parse_weighing_pair(gross_raw, tare_raw)
    assert exc.value.code == expected_code


def test_compute_grading_deductions_separates_weight_and_value_without_compounding() -> None:
    items = [
        GradingInputItem(
            grading_category="Buah Mentah",
            measurement_value_raw="2.0000",
            deduction_type=GradingDeductionType.WEIGHT_PERCENT,
            deduction_value_raw="2.0000",
            calculation_basis="NET_WEIGHT_BEFORE_GRADING",
            notes=None,
        ),
        GradingInputItem(
            grading_category="Tangkai Panjang",
            measurement_value_raw="15.0000",
            deduction_type=GradingDeductionType.WEIGHT_KG,
            deduction_value_raw="15.0000",
            calculation_basis="NET_WEIGHT_BEFORE_GRADING",
            notes=None,
        ),
        GradingInputItem(
            grading_category="Biaya Sortasi Tambahan",
            measurement_value_raw="1.0000",
            deduction_type=GradingDeductionType.VALUE_AMOUNT,
            deduction_value_raw="50000.00",
            calculation_basis="FIXED_AMOUNT",
            notes="Biaya administrasi",
        ),
    ]
    computed, after_grading = compute_grading_deductions(
        base_net_weight_kg=Decimal("3000.000"),
        items=items,
    )
    assert computed[0].deduction_weight_kg == Decimal("60.000")
    assert computed[0].deduction_amount is None
    assert computed[1].deduction_weight_kg == Decimal("15.000")
    assert computed[2].deduction_weight_kg is None
    assert computed[2].deduction_amount == Decimal("50000.00")
    assert after_grading == Decimal("2925.000")


def test_compute_grading_blocks_duplicate_categories_and_inconsistent_basis() -> None:
    with pytest.raises(AppError) as exc_dup:
        compute_grading_deductions(
            base_net_weight_kg=Decimal("3000.000"),
            items=[
                GradingInputItem(
                    "Buah Mentah",
                    "2.0000",
                    GradingDeductionType.WEIGHT_PERCENT,
                    "2.0000",
                    "NET_WEIGHT_BEFORE_GRADING",
                    None,
                ),
                GradingInputItem(
                    "buah  mentah",
                    "3.0000",
                    GradingDeductionType.WEIGHT_PERCENT,
                    "3.0000",
                    "NET_WEIGHT_BEFORE_GRADING",
                    None,
                ),
            ],
        )
    assert exc_dup.value.code == ErrorCode.TBS_INVALID_GRADING_DEDUCTION

    with pytest.raises(AppError) as exc_basis:
        compute_grading_deductions(
            base_net_weight_kg=Decimal("3000.000"),
            items=[
                GradingInputItem(
                    "Buah Busuk",
                    "5.0000",
                    GradingDeductionType.WEIGHT_PERCENT,
                    "5.0000",
                    "AFTER_PREVIOUS_DEDUCTION",
                    None,
                ),
            ],
        )
    assert exc_basis.value.code == ErrorCode.TBS_INVALID_GRADING_DEDUCTION


def test_receipt_mutability_and_cancel_state_guards() -> None:
    assert_receipt_mutable(ReceiptStatus.DRAFT)
    assert_receipt_mutable(ReceiptStatus.VALIDATED)
    for locked in (ReceiptStatus.ALLOCATED, ReceiptStatus.SHIPPED, ReceiptStatus.CLOSED):
        with pytest.raises(AppError) as exc:
            assert_receipt_mutable(locked)
        assert exc.value.code == ErrorCode.TBS_RECEIPT_LOCKED

    with pytest.raises(AppError) as exc_cancel_locked:
        assert_can_cancel_receipt(ReceiptStatus.ALLOCATED)
    assert exc_cancel_locked.value.code == ErrorCode.TBS_RECEIPT_LOCKED

    with pytest.raises(AppError) as exc_already_cancelled:
        assert_can_cancel_receipt(ReceiptStatus.CANCELLED)
    assert exc_already_cancelled.value.code == ErrorCode.TBS_INVALID_STATE_TRANSITION


def test_idempotency_key_and_hash_determinism() -> None:
    with pytest.raises(AppError) as exc_req:
        validate_idempotency_key(None)
    assert exc_req.value.code == ErrorCode.VAL_REQUIRED_FIELD

    with pytest.raises(AppError) as exc_fmt:
        validate_idempotency_key("short")
    assert exc_fmt.value.code == ErrorCode.VAL_INVALID_FORMAT

    assert validate_idempotency_key("  idem-key_2026:001  ") == "idem-key_2026:001"
    h1 = compute_request_hash({"b": 2, "a": 1})
    h2 = compute_request_hash({"a": 1, "b": 2})
    assert h1 == h2
