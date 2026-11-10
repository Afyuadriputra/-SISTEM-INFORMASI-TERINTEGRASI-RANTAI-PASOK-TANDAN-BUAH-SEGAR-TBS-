"""FastAPI endpoints for Commercial Contracts & Quota (/api/v1/contracts/*)."""

from __future__ import annotations

from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, status

from app.core.logging import request_id_ctx
from app.core.schemas import SimpleSuccessMeta, build_pagination_meta
from app.modules.contracts.application.use_cases import (
    CONTRACT_POLICY_NOTICE,
    ContractsService,
)
from app.modules.contracts.domain.entities import ContractStatus
from app.modules.contracts.presentation.schemas import (
    ContractEnvelope,
    ContractListEnvelope,
    CreateContractRequest,
    QuotaPeriodListEnvelope,
    QuotaReservationEnvelope,
    ReserveQuotaRequest,
    contract_to_dto,
    period_to_dto,
    reservation_to_dto,
)
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.presentation.dependencies import require_access

contracts_router = APIRouter(prefix="/api/v1/contracts", tags=["Contracts & Quota"])


def get_contracts_service(request: Request) -> ContractsService:
    """Resolve ContractsService wired in composition root."""
    return cast(ContractsService, request.app.state.contracts_service)


@contracts_router.get("", response_model=ContractListEnvelope)
async def list_contracts(
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("contracts.read",),
            )
        ),
    ],
    service: Annotated[ContractsService, Depends(get_contracts_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    contract_status: Annotated[ContractStatus | None, Query(alias="status")] = None,
    mill_id: Annotated[UUID | None, Query()] = None,
) -> ContractListEnvelope:
    rows, total = await service.list_contracts(
        status_filter=contract_status,
        mill_id=mill_id,
        page=page,
        page_size=page_size,
    )
    return ContractListEnvelope(
        data=[contract_to_dto(c) for c in rows],
        meta=build_pagination_meta(
            page, page_size, total, simulation_notice=CONTRACT_POLICY_NOTICE
        ),
        request_id=request_id_ctx.get(),
    )


@contracts_router.post(
    "",
    response_model=ContractEnvelope,
    status_code=status.HTTP_201_CREATED,
)
async def create_contract(
    body: CreateContractRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS,),
                required_permissions=("contracts.write",),
            )
        ),
    ],
    service: Annotated[ContractsService, Depends(get_contracts_service)],
) -> ContractEnvelope:
    contract = await service.create_contract(
        principal=principal,
        contract_number=body.contract_number,
        mill_id=body.mill_id,
        start_date=body.start_date,
        end_date=body.end_date,
        price_rule_type=body.price_rule_type,
        agreed_price_per_kg_raw=body.agreed_price_per_kg,
        business_model_code=body.business_model_code,
        perumda_role=body.perumda_role,
        seller_party_id=body.seller_party_id,
        buyer_party_id=body.buyer_party_id,
        agent_party_id=body.agent_party_id,
        represented_party_id=body.represented_party_id,
        payment_terms=body.payment_terms,
        initial_quota_kg_raw=body.initial_quota_kg,
    )
    return ContractEnvelope(
        data=contract_to_dto(contract),
        meta=SimpleSuccessMeta(simulation_notice=CONTRACT_POLICY_NOTICE),
        request_id=request_id_ctx.get(),
    )


@contracts_router.get("/{contract_id}", response_model=ContractEnvelope)
async def get_contract_detail(
    contract_id: UUID,
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("contracts.read",),
            )
        ),
    ],
    service: Annotated[ContractsService, Depends(get_contracts_service)],
) -> ContractEnvelope:
    contract = await service.get_contract_detail(contract_id=contract_id)
    return ContractEnvelope(
        data=contract_to_dto(contract),
        meta=SimpleSuccessMeta(simulation_notice=CONTRACT_POLICY_NOTICE),
        request_id=request_id_ctx.get(),
    )


@contracts_router.post("/{contract_id}/approve", response_model=ContractEnvelope)
async def approve_contract(
    contract_id: UUID,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.DIRECTOR,),
                required_permissions=("contracts.approve",),
            )
        ),
    ],
    service: Annotated[ContractsService, Depends(get_contracts_service)],
) -> ContractEnvelope:
    contract = await service.approve_contract(principal=principal, contract_id=contract_id)
    return ContractEnvelope(
        data=contract_to_dto(contract),
        meta=SimpleSuccessMeta(simulation_notice=CONTRACT_POLICY_NOTICE),
        request_id=request_id_ctx.get(),
    )


@contracts_router.get("/{contract_id}/quota", response_model=QuotaPeriodListEnvelope)
async def get_contract_quota_status(
    contract_id: UUID,
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("contracts.read",),
            )
        ),
    ],
    service: Annotated[ContractsService, Depends(get_contracts_service)],
) -> QuotaPeriodListEnvelope:
    periods = await service.get_quota_status(contract_id=contract_id)
    return QuotaPeriodListEnvelope(
        data=[period_to_dto(p) for p in periods],
        meta=SimpleSuccessMeta(simulation_notice=CONTRACT_POLICY_NOTICE),
        request_id=request_id_ctx.get(),
    )


@contracts_router.post(
    "/{contract_id}/reservations",
    response_model=QuotaReservationEnvelope,
    status_code=status.HTTP_201_CREATED,
)
async def reserve_contract_quota(
    contract_id: UUID,
    body: ReserveQuotaRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS,),
                required_permissions=("quotas.reserve",),
            )
        ),
    ],
    service: Annotated[ContractsService, Depends(get_contracts_service)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> QuotaReservationEnvelope:
    res, replayed = await service.reserve_quota(
        principal=principal,
        raw_idempotency_key=idempotency_key,
        contract_id=contract_id,
        quota_period_id=body.quota_period_id,
        delivery_order_id=body.delivery_order_id,
        reserved_weight_kg_raw=body.reserved_weight_kg,
    )
    return QuotaReservationEnvelope(
        data=reservation_to_dto(res),
        meta=SimpleSuccessMeta(
            simulation_notice=CONTRACT_POLICY_NOTICE,
            idempotency_replayed=True if replayed else False,
        ),
        request_id=request_id_ctx.get(),
    )
