"""Strict OpenAPI 3.1.0 request/response DTOs for /api/v1/contracts* endpoints."""

from __future__ import annotations

from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.logging import format_utc_iso
from app.core.schemas import (
    PaginationMeta,
    SimpleSuccessMeta,
    StrictContractModel,
    format_decimal,
)
from app.modules.contracts.domain.entities import (
    BusinessModelCode,
    ContractStatus,
    PerumdaRoleCode,
    PolicyClassification,
    PriceRuleType,
    QuotaPeriodEntity,
    QuotaPeriodStatus,
    QuotaReservationEntity,
    QuotaReservationStatus,
    TradeContractEntity,
)


class QuotaPeriodSummaryDto(StrictContractModel):
    id: str
    period_start: str
    period_end: str
    quota_limit_kg: str
    consumed_weight_kg: str
    active_reserved_kg: str
    available_quota_kg: str
    status: QuotaPeriodStatus


class TradeContractDto(StrictContractModel):
    id: str
    contract_number: str
    mill_id: str
    mill_name: str
    start_date: str
    end_date: str
    price_rule_type: PriceRuleType
    agreed_price_per_kg: str | None
    business_model_code: BusinessModelCode
    perumda_role: PerumdaRoleCode
    seller_party_id: str
    buyer_party_id: str
    agent_party_id: str | None
    represented_party_id: str | None
    business_model_rule_version: str
    payment_terms: str
    status: ContractStatus
    policy_classification: PolicyClassification
    quota_periods: list[QuotaPeriodSummaryDto]
    approved_by: str | None
    approved_at: str | None
    created_at: str


class CreateContractRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_number: str = Field(min_length=2, max_length=80)
    mill_id: UUID
    start_date: date
    end_date: date
    price_rule_type: PriceRuleType
    agreed_price_per_kg: str | None = Field(default=None, max_length=32)
    business_model_code: BusinessModelCode
    perumda_role: PerumdaRoleCode
    seller_party_id: UUID
    buyer_party_id: UUID
    agent_party_id: UUID | None = None
    represented_party_id: UUID | None = None
    payment_terms: str = Field(min_length=3, max_length=500)
    initial_quota_kg: str = Field(min_length=1, max_length=32)


class ReserveQuotaRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quota_period_id: UUID
    delivery_order_id: UUID
    reserved_weight_kg: str = Field(min_length=1, max_length=32)


class QuotaReservationDto(StrictContractModel):
    id: str
    quota_period_id: str
    delivery_order_id: str
    reserved_weight_kg: str
    consumed_weight_kg: str
    status: QuotaReservationStatus
    reserved_at: str


class ContractListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[TradeContractDto]
    meta: PaginationMeta
    request_id: str


class ContractEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: TradeContractDto
    meta: SimpleSuccessMeta | None = None
    request_id: str


class QuotaPeriodListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[QuotaPeriodSummaryDto]
    meta: SimpleSuccessMeta | None = None
    request_id: str


class QuotaReservationEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: QuotaReservationDto
    meta: SimpleSuccessMeta | None = None
    request_id: str


def period_to_dto(entity: QuotaPeriodEntity) -> QuotaPeriodSummaryDto:
    return QuotaPeriodSummaryDto(
        id=str(entity.id),
        period_start=entity.period_start.isoformat(),
        period_end=entity.period_end.isoformat(),
        quota_limit_kg=format_decimal(entity.quota_limit_kg, 3) or "0.000",
        consumed_weight_kg=format_decimal(entity.consumed_weight_kg, 3) or "0.000",
        active_reserved_kg=format_decimal(entity.active_reserved_kg, 3) or "0.000",
        available_quota_kg=format_decimal(entity.available_quota_kg, 3) or "0.000",
        status=entity.status,
    )


def contract_to_dto(entity: TradeContractEntity) -> TradeContractDto:
    return TradeContractDto(
        id=str(entity.id),
        contract_number=entity.contract_number,
        mill_id=str(entity.mill_id),
        mill_name=entity.mill_name,
        start_date=entity.start_date.isoformat(),
        end_date=entity.end_date.isoformat(),
        price_rule_type=entity.price_rule_type,
        agreed_price_per_kg=format_decimal(entity.agreed_price_per_kg, 2),
        business_model_code=entity.business_model_code,
        perumda_role=entity.perumda_role,
        seller_party_id=str(entity.seller_party_id),
        buyer_party_id=str(entity.buyer_party_id),
        agent_party_id=str(entity.agent_party_id) if entity.agent_party_id is not None else None,
        represented_party_id=(
            str(entity.represented_party_id) if entity.represented_party_id is not None else None
        ),
        business_model_rule_version=str(entity.business_model_rule_version),
        payment_terms=entity.payment_terms,
        status=entity.status,
        policy_classification=entity.policy_classification,
        quota_periods=[period_to_dto(p) for p in entity.quota_periods],
        approved_by=str(entity.approved_by) if entity.approved_by is not None else None,
        approved_at=format_utc_iso(entity.approved_at),
        created_at=format_utc_iso(entity.created_at) or "",
    )


def reservation_to_dto(entity: QuotaReservationEntity) -> QuotaReservationDto:
    return QuotaReservationDto(
        id=str(entity.id),
        quota_period_id=str(entity.quota_period_id),
        delivery_order_id=str(entity.delivery_order_id),
        reserved_weight_kg=format_decimal(entity.reserved_weight_kg, 3) or "0.000",
        consumed_weight_kg=format_decimal(entity.consumed_weight_kg, 3) or "0.000",
        status=entity.status,
        reserved_at=format_utc_iso(entity.reserved_at) or "",
    )
