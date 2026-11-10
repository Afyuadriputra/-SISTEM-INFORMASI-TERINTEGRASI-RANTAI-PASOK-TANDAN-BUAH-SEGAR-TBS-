"""FastAPI endpoints for Reconciliation, Disputes, & Farmer Allocations."""

from __future__ import annotations

from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, status

from app.core.logging import request_id_ctx
from app.core.schemas import SimpleSuccessMeta, build_pagination_meta
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.presentation.dependencies import require_access
from app.modules.reconciliation.application.use_cases import (
    TOLERANCE_SIMULATION_NOTICE,
    ReconciliationService,
)
from app.modules.reconciliation.domain.entities import ReconciliationStatus
from app.modules.reconciliation.presentation.schemas import (
    AllocationListEnvelope,
    ComputeAllocationsRequest,
    DisputeReviewRequest,
    ReconciliationEnvelope,
    ReconciliationListEnvelope,
    ResolveDisputeRequest,
    TriggerReconciliationRequest,
    allocation_to_dto,
    reconciliation_to_dto,
)

reconciliation_router = APIRouter(
    prefix="/api/v1/reconciliations", tags=["Reconciliation & Dispute"]
)


def get_reconciliation_service(request: Request) -> ReconciliationService:
    """Resolve ReconciliationService wired in composition root."""
    return cast(ReconciliationService, request.app.state.reconciliation_service)


@reconciliation_router.get("", response_model=ReconciliationListEnvelope)
async def list_reconciliations(
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("reconciliations.read",),
            )
        ),
    ],
    service: Annotated[ReconciliationService, Depends(get_reconciliation_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    rec_status: Annotated[ReconciliationStatus | None, Query(alias="status")] = None,
) -> ReconciliationListEnvelope:
    rows, total = await service.list_cases(
        principal=principal,
        status_filter=rec_status,
        page=page,
        page_size=page_size,
    )
    return ReconciliationListEnvelope(
        data=[reconciliation_to_dto(c) for c in rows],
        meta=build_pagination_meta(
            page, page_size, total, simulation_notice=TOLERANCE_SIMULATION_NOTICE
        ),
        request_id=request_id_ctx.get(),
    )


@reconciliation_router.post(
    "",
    response_model=ReconciliationEnvelope,
    status_code=status.HTTP_201_CREATED,
)
async def create_or_trigger_reconciliation(
    body: TriggerReconciliationRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS,),
                required_permissions=("reconciliations.calculate",),
            )
        ),
    ],
    service: Annotated[ReconciliationService, Depends(get_reconciliation_service)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> ReconciliationEnvelope:
    case, replayed = await service.create_or_trigger(
        principal=principal,
        raw_idempotency_key=idempotency_key,
        delivery_order_id=body.delivery_order_id,
        weight_basis=body.weight_basis,
    )
    return ReconciliationEnvelope(
        data=reconciliation_to_dto(case),
        meta=SimpleSuccessMeta(
            simulation_notice=TOLERANCE_SIMULATION_NOTICE,
            idempotency_replayed=True if replayed else False,
        ),
        request_id=request_id_ctx.get(),
    )


@reconciliation_router.get("/{reconciliation_id}", response_model=ReconciliationEnvelope)
async def get_reconciliation_detail(
    reconciliation_id: UUID,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("reconciliations.read",),
            )
        ),
    ],
    service: Annotated[ReconciliationService, Depends(get_reconciliation_service)],
) -> ReconciliationEnvelope:
    case = await service.get_case_detail(principal=principal, reconciliation_id=reconciliation_id)
    return ReconciliationEnvelope(
        data=reconciliation_to_dto(case),
        meta=SimpleSuccessMeta(simulation_notice=TOLERANCE_SIMULATION_NOTICE),
        request_id=request_id_ctx.get(),
    )


@reconciliation_router.post("/{reconciliation_id}/calculate", response_model=ReconciliationEnvelope)
async def calculate_reconciliation(
    reconciliation_id: UUID,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS,),
                required_permissions=("reconciliations.calculate",),
            )
        ),
    ],
    service: Annotated[ReconciliationService, Depends(get_reconciliation_service)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> ReconciliationEnvelope:
    case, replayed = await service.calculate(
        principal=principal,
        raw_idempotency_key=idempotency_key,
        reconciliation_id=reconciliation_id,
    )
    return ReconciliationEnvelope(
        data=reconciliation_to_dto(case),
        meta=SimpleSuccessMeta(
            simulation_notice=TOLERANCE_SIMULATION_NOTICE,
            idempotency_replayed=True if replayed else False,
        ),
        request_id=request_id_ctx.get(),
    )


@reconciliation_router.post("/{reconciliation_id}/review", response_model=ReconciliationEnvelope)
async def submit_dispute_review(
    reconciliation_id: UUID,
    body: DisputeReviewRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS,),
                required_permissions=("reconciliations.review",),
            )
        ),
    ],
    service: Annotated[ReconciliationService, Depends(get_reconciliation_service)],
) -> ReconciliationEnvelope:
    case = await service.submit_review(
        principal=principal,
        reconciliation_id=reconciliation_id,
        decision=body.decision,
        reason=body.reason,
        evidence_file_id=body.evidence_file_id,
        proposed_settlement_weight_raw=body.proposed_settlement_weight_kg,
    )
    return ReconciliationEnvelope(
        data=reconciliation_to_dto(case),
        meta=SimpleSuccessMeta(simulation_notice=TOLERANCE_SIMULATION_NOTICE),
        request_id=request_id_ctx.get(),
    )


@reconciliation_router.post("/{reconciliation_id}/resolve", response_model=ReconciliationEnvelope)
async def resolve_reconciliation_dispute(
    reconciliation_id: UUID,
    body: ResolveDisputeRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS, RoleCode.DIRECTOR),
                required_permissions=("reconciliations.resolve",),
            )
        ),
    ],
    service: Annotated[ReconciliationService, Depends(get_reconciliation_service)],
) -> ReconciliationEnvelope:
    case = await service.resolve_dispute(
        principal=principal,
        reconciliation_id=reconciliation_id,
        decision=body.decision,
        final_outcome=body.final_outcome,
        agreed_settlement_weight_raw=body.agreed_settlement_weight_kg,
        reason=body.reason,
        evidence_file_id=body.evidence_file_id,
    )
    return ReconciliationEnvelope(
        data=reconciliation_to_dto(case),
        meta=SimpleSuccessMeta(simulation_notice=TOLERANCE_SIMULATION_NOTICE),
        request_id=request_id_ctx.get(),
    )


@reconciliation_router.post(
    "/{reconciliation_id}/allocations", response_model=AllocationListEnvelope
)
async def simulate_or_compute_farmer_allocations(
    reconciliation_id: UUID,
    body: ComputeAllocationsRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS, RoleCode.PERUMDA_FINANCE),
                required_permissions=("allocations.compute",),
            )
        ),
    ],
    service: Annotated[ReconciliationService, Depends(get_reconciliation_service)],
) -> AllocationListEnvelope:
    allocations = await service.compute_allocations(
        principal=principal,
        reconciliation_id=reconciliation_id,
        mode=body.mode,
        allocation_policy_version_id=body.allocation_policy_version_id,
    )
    return AllocationListEnvelope(
        data=[allocation_to_dto(a) for a in allocations],
        meta=SimpleSuccessMeta(simulation_notice=TOLERANCE_SIMULATION_NOTICE),
        request_id=request_id_ctx.get(),
    )
