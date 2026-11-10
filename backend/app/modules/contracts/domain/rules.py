"""Pure domain validation and SM-03 / SM-04 / SOD-02 invariants for Contracts & Quota."""

from __future__ import annotations

import re
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from uuid import UUID

from app.core.exceptions import AppError, ErrorCode
from app.modules.contracts.domain.entities import (
    BusinessModelCode,
    ContractStatus,
    PerumdaRoleCode,
    PolicyClassification,
    PriceRuleType,
    QuotaPeriodStatus,
)

_KG_PATTERN = re.compile(r"^-?\d{1,11}\.\d{3}$")
_PRICE_PATTERN = re.compile(r"^-?\d{1,16}\.\d{2}$")


def parse_positive_kg(raw_value: str, *, field_name: str) -> Decimal:
    """Validate positive NUMERIC(14,3) kilogram value."""
    cleaned = raw_value.strip()
    if not _KG_PATTERN.match(cleaned):
        raise AppError(
            ErrorCode.VAL_INVALID_DECIMAL_PRECISION,
            details=[
                {
                    "field": field_name,
                    "reason": "Gunakan format desimal 3 angka di belakang koma (kg).",
                    "code": ErrorCode.VAL_INVALID_DECIMAL_PRECISION.value,
                }
            ],
        )
    try:
        val = Decimal(cleaned)
    except InvalidOperation as exc:
        raise AppError(ErrorCode.VAL_INVALID_DECIMAL_PRECISION) from exc
    if not val.is_finite() or val <= Decimal("0"):
        raise AppError(
            ErrorCode.VAL_INVALID_FORMAT,
            details=[
                {
                    "field": field_name,
                    "reason": "Nilai berat kuota harus lebih besar dari nol.",
                    "code": ErrorCode.VAL_INVALID_FORMAT.value,
                }
            ],
        )
    return val.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


def parse_agreed_price(*, price_rule_type: PriceRuleType, raw_price: str | None) -> Decimal | None:
    """Enforce mandatory positive agreed_price_per_kg on FIXED contracts."""
    if raw_price is None:
        if price_rule_type == PriceRuleType.FIXED:
            raise AppError(
                ErrorCode.VAL_REQUIRED_FIELD,
                details=[
                    {
                        "field": "agreed_price_per_kg",
                        "reason": "Kontrak FIXED wajib mengisi harga per kg disepakati.",
                        "code": ErrorCode.VAL_REQUIRED_FIELD.value,
                    }
                ],
            )
        return None
    cleaned = raw_price.strip()
    if not _PRICE_PATTERN.match(cleaned):
        raise AppError(
            ErrorCode.VAL_INVALID_DECIMAL_PRECISION,
            details=[
                {
                    "field": "agreed_price_per_kg",
                    "reason": "Gunakan format harga desimal 2 angka di belakang koma (IDR).",
                    "code": ErrorCode.VAL_INVALID_DECIMAL_PRECISION.value,
                }
            ],
        )
    try:
        val = Decimal(cleaned)
    except InvalidOperation as exc:
        raise AppError(ErrorCode.VAL_INVALID_DECIMAL_PRECISION) from exc
    if not val.is_finite() or val <= Decimal("0"):
        raise AppError(ErrorCode.PRICE_INVALID_AMOUNT)
    return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def validate_contract_party_structure(
    *,
    business_model_code: BusinessModelCode,
    perumda_role: PerumdaRoleCode,
    seller_party_id: UUID,
    buyer_party_id: UUID,
    agent_party_id: UUID | None,
    represented_party_id: UUID | None,
) -> None:
    """Enforce explicit PRINCIPAL / AGENT / UNCONFIRMED party invariants (DBD §10.1)."""
    if seller_party_id == buyer_party_id:
        raise AppError(
            ErrorCode.CONTRACT_BUSINESS_MODEL_UNCONFIRMED,
            details=[
                {
                    "field": "buyer_party_id",
                    "reason": "Pihak penjual dan pembeli kontrak tidak boleh entitas yang sama.",
                    "code": ErrorCode.CONTRACT_BUSINESS_MODEL_UNCONFIRMED.value,
                }
            ],
        )

    if business_model_code == BusinessModelCode.PRINCIPAL:
        if represented_party_id is not None:
            raise AppError(
                ErrorCode.CONTRACT_BUSINESS_MODEL_UNCONFIRMED,
                details=[
                    {
                        "field": "represented_party_id",
                        "reason": "Mode PRINCIPAL tidak menggunakan represented_party_id.",
                        "code": ErrorCode.CONTRACT_BUSINESS_MODEL_UNCONFIRMED.value,
                    }
                ],
            )
        if perumda_role not in (PerumdaRoleCode.BUYER, PerumdaRoleCode.SELLER):
            raise AppError(
                ErrorCode.CONTRACT_BUSINESS_MODEL_UNCONFIRMED,
                details=[
                    {
                        "field": "perumda_role",
                        "reason": "Mode PRINCIPAL wajib menetapkan perumda_role BUYER atau SELLER.",
                        "code": ErrorCode.CONTRACT_BUSINESS_MODEL_UNCONFIRMED.value,
                    }
                ],
            )
    elif business_model_code == BusinessModelCode.AGENT:
        if agent_party_id is None or represented_party_id is None:
            raise AppError(
                ErrorCode.CONTRACT_BUSINESS_MODEL_UNCONFIRMED,
                details=[
                    {
                        "field": "agent_party_id",
                        "reason": (
                            "Mode AGENT wajib mengisi agent_party_id dan represented_party_id."
                        ),
                        "code": ErrorCode.CONTRACT_BUSINESS_MODEL_UNCONFIRMED.value,
                    }
                ],
            )
        if perumda_role != PerumdaRoleCode.AGENT:
            raise AppError(
                ErrorCode.CONTRACT_BUSINESS_MODEL_UNCONFIRMED,
                details=[
                    {
                        "field": "perumda_role",
                        "reason": "Mode AGENT wajib menetapkan perumda_role = AGENT.",
                        "code": ErrorCode.CONTRACT_BUSINESS_MODEL_UNCONFIRMED.value,
                    }
                ],
            )
    elif business_model_code == BusinessModelCode.UNCONFIRMED:
        if perumda_role != PerumdaRoleCode.UNCONFIRMED:
            raise AppError(
                ErrorCode.CONTRACT_BUSINESS_MODEL_UNCONFIRMED,
                details=[
                    {
                        "field": "perumda_role",
                        "reason": (
                            "Rancangan UNCONFIRMED harus mempertahankan perumda_role UNCONFIRMED."
                        ),
                        "code": ErrorCode.CONTRACT_BUSINESS_MODEL_UNCONFIRMED.value,
                    }
                ],
            )


