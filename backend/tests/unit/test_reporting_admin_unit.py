"""Pure unit tests for Reporting, System Rules, Audit Redaction & Observability (B10)."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from app.core.exceptions import AppError, ErrorCode
from app.core.observability import ObservabilityTracker
from app.modules.admin.domain.entities import RuleDtoApprovalStatus
from app.modules.admin.domain.rules import (
    compute_cache_hit_ratio_percent,
    map_db_rule_status,
    validate_rule_version_input,
)
from app.modules.contracts.domain.entities import PolicyClassification
from app.modules.identity_access.domain.entities import (
    AccessScopeEntity,
    AccountStatus,
    AuthenticatedPrincipal,
    RoleCode,
    ScopeType,
)
from app.modules.reporting.domain.rules import (
    build_report_scope_key,
    compute_gross_contribution_simulation,
    resolve_report_date_window,
)


def _principal(role: RoleCode) -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(
        session_id=uuid4(),
        user_id=uuid4(),
        username=role.value.lower(),
        email=f"{role.value.lower()}@agroniaga.local",
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
        permissions=frozenset(),
        last_login_at=None,
        non_approver_admin=(role == RoleCode.SYSTEM_ADMIN),
    )


def test_report_date_window_margin_simulation_and_scope_key() -> None:
    d1, d2 = resolve_report_date_window(date(2026, 11, 1), date(2026, 11, 10))
    assert (d1, d2) == (date(2026, 11, 1), date(2026, 11, 10))

    with pytest.raises(AppError) as bad_range:
        resolve_report_date_window(date(2026, 11, 12), date(2026, 11, 10))
    assert bad_range.value.code == ErrorCode.VAL_INVALID_DATE_RANGE

    assert (
        compute_gross_contribution_simulation(
            ar_billed_total=Decimal("28215000.00"),
            ap_approved_unpaid_total=Decimal("0.00"),
            ap_verified_paid_total=Decimal("0.00"),
        )
        is None
    )
    assert compute_gross_contribution_simulation(
        ar_billed_total=Decimal("28215000.00"),
        ap_approved_unpaid_total=Decimal("6730000.00"),
        ap_verified_paid_total=Decimal("20000000.00"),
    ) == Decimal("1485000.00")

    f1, f2 = uuid4(), uuid4()
    k1 = build_report_scope_key(
        role_code=RoleCode.FARMER, farmer_ids={f1}, coop_ids=None, mill_ids=None
    )
    k2 = build_report_scope_key(
        role_code=RoleCode.FARMER, farmer_ids={f2}, coop_ids=None, mill_ids=None
    )
    assert k1 != k2


def test_system_rule_version_br_sys_002_and_status_mapping() -> None:
    now = datetime.now(UTC)
    sys_admin = _principal(RoleCode.SYSTEM_ADMIN)
    director = _principal(RoleCode.DIRECTOR)

    with pytest.raises(AppError) as admin_confirmed:
        validate_rule_version_input(
            principal=sys_admin,
            rule_code="RECONCILIATION_TOLERANCE",
            effective_from=now,
            effective_until=None,
            rule_config={"tolerance_percent": "2.0000"},
            policy_classification=PolicyClassification.CONFIRMED,
        )
    assert admin_confirmed.value.code == ErrorCode.AUTH_OPERATION_FORBIDDEN

    code, db_status, cfg = validate_rule_version_input(
        principal=sys_admin,
        rule_code="RECONCILIATION_TOLERANCE",
        effective_from=now,
        effective_until=now + timedelta(days=30),
        rule_config={"tolerance_percent": "2.0000"},
        policy_classification=PolicyClassification.SIMULATION_ONLY,
    )
    assert code == "RECONCILIATION_TOLERANCE"
    assert db_status == "SIMULATION_ONLY"
    assert cfg["policy_classification"] == "SIMULATION_ONLY"

    _, dir_status, _ = validate_rule_version_input(
        principal=director,
        rule_code="BUSINESS_MODEL_POLICY",
        effective_from=now,
        effective_until=None,
        rule_config={"business_model_code": "PRINCIPAL"},
        policy_classification=PolicyClassification.CONFIRMED,
    )
    assert dir_status == "APPROVED"

    assert map_db_rule_status(
        db_approval_status="SIMULATION_ONLY",
        rule_config={"policy_classification": "SIMULATION_ONLY"},
    ) == (RuleDtoApprovalStatus.DRAFT, PolicyClassification.SIMULATION_ONLY)
    assert map_db_rule_status(
        db_approval_status="APPROVED",
        rule_config={"policy_classification": "CONFIRMED"},
    ) == (RuleDtoApprovalStatus.APPROVED, PolicyClassification.CONFIRMED)


def test_observability_cache_ratio_and_error_correlation_window() -> None:
    assert compute_cache_hit_ratio_percent(hits=0, misses=0) == Decimal("0.0000")
    assert compute_cache_hit_ratio_percent(hits=3, misses=1) == Decimal("75.0000")

    tracker = ObservabilityTracker()
    now = datetime.now(UTC)
    tracker.record_completion(
        request_id="req_old",
        trace_id="trace_old",
        route="/api/v1/reports/overview",
        status_code=500,
        error_code="SYS_INTERNAL_ERROR",
        occurred_at=now - timedelta(hours=25),
    )
    tracker.record_completion(
        request_id="req_ok",
        trace_id="trace_ok",
        route="/api/v1/reports/overview",
        status_code=200,
        error_code=None,
        occurred_at=now,
    )
    tracker.record_completion(
        request_id="req_fail_503",
        trace_id="trace_503",
        route="/api/v1/admin/system-health",
        status_code=503,
        error_code="SYS_DEPENDENCY_UNAVAILABLE",
        occurred_at=now,
    )
    total_24h, err_5xx, recent = tracker.snapshot_24h()
    assert total_24h == 2
    assert err_5xx == 1
    assert len(recent) == 1
    assert recent[0].request_id == "req_fail_503"
    assert recent[0].module == "admin.system-health"
