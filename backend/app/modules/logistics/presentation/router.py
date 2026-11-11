"""FastAPI endpoints for Logistics & e-DO (/api/v1/delivery-orders/*)."""

from __future__ import annotations

from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, status

from app.core.logging import request_id_ctx
from app.core.schemas import SimpleSuccessMeta, build_pagination_meta
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.presentation.dependencies import require_access
from app.modules.logistics.application.use_cases import EDO_ISSUANCE_NOTICE, LogisticsService
from app.modules.logistics.domain.entities import DeliveryOrderStatus
from app.modules.logistics.presentation.schemas import (
    CancelDeliveryOrderRequest,
    CreateDeliveryOrderDraftRequest,
    DeliveryOrderEnvelope,
    DeliveryOrderListEnvelope,
    IssueDeliveryOrderRequest,
    TransitionDeliveryStatusRequest,
    VerifyDeliveryQrRequest,
    delivery_order_to_dto,
)

logistics_router = APIRouter(prefix="/api/v1/delivery-orders", tags=["Logistics & e-DO"])


def get_logistics_service(request: Request) -> LogisticsService:
    """Resolve LogisticsService wired in composition root."""
    return cast(LogisticsService, request.app.state.logistics_service)


@logistics_router.get("", response_model=DeliveryOrderListEnvelope)
async def list_delivery_orders(
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.FARMER,
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.MILL_OPERATOR,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("delivery_orders.read",),
            )
        ),
    ],
    service: Annotated[LogisticsService, Depends(get_logistics_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    do_status: Annotated[DeliveryOrderStatus | None, Query(alias="status")] = None,
    mill_id: Annotated[UUID | None, Query()] = None,
) -> DeliveryOrderListEnvelope:
    rows, total = await service.list_delivery_orders(
        principal=principal,
        status_filter=do_status,
        mill_id=mill_id,
        page=page,
        page_size=page_size,
    )
    return DeliveryOrderListEnvelope(
        data=[delivery_order_to_dto(r) for r in rows],
        meta=build_pagination_meta(page, page_size, total),
        request_id=request_id_ctx.get(),
    )


@logistics_router.post(
    "",
    response_model=DeliveryOrderEnvelope,
    status_code=status.HTTP_201_CREATED,
)
async def create_delivery_order_draft(
    body: CreateDeliveryOrderDraftRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.COOPERATIVE_OPERATOR, RoleCode.PERUMDA_OPERATIONS),
                required_permissions=("delivery_orders.create",),
            )
        ),
    ],
    service: Annotated[LogisticsService, Depends(get_logistics_service)],
) -> DeliveryOrderEnvelope:
    do = await service.create_draft(
        principal=principal,
        mill_id=body.mill_id,
        contract_id=body.contract_id,
        vehicle_id=body.vehicle_id,
        driver_id=body.driver_id,
        receipt_ids=body.receipt_ids,
    )
    return DeliveryOrderEnvelope(
        data=delivery_order_to_dto(do),
        meta=SimpleSuccessMeta(simulation_notice=EDO_ISSUANCE_NOTICE),
        request_id=request_id_ctx.get(),
    )


@logistics_router.post("/verify-qr", response_model=DeliveryOrderEnvelope)
async def verify_delivery_order_qr(
    body: VerifyDeliveryQrRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.MILL_OPERATOR,),
                required_permissions=("delivery_orders.verify_arrival",),
            )
        ),
    ],
    service: Annotated[LogisticsService, Depends(get_logistics_service)],
) -> DeliveryOrderEnvelope:
    do = await service.verify_qr_arrival(
        principal=principal,
        qr_token_or_edo_number=body.qr_token_or_edo_number,
        observed_plate_number=body.observed_plate_number,
    )
    return DeliveryOrderEnvelope(
        data=delivery_order_to_dto(do),
        meta=SimpleSuccessMeta(),
        request_id=request_id_ctx.get(),
    )


@logistics_router.get("/{delivery_order_id}", response_model=DeliveryOrderEnvelope)
async def get_delivery_order_detail(
    delivery_order_id: UUID,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.FARMER,
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.MILL_OPERATOR,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("delivery_orders.read",),
            )
        ),
    ],
    service: Annotated[LogisticsService, Depends(get_logistics_service)],
) -> DeliveryOrderEnvelope:
    do = await service.get_delivery_order_detail(
        principal=principal,
        delivery_order_id=delivery_order_id,
    )
    return DeliveryOrderEnvelope(
        data=delivery_order_to_dto(do),
        meta=SimpleSuccessMeta(),
        request_id=request_id_ctx.get(),
    )


@logistics_router.post("/{delivery_order_id}/issue", response_model=DeliveryOrderEnvelope)
async def issue_delivery_order(
    delivery_order_id: UUID,
    body: IssueDeliveryOrderRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.COOPERATIVE_OPERATOR, RoleCode.PERUMDA_OPERATIONS),
                required_permissions=("delivery_orders.issue",),
            )
        ),
    ],
    service: Annotated[LogisticsService, Depends(get_logistics_service)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> DeliveryOrderEnvelope:
    do, replayed = await service.issue_delivery_order(
        principal=principal,
        raw_idempotency_key=idempotency_key,
        delivery_order_id=delivery_order_id,
        expected_version=body.version,
        confirm_lock_allocations=body.confirm_lock_allocations,
    )
    return DeliveryOrderEnvelope(
        data=delivery_order_to_dto(do),
        meta=SimpleSuccessMeta(
            simulation_notice=EDO_ISSUANCE_NOTICE,
            idempotency_replayed=True if replayed else False,
        ),
        request_id=request_id_ctx.get(),
    )


@logistics_router.post("/{delivery_order_id}/status", response_model=DeliveryOrderEnvelope)
async def transition_delivery_order_status(
    delivery_order_id: UUID,
    body: TransitionDeliveryStatusRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.COOPERATIVE_OPERATOR, RoleCode.PERUMDA_OPERATIONS),
                required_permissions=("delivery_orders.transition",),
            )
        ),
    ],
    service: Annotated[LogisticsService, Depends(get_logistics_service)],
) -> DeliveryOrderEnvelope:
    do = await service.transition_status(
        principal=principal,
        delivery_order_id=delivery_order_id,
        target_status=body.target_status,
        reason=body.reason,
        expected_version=body.version,
    )
    return DeliveryOrderEnvelope(
        data=delivery_order_to_dto(do),
        meta=SimpleSuccessMeta(),
        request_id=request_id_ctx.get(),
    )


@logistics_router.post("/{delivery_order_id}/cancel", response_model=DeliveryOrderEnvelope)
async def cancel_delivery_order(
    delivery_order_id: UUID,
    body: CancelDeliveryOrderRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.COOPERATIVE_OPERATOR, RoleCode.PERUMDA_OPERATIONS),
                required_permissions=("delivery_orders.cancel",),
            )
        ),
    ],
    service: Annotated[LogisticsService, Depends(get_logistics_service)],
) -> DeliveryOrderEnvelope:
    do = await service.cancel_delivery_order(
        principal=principal,
        delivery_order_id=delivery_order_id,
        reason=body.reason,
        expected_version=body.version,
    )
    return DeliveryOrderEnvelope(
        data=delivery_order_to_dto(do),
        meta=SimpleSuccessMeta(simulation_notice=EDO_ISSUANCE_NOTICE),
        request_id=request_id_ctx.get(),
    )
