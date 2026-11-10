"""Use cases orchestrating Reconciliation SM-07, Disputes SM-08, SOD-03 & Allocations."""

from __future__ import annotations

from uuid import UUID

from app.core.exceptions import AppError, ErrorCode
from app.core.idempotency_primitives import (
    IdempotencySlotPort,
    compute_request_hash,
    validate_idempotency_key,
)
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.domain.rules import (
    allowed_cooperative_ids,
    has_global_scope,
    is_non_approver_admin,
)
from app.modules.reconciliation.application.ports import ReconciliationRepositoryPort
from app.modules.reconciliation.domain.entities import (
    AllocationMode,
    DisputeDecision,
    FarmerSettlementAllocationEntity,
    ReconciliationCaseEntity,
    ReconciliationStatus,
    WeightBasis,
)
from app.modules.reconciliation.domain.rules import (
    assert_equivalent_weight_basis,
    validate_dispute_reason,
)

TOLERANCE_SIMULATION_NOTICE = (
    "Ambang batas toleransi 1,5000% & pembagian hasil petani berstatus SIMULATION_ONLY / "
    "PENDING_SOP (BSD-DEC-007, BSD-DEC-013)."
)


def _resolve_coop_read_scope(principal: AuthenticatedPrincipal) -> set[UUID] | None:
    if has_global_scope(principal):
        return None
    if RoleCode.COOPERATIVE_OPERATOR in principal.roles:
        return allowed_cooperative_ids(principal)
    raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)


class ReconciliationService:
    """Orchestrates weighing reconciliation, dispute SOD-03 review/resolution, & allocations."""

    def __init__(
        self,
        *,
        repo: ReconciliationRepositoryPort,
        idempotency: IdempotencySlotPort,
    ) -> None:
        self._repo = repo
        self._idempotency = idempotency

    async def list_cases(
        self,
        *,
        principal: AuthenticatedPrincipal,
        status_filter: ReconciliationStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ReconciliationCaseEntity], int]:
        coop_ids = _resolve_coop_read_scope(principal)
        return await self._repo.list_cases(
            allowed_cooperative_ids=coop_ids,
            status_filter=status_filter,
            page=page,
            page_size=page_size,
        )

    async def get_case_detail(
        self,
        *,
        principal: AuthenticatedPrincipal,
        reconciliation_id: UUID,
    ) -> ReconciliationCaseEntity:
        case = await self._repo.get_case_by_id(reconciliation_id)
        if case is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        coop_ids = _resolve_coop_read_scope(principal)
        if coop_ids is not None:
            case_coop = await self._repo.get_case_coop_id(reconciliation_id)
            if case_coop is None or case_coop not in coop_ids:
                raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)
        return case

    async def create_or_trigger(
        self,
        *,
        principal: AuthenticatedPrincipal,
        raw_idempotency_key: str | None,
        delivery_order_id: UUID,
        weight_basis: WeightBasis,
    ) -> tuple[ReconciliationCaseEntity, bool]:
        idempotency_key = validate_idempotency_key(raw_idempotency_key)
        assert_equivalent_weight_basis(weight_basis)
        req_hash = compute_request_hash(
            {
                "delivery_order_id": str(delivery_order_id),
                "weight_basis": weight_basis.value,
            }
        )
        slot = await self._idempotency.reserve(
            actor_id=principal.user_id,
            operation_key="createOrTriggerReconciliation",
            idempotency_key=idempotency_key,
            request_hash=req_hash,
        )
        if slot.is_replay:
            if slot.response_reference is None:
                raise AppError(ErrorCode.SYS_DEPENDENCY_UNAVAILABLE)
            existing = await self._repo.get_case_by_id(slot.response_reference)
            if existing is None:
                raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
            return existing, True

        try:
            case = await self._repo.create_or_trigger(
                delivery_order_id=delivery_order_id,
                weight_basis=weight_basis,
                actor_id=principal.user_id,
                idempotency_record_id=slot.record_id,
            )
        except Exception:
            await self._idempotency.release_on_error(record_id=slot.record_id)
            raise
        return case, False

    async def calculate(
        self,
        *,
        principal: AuthenticatedPrincipal,
        raw_idempotency_key: str | None,
        reconciliation_id: UUID,
    ) -> tuple[ReconciliationCaseEntity, bool]:
        idempotency_key = validate_idempotency_key(raw_idempotency_key)
        req_hash = compute_request_hash({"reconciliation_id": str(reconciliation_id)})
        slot = await self._idempotency.reserve(
            actor_id=principal.user_id,
            operation_key="calculateReconciliation",
            idempotency_key=idempotency_key,
            request_hash=req_hash,
        )
        if slot.is_replay:
            if slot.response_reference is None:
                raise AppError(ErrorCode.SYS_DEPENDENCY_UNAVAILABLE)
            existing = await self._repo.get_case_by_id(slot.response_reference)
            if existing is None:
                raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
            return existing, True

        try:
            case = await self._repo.calculate(
                reconciliation_id=reconciliation_id,
                actor_id=principal.user_id,
                idempotency_record_id=slot.record_id,
            )
        except Exception:
            await self._idempotency.release_on_error(record_id=slot.record_id)
            raise
        return case, False

    async def submit_review(
        self,
        *,
        principal: AuthenticatedPrincipal,
        reconciliation_id: UUID,
        decision: DisputeDecision,
        reason: str | None,
        evidence_file_id: UUID | None,
        proposed_settlement_weight_raw: str | None,
    ) -> ReconciliationCaseEntity:
        clean_reason = validate_dispute_reason(reason)
        return await self._repo.submit_review(
            reconciliation_id=reconciliation_id,
            decision=decision,
            reason=clean_reason,
            evidence_file_id=evidence_file_id,
            proposed_settlement_weight_raw=proposed_settlement_weight_raw,
            actor_id=principal.user_id,
        )

    async def resolve_dispute(
        self,
        *,
        principal: AuthenticatedPrincipal,
        reconciliation_id: UUID,
        decision: DisputeDecision,
        final_outcome: ReconciliationStatus,
        agreed_settlement_weight_raw: str | None,
        reason: str | None,
        evidence_file_id: UUID | None,
    ) -> ReconciliationCaseEntity:
        if final_outcome not in (ReconciliationStatus.RESOLVED, ReconciliationStatus.CANCELLED):
            raise AppError(ErrorCode.REC_INVALID_STATE_TRANSITION)
        clean_reason = validate_dispute_reason(reason)
        return await self._repo.resolve_dispute(
            reconciliation_id=reconciliation_id,
            decision=decision,
            final_outcome=final_outcome,
            agreed_settlement_weight_raw=agreed_settlement_weight_raw,
            reason=clean_reason,
            evidence_file_id=evidence_file_id,
            actor_id=principal.user_id,
            non_approver_admin=is_non_approver_admin(principal.roles),
        )

    async def compute_allocations(
        self,
        *,
        principal: AuthenticatedPrincipal,
        reconciliation_id: UUID,
        mode: AllocationMode,
        allocation_policy_version_id: UUID,
    ) -> list[FarmerSettlementAllocationEntity]:
        _ = principal
        return await self._repo.compute_allocations(
            reconciliation_id=reconciliation_id,
            mode=mode,
            allocation_policy_version_id=allocation_policy_version_id,
            actor_id=principal.user_id,
        )
