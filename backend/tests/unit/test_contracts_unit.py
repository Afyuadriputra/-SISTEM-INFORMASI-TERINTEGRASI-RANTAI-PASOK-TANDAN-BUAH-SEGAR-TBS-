"""Unit tests for Trade Contracts, Model Classification, SM-03/04, and Quota invariants (B5)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from app.core.exceptions import AppError, ErrorCode
from app.modules.contracts.domain.entities import (
    BusinessModelCode,
    ContractStatus,
    PerumdaRoleCode,
    PolicyClassification,
    PriceRuleType,
    QuotaPeriodStatus,
)
from app.modules.contracts.domain.rules import (
    assert_can_approve_contract,
    assert_quota_reservable,
    derive_contract_policy_classification,
    parse_agreed_price,
    validate_contract_party_structure,
)


def test_validate_contract_party_structure_principal_vs_agent() -> None:
    p_perumda, p_mill, p_agent = uuid4(), uuid4(), uuid4()

    # Valid PRINCIPAL SELLER.
    validate_contract_party_structure(
        business_model_code=BusinessModelCode.PRINCIPAL,
        perumda_role=PerumdaRoleCode.SELLER,
        seller_party_id=p_perumda,
        buyer_party_id=p_mill,
        agent_party_id=None,
        represented_party_id=None,
    )

    # PRINCIPAL must reject represented_party_id.
    with pytest.raises(AppError) as exc_prin:
        validate_contract_party_structure(
            business_model_code=BusinessModelCode.PRINCIPAL,
            perumda_role=PerumdaRoleCode.SELLER,
            seller_party_id=p_perumda,
            buyer_party_id=p_mill,
            agent_party_id=None,
            represented_party_id=p_agent,
        )
    assert exc_prin.value.code == ErrorCode.CONTRACT_BUSINESS_MODEL_UNCONFIRMED

    # AGENT requires both agent_party_id and represented_party_id and role=AGENT.
    with pytest.raises(AppError) as exc_agent:
        validate_contract_party_structure(
            business_model_code=BusinessModelCode.AGENT,
            perumda_role=PerumdaRoleCode.AGENT,
            seller_party_id=p_agent,
            buyer_party_id=p_mill,
            agent_party_id=p_perumda,
            represented_party_id=None,
        )
    assert exc_agent.value.code == ErrorCode.CONTRACT_BUSINESS_MODEL_UNCONFIRMED

    validate_contract_party_structure(
        business_model_code=BusinessModelCode.AGENT,
        perumda_role=PerumdaRoleCode.AGENT,
        seller_party_id=p_agent,
        buyer_party_id=p_mill,
        agent_party_id=p_perumda,
        represented_party_id=p_agent,
    )


def test_contract_price_and_policy_classification() -> None:
    with pytest.raises(AppError) as exc_req:
        parse_agreed_price(price_rule_type=PriceRuleType.FIXED, raw_price=None)
    assert exc_req.value.code == ErrorCode.VAL_REQUIRED_FIELD

    assert parse_agreed_price(price_rule_type=PriceRuleType.FIXED, raw_price="2850.00") == Decimal(
        "2850.00"
    )

    assert (
        derive_contract_policy_classification(
            business_model_code=BusinessModelCode.UNCONFIRMED,
            rule_approval_status="PENDING_SOP",
        )
        == PolicyClassification.PENDING_SOP
    )
    assert (
        derive_contract_policy_classification(
            business_model_code=BusinessModelCode.PRINCIPAL,
            rule_approval_status="PENDING_SOP",
        )
        == PolicyClassification.SIMULATION_ONLY
    )


def test_contract_approval_sod_and_quota_bounds() -> None:
    maker, checker = uuid4(), uuid4()

    with pytest.raises(AppError) as exc_sysadmin:
        assert_can_approve_contract(
            status=ContractStatus.PENDING_APPROVAL,
            created_by=maker,
            actor_id=checker,
            non_approver_admin=True,
        )
    assert exc_sysadmin.value.code == ErrorCode.AUTH_OPERATION_FORBIDDEN

    with pytest.raises(AppError) as exc_sod:
        assert_can_approve_contract(
            status=ContractStatus.PENDING_APPROVAL,
            created_by=maker,
            actor_id=maker,
            non_approver_admin=False,
        )
    assert exc_sod.value.code == ErrorCode.AUTH_CONFLICT_OF_DUTIES

    with pytest.raises(AppError) as exc_exp:
        assert_quota_reservable(
            contract_status=ContractStatus.ACTIVE,
            contract_start=date(2026, 8, 1),
            contract_end=date(2026, 10, 31),
            period_status=QuotaPeriodStatus.ACTIVE,
            period_start=date(2026, 10, 1),
            period_end=date(2026, 10, 31),
            available_quota_kg=Decimal("50000.000"),
            requested_weight_kg=Decimal("10000.000"),
            as_of_date=date(2026, 11, 10),
        )
    assert exc_exp.value.code == ErrorCode.CONTRACT_EXPIRED

    with pytest.raises(AppError) as exc_exceeded:
        assert_quota_reservable(
            contract_status=ContractStatus.ACTIVE,
            contract_start=date(2026, 10, 1),
            contract_end=date(2026, 12, 31),
            period_status=QuotaPeriodStatus.ACTIVE,
            period_start=date(2026, 11, 1),
            period_end=date(2026, 11, 30),
            available_quota_kg=Decimal("25000.000"),
            requested_weight_kg=Decimal("30000.000"),
            as_of_date=date(2026, 11, 10),
        )
    assert exc_exceeded.value.code == ErrorCode.CONTRACT_QUOTA_EXCEEDED