def derive_contract_policy_classification(
    *, business_model_code: BusinessModelCode, rule_approval_status: str
) -> PolicyClassification:
    """Keep UNCONFIRMED marked PENDING_SOP and non-approved policies marked SIMULATION_ONLY."""
    if business_model_code == BusinessModelCode.UNCONFIRMED:
        return PolicyClassification.PENDING_SOP
    if rule_approval_status == "APPROVED":
        return PolicyClassification.CONFIRMED
    if rule_approval_status == "PENDING_SOP":
        return PolicyClassification.SIMULATION_ONLY
    return PolicyClassification.SIMULATION_ONLY


def assert_can_approve_contract(
    *,
    status: ContractStatus,
    created_by: UUID,
    actor_id: UUID,
    non_approver_admin: bool,
) -> None:
    """Enforce SM-03, BR-SYS-002, and SOD-02 Maker != Checker on contract activation."""
    if non_approver_admin:
        raise AppError(ErrorCode.AUTH_OPERATION_FORBIDDEN)
    if created_by == actor_id:
        raise AppError(
            ErrorCode.AUTH_CONFLICT_OF_DUTIES,
            details={"sod_rule": "SOD-02", "created_by": str(created_by)},
        )
    if status != ContractStatus.PENDING_APPROVAL:
        raise AppError(
            ErrorCode.CONTRACT_NOT_ACTIVE,
            details={"contract_status": status.value},
        )


def assert_quota_reservable(
    *,
    contract_status: ContractStatus,
    contract_start: date,
    contract_end: date,
    period_status: QuotaPeriodStatus,
    period_start: date,
    period_end: date,
    available_quota_kg: Decimal,
    requested_weight_kg: Decimal,
    as_of_date: date,
) -> None:
    """Validate SM-03 ACTIVE/date bounds and PostgreSQL non-over-quota invariant."""
    if contract_status != ContractStatus.ACTIVE:
        raise AppError(
            ErrorCode.CONTRACT_NOT_ACTIVE,
            details={"contract_status": contract_status.value},
        )
    if as_of_date < contract_start or as_of_date > contract_end:
        raise AppError(
            ErrorCode.CONTRACT_EXPIRED,
            details={"contract_end_date": contract_end.isoformat()},
        )
    if (
        period_status != QuotaPeriodStatus.ACTIVE
        or as_of_date < period_start
        or as_of_date > period_end
    ):
        raise AppError(
            ErrorCode.CONTRACT_EXPIRED,
            details={"contract_end_date": period_end.isoformat()},
        )
    if requested_weight_kg > available_quota_kg:
        raise AppError(
            ErrorCode.CONTRACT_QUOTA_EXCEEDED,
            details={
                "available_quota_kg": f"{available_quota_kg:.3f}",
                "requested_weight_kg": f"{requested_weight_kg:.3f}",
            },
        )
