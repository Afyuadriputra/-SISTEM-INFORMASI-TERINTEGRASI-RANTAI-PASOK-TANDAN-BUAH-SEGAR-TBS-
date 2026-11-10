"""Unit tests for B3 Pricing SM-01, SOD-01, periods, Decimals, and HTML sanitization."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from app.core.exceptions import AppError, ErrorCode
from app.modules.identity_access.domain.entities import (
    AccessScopeEntity,
    AccountStatus,
    AuthenticatedPrincipal,
    RoleCode,
    ScopeType,
)
from app.modules.identity_access.domain.rules import ROLE_PERMISSIONS_MAP
from app.modules.pricing.domain.entities import PriceQuoteStatus
from app.modules.pricing.domain.rules import (
    assert_can_publish,
    assert_can_verify,
    parse_positive_price_per_kg,
    periods_overlap,
    validate_price_period,
)
from app.modules.public_portal.domain.entities import sanitize_public_text


def _actor(role: RoleCode) -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(
        session_id=uuid4(),
        user_id=uuid4(),
        username=role.value.lower(),
        email=None,
        display_name=role.value,
        linked_party_id=None,
        status=AccountStatus.ACTIVE,
        roles=(role,),
        access_scopes=(
            AccessScopeEntity(
                id=uuid4(),
                scope_type=ScopeType.PERUMDA_GLOBAL,
                farmer_id=None,
                cooperative_id=None,
                mill_id=None,
            ),
        ),
        permissions=ROLE_PERMISSIONS_MAP[role],
        last_login_at=None,
        non_approver_admin=(role == RoleCode.SYSTEM_ADMIN),
    )


def test_price_decimal_and_period_validation() -> None:
    assert parse_positive_price_per_kg("2920.00") == Decimal("2920.00")
    for non_pos in ("0.00", "-2500.00"):
        with pytest.raises(AppError) as exc:
            parse_positive_price_per_kg(non_pos)
        assert exc.value.code == ErrorCode.PRICE_INVALID_AMOUNT
        assert exc.value.status_code == 422

    for bad_fmt in ("2920", "Rp2920.00", "2920.5"):
        with pytest.raises(AppError) as exc2:
            parse_positive_price_per_kg(bad_fmt)
        assert exc2.value.code == ErrorCode.VAL_INVALID_DECIMAL_PRECISION

    t0 = datetime(2026, 11, 10, 1, 0, tzinfo=UTC)
    validate_price_period(t0, t0 + timedelta(hours=8))
    with pytest.raises(AppError) as exc3:
        validate_price_period(t0, t0)
    assert exc3.value.code == ErrorCode.PRICE_INVALID_PERIOD


def test_sm01_maker_checker_br_sys_002_and_interval_overlap() -> None:
    maker = _actor(RoleCode.PERUMDA_OPERATIONS)
    admin = _actor(RoleCode.SYSTEM_ADMIN)
    checker = _actor(RoleCode.DIRECTOR)

    with pytest.raises(AppError) as exc_sod:
        assert_can_verify(
            PriceQuoteStatus.PENDING_VERIFICATION, submitted_by=maker.user_id, actor=maker
        )
    assert exc_sod.value.code == ErrorCode.AUTH_CONFLICT_OF_DUTIES

    with pytest.raises(AppError) as exc_adm:
        assert_can_verify(
            PriceQuoteStatus.PENDING_VERIFICATION, submitted_by=maker.user_id, actor=admin
        )
    assert exc_adm.value.code == ErrorCode.AUTH_OPERATION_FORBIDDEN

    assert_can_verify(
        PriceQuoteStatus.PENDING_VERIFICATION, submitted_by=maker.user_id, actor=checker
    )

    with pytest.raises(AppError) as exc_unver:
        assert_can_publish(PriceQuoteStatus.PENDING_VERIFICATION)
    assert exc_unver.value.code == ErrorCode.PRICE_NOT_VERIFIED

    t0 = datetime(2026, 11, 10, 0, 0, tzinfo=UTC)
    t1 = t0 + timedelta(hours=8)
    t2 = t1 + timedelta(hours=8)
    assert periods_overlap(t0, t1, t1, t2) is False
    assert periods_overlap(t0, t1, t0 + timedelta(hours=4), None) is True


def test_sanitize_public_text_removes_scripts_and_tags() -> None:
    dirty = "<b>Pengumuman</b><script>alert('xss')</script> Harga resmi &amp; update."
    assert sanitize_public_text(dirty) == "Pengumuman Harga resmi & update."
