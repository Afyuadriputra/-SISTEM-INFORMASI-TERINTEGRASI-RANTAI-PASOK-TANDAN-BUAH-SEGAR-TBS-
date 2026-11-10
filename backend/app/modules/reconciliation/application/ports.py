"""Repository port contract for Reconciliation, Disputes SM-07/08, and Farmer Allocations."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.modules.reconciliation.domain.entities import (
    AllocationMode,
    DisputeDecision,
    FarmerSettlementAllocationEntity,
    ReconciliationCaseEntity,
    ReconciliationStatus,
    WeightBasis,
)


class ReconciliationRepositoryPort(Protocol):
    """Storage abstraction for reconciliation_cases, dispute_reviews, & farmer allocations."""

    async def list_cases(
        self,
        *,
        allowed_cooperative_ids: set[UUID] | None,
        status_filter: ReconciliationStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ReconciliationCaseEntity], int]: ...

    async def get_case_by_id(self, reconciliation_id: UUID) -> ReconciliationCaseEntity | None: ...

    async def get_case_coop_id(self, reconciliation_id: UUID) -> UUID | None: ...

    async def create_or_trigger(
        self,
        *,
        delivery_order_id: UUID,
        weight_basis: WeightBasis,
        actor_id: UUID,
        idempotency_record_id: UUID,
    ) -> ReconciliationCaseEntity: ...

    async def calculate(
        self,
        *,
        reconciliation_id: UUID,
        actor_id: UUID,
        idempotency_record_id: UUID,
    ) -> ReconciliationCaseEntity: ...

    async def submit_review(
        self,
        *,
        reconciliation_id: UUID,
        decision: DisputeDecision,
        reason: str,
        evidence_file_id: UUID | None,
        proposed_settlement_weight_raw: str | None,
        actor_id: UUID,
    ) -> ReconciliationCaseEntity: ...

    async def resolve_dispute(
        self,
        *,
        reconciliation_id: UUID,
        decision: DisputeDecision,
        final_outcome: ReconciliationStatus,
        agreed_settlement_weight_raw: str | None,
        reason: str,
        evidence_file_id: UUID | None,
        actor_id: UUID,
        non_approver_admin: bool,
    ) -> ReconciliationCaseEntity: ...

    async def compute_allocations(
        self,
        *,
        reconciliation_id: UUID,
        mode: AllocationMode,
        allocation_policy_version_id: UUID,
        actor_id: UUID,
    ) -> list[FarmerSettlementAllocationEntity]: ...
