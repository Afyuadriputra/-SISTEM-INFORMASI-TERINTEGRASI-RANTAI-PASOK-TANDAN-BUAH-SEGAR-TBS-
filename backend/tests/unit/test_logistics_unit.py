"""Unit tests for Logistics SM-05, QR generation, and cancellation invariants (B6)."""

from __future__ import annotations

import hashlib

import pytest
from app.core.exceptions import AppError, ErrorCode
from app.modules.logistics.domain.entities import DeliveryOrderStatus
from app.modules.logistics.domain.rules import (
    assert_can_cancel_edo,
    assert_can_issue_edo,
    assert_can_transition_edo,
    generate_edo_qr_token_and_hash,
)


def test_generate_edo_qr_token_is_unique_and_matches_sha256() -> None:
    t1, h1 = generate_edo_qr_token_and_hash(delivery_order_number="EDO-2026-1110-0001")
    t2, h2 = generate_edo_qr_token_and_hash(delivery_order_number="EDO-2026-1110-0001")
    assert t1 != t2
    assert h1 != h2
    assert hashlib.sha256(t1.encode("utf-8")).hexdigest() == h1


def test_sm05_issue_and_transition_guards() -> None:
    assert_can_issue_edo(
        current_status=DeliveryOrderStatus.DRAFT, expected_version=1, actual_version=1
    )
    with pytest.raises(AppError) as exc_stale:
        assert_can_issue_edo(
            current_status=DeliveryOrderStatus.DRAFT, expected_version=1, actual_version=2
        )
    assert exc_stale.value.code == ErrorCode.LOG_STALE_RECORD_VERSION

    assert_can_transition_edo(
        current_status=DeliveryOrderStatus.READY,
        target_status=DeliveryOrderStatus.IN_TRANSIT,
        expected_version=2,
        actual_version=2,
        has_global_ops=False,
    )
    with pytest.raises(AppError) as exc_scope:
        assert_can_transition_edo(
            current_status=DeliveryOrderStatus.RECEIVED,
            target_status=DeliveryOrderStatus.COMPLETED,
            expected_version=5,
            actual_version=5,
            has_global_ops=False,
        )
    assert exc_scope.value.code == ErrorCode.AUTH_SCOPE_FORBIDDEN

    with pytest.raises(AppError) as exc_jump:
        assert_can_transition_edo(
            current_status=DeliveryOrderStatus.DRAFT,
            target_status=DeliveryOrderStatus.COMPLETED,
            expected_version=1,
            actual_version=1,
            has_global_ops=True,
        )
    assert exc_jump.value.code == ErrorCode.LOG_INVALID_STATE_TRANSITION


def test_sm05_cancellation_guards() -> None:
    for forbidden_state in (
        DeliveryOrderStatus.ARRIVED,
        DeliveryOrderStatus.RECEIVED,
        DeliveryOrderStatus.COMPLETED,
        DeliveryOrderStatus.CANCELLED,
    ):
        with pytest.raises(AppError) as exc:
            assert_can_cancel_edo(
                current_status=forbidden_state,
                expected_version=3,
                actual_version=3,
                has_global_ops=True,
            )
        assert exc.value.code == ErrorCode.LOG_CANCELLATION_FORBIDDEN

    with pytest.raises(AppError) as exc_coop_transit:
        assert_can_cancel_edo(
            current_status=DeliveryOrderStatus.IN_TRANSIT,
            expected_version=3,
            actual_version=3,
            has_global_ops=False,
        )
    assert exc_coop_transit.value.code == ErrorCode.AUTH_SCOPE_FORBIDDEN
