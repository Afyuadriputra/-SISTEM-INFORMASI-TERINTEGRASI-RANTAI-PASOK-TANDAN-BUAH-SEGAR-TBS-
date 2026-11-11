"""Strict OpenAPI 3.1.0 request/response DTOs for /api/v1/reconciliations* endpoints."""

from __future__ import annotations

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
from app.modules.contracts.domain.entities import PolicyClassification
from app.modules.reconciliation.domain.entities import (
    AllocationMode,
    AllocationRecordStatus,
    DisputeDecision,
    DisputeReviewEntity,
    FarmerSettlementAllocationEntity,
    ReconciliationCaseEntity,
    ReconciliationStatus,
    WeightBasis,
)


class DisputeReviewDto(StrictContractModel):
    id: str
    reviewer_id: str
    previous_status: ReconciliationStatus
    decision: DisputeDecision
    reason: str
    evidence_file_id: str | None
    approved_by: str | None
    reviewed_at: str


class FarmerSettlementAllocationDto(StrictContractModel):
    id: str
    receipt_id: str
    farmer_id: str
    farmer_name: str
    allocation_basis_weight_kg: str
    agreed_weight_kg: str | None
    allocation_policy_version_id: str
    gross_amount: str
    deduction_amount: str
    net_amount: str
    status: AllocationRecordStatus
    policy_classification: PolicyClassification


class ReconciliationCaseDto(StrictContractModel):
    id: str
    delivery_order_id: str
    delivery_order_number: str
    mill_ticket_id: str | None
    revision_number: int = Field(ge=1)
    origin_weight_kg: str
    mill_weight_kg: str
    difference_weight_kg: str
    difference_percent: str
    tolerance_percent: str
    rule_version_id: str
    tolerance_policy_classification: PolicyClassification
    is_negative_difference: bool
    status: ReconciliationStatus
    is_current: bool
    calculated_at: str | None
    resolved_at: str | None
    dispute_reviews: list[DisputeReviewDto]
    farmer_allocations: list[FarmerSettlementAllocationDto]


class TriggerReconciliationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    delivery_order_id: UUID
    weight_basis: WeightBasis = WeightBasis.NET_WEIGHT_BEFORE_GRADING


class DisputeReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: DisputeDecision
    reason: str = Field(min_length=5, max_length=1000)
    evidence_file_id: UUID | None = None
    proposed_settlement_weight_kg: str | None = Field(default=None, max_length=32)


class ResolveDisputeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: DisputeDecision
    final_outcome: Literal[ReconciliationStatus.RESOLVED, ReconciliationStatus.CANCELLED]
    agreed_settlement_weight_kg: str | None = Field(default=None, max_length=32)
    reason: str = Field(min_length=5, max_length=1000)
    evidence_file_id: UUID | None = None


class ComputeAllocationsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: AllocationMode
    allocation_policy_version_id: UUID


class ReconciliationListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[ReconciliationCaseDto]
    meta: PaginationMeta
    request_id: str


class ReconciliationEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: ReconciliationCaseDto
    meta: SimpleSuccessMeta
    request_id: str


class AllocationListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[FarmerSettlementAllocationDto]
    meta: SimpleSuccessMeta
    request_id: str


def _review_to_dto(r: DisputeReviewEntity) -> DisputeReviewDto:
    return DisputeReviewDto(
        id=str(r.id),
        reviewer_id=str(r.reviewer_id),
        previous_status=r.previous_status,
        decision=r.decision,
        reason=r.reason,
        evidence_file_id=str(r.evidence_file_id) if r.evidence_file_id is not None else None,
        approved_by=str(r.approved_by) if r.approved_by is not None else None,
        reviewed_at=format_utc_iso(r.reviewed_at) or "",
    )


def allocation_to_dto(a: FarmerSettlementAllocationEntity) -> FarmerSettlementAllocationDto:
    return FarmerSettlementAllocationDto(
        id=str(a.id),
        receipt_id=str(a.receipt_id),
        farmer_id=str(a.farmer_id),
        farmer_name=a.farmer_name,
        allocation_basis_weight_kg=format_decimal(a.allocation_basis_weight_kg, 3) or "0.000",
        agreed_weight_kg=format_decimal(a.agreed_weight_kg, 3),
        allocation_policy_version_id=str(a.allocation_policy_version_id),
        gross_amount=format_decimal(a.gross_amount, 2) or "0.00",
        deduction_amount=format_decimal(a.deduction_amount, 2) or "0.00",
        net_amount=format_decimal(a.net_amount, 2) or "0.00",
        status=a.status,
        policy_classification=a.policy_classification,
    )


def reconciliation_to_dto(entity: ReconciliationCaseEntity) -> ReconciliationCaseDto:
    return ReconciliationCaseDto(
        id=str(entity.id),
        delivery_order_id=str(entity.delivery_order_id),
        delivery_order_number=entity.delivery_order_number,
        mill_ticket_id=str(entity.mill_ticket_id) if entity.mill_ticket_id is not None else None,
        revision_number=entity.revision_number,
        origin_weight_kg=format_decimal(entity.origin_weight_kg, 3) or "0.000",
        mill_weight_kg=format_decimal(entity.mill_weight_kg, 3) or "0.000",
        difference_weight_kg=format_decimal(entity.difference_weight_kg, 3) or "0.000",
        difference_percent=format_decimal(entity.difference_percent, 4) or "0.0000",
        tolerance_percent=format_decimal(entity.tolerance_percent, 4) or "0.0000",
        rule_version_id=str(entity.rule_version_id),
        tolerance_policy_classification=entity.tolerance_policy_classification,
        is_negative_difference=entity.is_negative_difference,
        status=entity.status,
        is_current=entity.is_current,
        calculated_at=format_utc_iso(entity.calculated_at),
        resolved_at=format_utc_iso(entity.resolved_at),
        dispute_reviews=[_review_to_dto(r) for r in entity.dispute_reviews],
        farmer_allocations=[allocation_to_dto(a) for a in entity.farmer_allocations],
    )
