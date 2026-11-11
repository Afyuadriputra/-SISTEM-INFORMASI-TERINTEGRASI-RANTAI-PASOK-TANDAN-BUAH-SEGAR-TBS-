"""FastAPI endpoints for Mill Weighing Tickets (/api/v1/mill-tickets/*)."""

from __future__ import annotations

from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, status

from app.core.logging import request_id_ctx
from app.core.schemas import SimpleSuccessMeta, build_pagination_meta
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.presentation.dependencies import require_access
from app.modules.mill_weighing.application.use_cases import MillWeighingService
from app.modules.mill_weighing.domain.entities import MillTicketStatus
from app.modules.mill_weighing.domain.rules import MillGradingInput
from app.modules.mill_weighing.presentation.schemas import (
    CreateMillTicketRequest,
    MillTicketEnvelope,
    MillTicketListEnvelope,
    ReviseMillTicketRequest,
    mill_ticket_to_dto,
)

mill_weighing_router = APIRouter(prefix="/api/v1/mill-tickets", tags=["Mill Weighing"])


def get_mill_weighing_service(request: Request) -> MillWeighingService:
    """Resolve MillWeighingService wired in composition root."""
    return cast(MillWeighingService, request.app.state.mill_weighing_service)


@mill_weighing_router.get("", response_model=MillTicketListEnvelope)
async def list_mill_tickets(
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.MILL_OPERATOR,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("mill_tickets.read",),
            )
        ),
    ],
    service: Annotated[MillWeighingService, Depends(get_mill_weighing_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    ticket_status: Annotated[MillTicketStatus | None, Query(alias="status")] = None,
) -> MillTicketListEnvelope:
    rows, total = await service.list_tickets(
        principal=principal,
        status_filter=ticket_status,
        page=page,
        page_size=page_size,
    )
    return MillTicketListEnvelope(
        data=[mill_ticket_to_dto(r) for r in rows],
        meta=build_pagination_meta(page, page_size, total),
        request_id=request_id_ctx.get(),
    )


@mill_weighing_router.post(
    "",
    response_model=MillTicketEnvelope,
    status_code=status.HTTP_201_CREATED,
)
async def create_mill_ticket(
    body: CreateMillTicketRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.MILL_OPERATOR,),
                required_permissions=("mill_tickets.create",),
            )
        ),
    ],
    service: Annotated[MillWeighingService, Depends(get_mill_weighing_service)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> MillTicketEnvelope:
    ticket, replayed = await service.create_ticket(
        principal=principal,
        raw_idempotency_key=idempotency_key,
        delivery_order_id=body.delivery_order_id,
        ticket_number=body.ticket_number,
        gross_weight_kg_raw=body.gross_weight_kg,
        tare_weight_kg_raw=body.tare_weight_kg,
        weighed_at=body.weighed_at,
        proof_file_id=body.proof_file_id,
        grading_items=[
            MillGradingInput(
                grading_category=g.grading_category,
                deduction_type=g.deduction_type,
                deduction_value_raw=g.deduction_value,
                calculation_basis=g.calculation_basis,
                notes=g.notes,
            )
            for g in body.grading_items
        ],
    )
    return MillTicketEnvelope(
        data=mill_ticket_to_dto(ticket),
        meta=SimpleSuccessMeta(idempotency_replayed=True if replayed else False),
        request_id=request_id_ctx.get(),
    )


@mill_weighing_router.get("/{ticket_id}", response_model=MillTicketEnvelope)
async def get_mill_ticket_detail(
    ticket_id: UUID,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.MILL_OPERATOR,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("mill_tickets.read",),
            )
        ),
    ],
    service: Annotated[MillWeighingService, Depends(get_mill_weighing_service)],
) -> MillTicketEnvelope:
    ticket = await service.get_ticket_detail(principal=principal, ticket_id=ticket_id)
    return MillTicketEnvelope(
        data=mill_ticket_to_dto(ticket),
        meta=SimpleSuccessMeta(),
        request_id=request_id_ctx.get(),
    )


@mill_weighing_router.patch("/{ticket_id}", response_model=MillTicketEnvelope)
async def revise_mill_ticket(
    ticket_id: UUID,
    body: ReviseMillTicketRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.MILL_OPERATOR,),
                required_permissions=("mill_tickets.create",),
            )
        ),
    ],
    service: Annotated[MillWeighingService, Depends(get_mill_weighing_service)],
) -> MillTicketEnvelope:
    ticket = await service.revise_ticket(
        principal=principal,
        ticket_id=ticket_id,
        gross_weight_kg_raw=body.gross_weight_kg,
        tare_weight_kg_raw=body.tare_weight_kg,
        proof_file_id=body.proof_file_id,
        correction_reason=body.correction_reason,
    )
    return MillTicketEnvelope(
        data=mill_ticket_to_dto(ticket),
        meta=SimpleSuccessMeta(),
        request_id=request_id_ctx.get(),
    )


@mill_weighing_router.post("/{ticket_id}/verify", response_model=MillTicketEnvelope)
async def verify_mill_ticket(
    ticket_id: UUID,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.MILL_OPERATOR,),
                required_permissions=("mill_tickets.verify",),
            )
        ),
    ],
    service: Annotated[MillWeighingService, Depends(get_mill_weighing_service)],
) -> MillTicketEnvelope:
    ticket = await service.verify_ticket(principal=principal, ticket_id=ticket_id)
    return MillTicketEnvelope(
        data=mill_ticket_to_dto(ticket),
        meta=SimpleSuccessMeta(),
        request_id=request_id_ctx.get(),
    )
