"""Domain entities and status enums for Reconciliation, Disputes, and Farmer Allocations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from app.modules.contracts.domain.entities import PolicyClassification


class ReconciliationStatus(StrEnum):
    WAITING_TICKET = "WAITING_TICKET"
    READY = "READY"
    MATCHED = "MATCHED"
    DISPUTE_HOLD = "DISPUTE_HOLD"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"


class DisputeDecision(StrEnum):
    KEEP_ORIGIN_WEIGHT = "KEEP_ORIGIN_WEIGHT"
    ACCEPT_MILL_WEIGHT = "ACCEPT_MILL_WEIGHT"
    AGREED_SETTLEMENT_WEIGHT = "AGREED_SETTLEMENT_WEIGHT"
    REQUIRE_TICKET_REVISION = "REQUIRE_TICKET_REVISION"
    HOLD_FOR_AUDIT = "HOLD_FOR_AUDIT"
    CANCEL_CASE = "CANCEL_CASE"


class WeightBasis(StrEnum):
    NET_WEIGHT_BEFORE_GRADING = "NET_WEIGHT_BEFORE_GRADING"
    NET_WEIGHT_AFTER_GRADING = "NET_WEIGHT_AFTER_GRADING"


class AllocationMode(StrEnum):
    SIMULATION = "SIMULATION"
    FINAL = "FINAL"


class AllocationRecordStatus(StrEnum):
    SIMULATED = "SIMULATED"
    PENDING_SOP_LOCKED = "PENDING_SOP_LOCKED"
    APPROVED = "APPROVED"
    SETTLED = "SETTLED"


@dataclass(frozen=True, slots=True)
class DisputeReviewEntity:
    id: UUID
    reviewer_id: UUID
    previous_status: ReconciliationStatus
    decision: DisputeDecision
    reason: str
    evidence_file_id: UUID | None
    approved_by: UUID | None
    reviewed_at: datetime


@dataclass(frozen=True, slots=True)
class FarmerSettlementAllocationEntity:
    id: UUID
    receipt_id: UUID
    farmer_id: UUID
    farmer_name: str
    allocation_basis_weight_kg: Decimal
    agreed_weight_kg: Decimal | None
    allocation_policy_version_id: UUID
    gross_amount: Decimal
    deduction_amount: Decimal
    net_amount: Decimal
    status: AllocationRecordStatus
    policy_classification: PolicyClassification


@dataclass(frozen=True, slots=True)
class ReconciliationCaseEntity:
    id: UUID
    delivery_order_id: UUID
    delivery_order_number: str
    mill_ticket_id: UUID | None
    revision_number: int
    origin_weight_kg: Decimal
    mill_weight_kg: Decimal
    difference_weight_kg: Decimal
    difference_percent: Decimal
    tolerance_percent: Decimal
    rule_version_id: UUID
    tolerance_policy_classification: PolicyClassification
    is_negative_difference: bool
    status: ReconciliationStatus
    is_current: bool
    agreed_settlement_weight_kg: Decimal | None
    calculated_at: datetime | None
    resolved_at: datetime | None
    dispute_reviews: tuple[DisputeReviewEntity, ...]
    farmer_allocations: tuple[FarmerSettlementAllocationEntity, ...]
