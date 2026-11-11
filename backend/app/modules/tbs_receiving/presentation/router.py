"""FastAPI endpoints for TBS Receiving, Versioned Weighing, and Grading (/api/v1/receipts/*)."""

from __future__ import annotations

from datetime import date
from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, status

from app.core.logging import request_id_ctx
from app.core.schemas import SimpleSuccessMeta, build_pagination_meta
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.presentation.dependencies import require_access
from app.modules.tbs_receiving.application.use_cases import (
    GRADING_SIMULATION_NOTICE,
    TbsReceivingService,
)
from app.modules.tbs_receiving.domain.entities import ReceiptStatus
from app.modules.tbs_receiving.domain.rules import GradingInputItem
from app.modules.tbs_receiving.presentation.schemas import (
    CreateReceiptRequest,
    ReasonActionRequest,
    ReceiptEnvelope,
    ReceiptListEnvelope,
    RecordGradingRequest,
    RecordWeighingRequest,
    receipt_to_dto,
)

tbs_receiving_router = APIRouter(prefix="/api/v1/receipts", tags=["TBS Receiving"])


def get_tbs_receiving_service(request: Request) -> TbsReceivingService:
    """Resolve TbsReceivingService wired in composition root."""
    return cast(TbsReceivingService, request.app.state.tbs_receiving_service)


@tbs_receiving_router.get("", response_model=ReceiptListEnvelope)
async def list_receipts(
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.FARMER,
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("receipts.read",),
            )
        ),
    ],
    service: Annotated[TbsReceivingService, Depends(get_tbs_receiving_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
    receipt_status: Annotated[ReceiptStatus | None, Query(alias="status")] = None,
) -> ReceiptListEnvelope:
    rows, total = await service.list_receipts(
        principal=principal,
        status=receipt_status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    return ReceiptListEnvelope(
        data=[receipt_to_dto(r) for r in rows],
        meta=build_pagination_meta(page, page_size, total),
        request_id=request_id_ctx.get(),
    )


@tbs_receiving_router.post(
    "",
    response_model=ReceiptEnvelope,
    status_code=status.HTTP_201_CREATED,
)
async def create_receipt_draft(
    body: CreateReceiptRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.COOPERATIVE_OPERATOR,),
                required_permissions=("receipts.create",),
            )
        ),
    ],
    service: Annotated[TbsReceivingService, Depends(get_tbs_receiving_service)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> ReceiptEnvelope:
    receipt, replayed = await service.create_receipt_draft(
        principal=principal,
        raw_idempotency_key=idempotency_key,
        farmer_id=body.farmer_id,
        farm_id=body.farm_id,
        harvest_date=body.harvest_date,
        received_at=body.received_at,
        notes=body.notes,
    )
    return ReceiptEnvelope(
        data=receipt_to_dto(receipt),
        meta=SimpleSuccessMeta(idempotency_replayed=True if replayed else False),
        request_id=request_id_ctx.get(),
    )


@tbs_receiving_router.get("/{receipt_id}", response_model=ReceiptEnvelope)
async def get_receipt_detail(
    receipt_id: UUID,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.FARMER,
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("receipts.read",),
            )
        ),
    ],
    service: Annotated[TbsReceivingService, Depends(get_tbs_receiving_service)],
) -> ReceiptEnvelope:
    receipt = await service.get_receipt_detail(principal=principal, receipt_id=receipt_id)
    sim_notice = GRADING_SIMULATION_NOTICE if receipt.grading_items else None
    return ReceiptEnvelope(
        data=receipt_to_dto(receipt),
        meta=SimpleSuccessMeta(simulation_notice=sim_notice),
        request_id=request_id_ctx.get(),
    )


@tbs_receiving_router.post("/{receipt_id}/weighing", response_model=ReceiptEnvelope)
async def record_receipt_weighing(
    receipt_id: UUID,
    body: RecordWeighingRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.COOPERATIVE_OPERATOR,),
                required_permissions=("receipts.weigh",),
            )
        ),
    ],
    service: Annotated[TbsReceivingService, Depends(get_tbs_receiving_service)],
) -> ReceiptEnvelope:
    receipt = await service.record_weighing(
        principal=principal,
        receipt_id=receipt_id,
        gross_weight_kg_raw=body.gross_weight_kg,
        tare_weight_kg_raw=body.tare_weight_kg,
        correction_reason=body.correction_reason,
        expected_version=body.version,
    )
    return ReceiptEnvelope(
        data=receipt_to_dto(receipt),
        meta=SimpleSuccessMeta(),
        request_id=request_id_ctx.get(),
    )


@tbs_receiving_router.post("/{receipt_id}/grading", response_model=ReceiptEnvelope)
async def record_receipt_grading(
    receipt_id: UUID,
    body: RecordGradingRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.COOPERATIVE_OPERATOR,),
                required_permissions=("receipts.weigh",),
            )
        ),
    ],
    service: Annotated[TbsReceivingService, Depends(get_tbs_receiving_service)],
) -> ReceiptEnvelope:
    receipt = await service.record_grading(
        principal=principal,
        receipt_id=receipt_id,
        items=[
            GradingInputItem(
                grading_category=item.grading_category,
                measurement_value_raw=item.measurement_value,
                deduction_type=item.deduction_type,
                deduction_value_raw=item.deduction_value,
                calculation_basis=item.calculation_basis,
                notes=item.notes,
            )
            for item in body.items
        ],
        expected_version=body.version,
    )
    return ReceiptEnvelope(
        data=receipt_to_dto(receipt),
        meta=SimpleSuccessMeta(simulation_notice=GRADING_SIMULATION_NOTICE),
        request_id=request_id_ctx.get(),
    )


@tbs_receiving_router.post("/{receipt_id}/validate", response_model=ReceiptEnvelope)
async def validate_receipt(
    receipt_id: UUID,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.COOPERATIVE_OPERATOR,),
                required_permissions=("receipts.validate",),
            )
        ),
    ],
    service: Annotated[TbsReceivingService, Depends(get_tbs_receiving_service)],
) -> ReceiptEnvelope:
    receipt = await service.validate_receipt(principal=principal, receipt_id=receipt_id)
    sim_notice = GRADING_SIMULATION_NOTICE if receipt.grading_items else None
    return ReceiptEnvelope(
        data=receipt_to_dto(receipt),
        meta=SimpleSuccessMeta(simulation_notice=sim_notice),
        request_id=request_id_ctx.get(),
    )


@tbs_receiving_router.post("/{receipt_id}/cancel", response_model=ReceiptEnvelope)
async def cancel_receipt(
    receipt_id: UUID,
    body: ReasonActionRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.COOPERATIVE_OPERATOR,),
                required_permissions=("receipts.cancel",),
            )
        ),
    ],
    service: Annotated[TbsReceivingService, Depends(get_tbs_receiving_service)],
) -> ReceiptEnvelope:
    receipt = await service.cancel_receipt(
        principal=principal,
        receipt_id=receipt_id,
        reason=body.reason,
        expected_version=body.version,
    )
    return ReceiptEnvelope(
        data=receipt_to_dto(receipt),
        meta=SimpleSuccessMeta(),
        request_id=request_id_ctx.get(),
    )
