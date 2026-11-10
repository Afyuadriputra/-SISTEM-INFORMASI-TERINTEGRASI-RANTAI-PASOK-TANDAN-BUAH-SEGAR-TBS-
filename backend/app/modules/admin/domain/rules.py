"""Pure governance rules enforcing BR-SYS-002 & immutable versioned rule creation."""

from __future__ import annotations

from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from app.core.exceptions import AppError, ErrorCode
from app.modules.admin.domain.entities import RuleDtoApprovalStatus
from app.modules.contracts.domain.entities import PolicyClassification
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.domain.rules import is_non_approver_admin


def validate_rule_version_input(
    *,
    principal: AuthenticatedPrincipal,
    rule_code: str,
    effective_from: datetime,
    effective_until: datetime | None,
    rule_config: dict[str, Any],
    policy_classification: PolicyClassification,
) -> tuple[str, str, dict[str, Any]]:
    """Enforce BR-SYS-002 (only Director activates CONFIRMED) & validate bounds."""
    cleaned_code = rule_code.strip()
    if not cleaned_code:
        raise AppError(
            ErrorCode.VAL_REQUIRED_FIELD,
            details=[{"field": "rule_code", "reason": "Kode aturan wajib diisi."}],
        )
    if effective_until is not None and effective_until <= effective_from:
        raise AppError(
            ErrorCode.VAL_INVALID_DATE_RANGE,
            details=[
                {
                    "field": "effective_until",
                    "reason": "Tanggal berakhir aturan harus setelah tanggal mulai.",
                    "code": ErrorCode.VAL_INVALID_DATE_RANGE.value,
                }
            ],
        )

    is_director = RoleCode.DIRECTOR in principal.roles and not is_non_approver_admin(
        principal.roles
    )
    if policy_classification == PolicyClassification.CONFIRMED and not is_director:
        raise AppError(ErrorCode.AUTH_OPERATION_FORBIDDEN)

    if policy_classification == PolicyClassification.CONFIRMED:
        db_status = "APPROVED"
    elif policy_classification in (
        PolicyClassification.SIMULATION_ONLY,
        PolicyClassification.PENDING_SOP,
    ):
        db_status = policy_classification.value
    else:
        db_status = "DRAFT"

    stored_config = dict(rule_config)
    stored_config.setdefault("policy_classification", policy_classification.value)
    return cleaned_code, db_status, stored_config


def map_db_rule_status(
    *, db_approval_status: str, rule_config: dict[str, Any]
) -> tuple[RuleDtoApprovalStatus, PolicyClassification]:
    """Translate persisted rule_status into OpenAPI approval_status + policy_classification."""
    if db_approval_status == "APPROVED":
        dto_status = RuleDtoApprovalStatus.APPROVED
    elif db_approval_status in ("SUPERSEDED", "RETIRED"):
        dto_status = RuleDtoApprovalStatus.RETIRED
    else:
        dto_status = RuleDtoApprovalStatus.DRAFT

    raw_cls = str(rule_config.get("policy_classification") or "").strip()
    if raw_cls in {p.value for p in PolicyClassification}:
        policy_cls = PolicyClassification(raw_cls)
    elif db_approval_status == "APPROVED":
        policy_cls = PolicyClassification.CONFIRMED
    elif db_approval_status == "PENDING_SOP":
        policy_cls = PolicyClassification.PENDING_SOP
    else:
        policy_cls = PolicyClassification.SIMULATION_ONLY

    return dto_status, policy_cls


def validate_audit_date_range(date_from: date | None, date_to: date | None) -> None:
    if date_from is not None and date_to is not None and date_from > date_to:
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


def compute_cache_hit_ratio_percent(*, hits: int, misses: int) -> Decimal:
    total = hits + misses
    if total <= 0:
        return Decimal("0.0000")
    ratio = (Decimal(hits) * Decimal("100")) / Decimal(total)
    return ratio.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
