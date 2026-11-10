"""Domain entities and status enums for Contracts & Quota (DBD §10)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


class BusinessModelCode(StrEnum):
    PRINCIPAL = "PRINCIPAL"
    AGENT = "AGENT"
    UNCONFIRMED = "UNCONFIRMED"


class PerumdaRoleCode(StrEnum):
    BUYER = "BUYER"
    SELLER = "SELLER"
    AGENT = "AGENT"
    UNCONFIRMED = "UNCONFIRMED"


class PriceRuleType(StrEnum):
    FIXED = "FIXED"
    REFERENCE_FORMULA = "REFERENCE_FORMULA"
    PERIOD_SCHEDULE = "PERIOD_SCHEDULE"


class ContractStatus(StrEnum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class QuotaPeriodStatus(StrEnum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class QuotaReservationStatus(StrEnum):
    RESERVED = "RESERVED"
    CONSUMED = "CONSUMED"
    RELEASED = "RELEASED"


class PolicyClassification(StrEnum):
    CONFIRMED = "CONFIRMED"
    SIMULATION_ONLY = "SIMULATION_ONLY"
    PENDING_SOP = "PENDING_SOP"
    FUTURE = "FUTURE"


@dataclass(frozen=True, slots=True)
class QuotaPeriodEntity:
    id: UUID
    contract_id: UUID
    period_start: date
    period_end: date
    quota_limit_kg: Decimal
    consumed_weight_kg: Decimal
    active_reserved_kg: Decimal
    available_quota_kg: Decimal
    status: QuotaPeriodStatus


@dataclass(frozen=True, slots=True)
class QuotaReservationEntity:
    id: UUID
    quota_period_id: UUID
    delivery_order_id: UUID
    reserved_weight_kg: Decimal
    consumed_weight_kg: Decimal
    status: QuotaReservationStatus
    reserved_at: datetime


@dataclass(frozen=True, slots=True)
class TradeContractEntity:
    id: UUID
    contract_number: str
    mill_id: UUID
    mill_name: str
    start_date: date
    end_date: date
    price_rule_type: PriceRuleType
    agreed_price_per_kg: Decimal | None
    business_model_code: BusinessModelCode
    perumda_role: PerumdaRoleCode
    seller_party_id: UUID
    buyer_party_id: UUID
    agent_party_id: UUID | None
    represented_party_id: UUID | None
    business_model_rule_version: UUID
    payment_terms: str
    status: ContractStatus
    policy_classification: PolicyClassification
    quota_periods: tuple[QuotaPeriodEntity, ...]
    approved_by: UUID | None
    approved_at: datetime | None
    created_by: UUID
    version: int
    created_at: datetime
    updated_at: datetime
