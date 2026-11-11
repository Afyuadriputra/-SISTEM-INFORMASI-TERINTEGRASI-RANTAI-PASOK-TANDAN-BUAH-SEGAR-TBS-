"""FastAPI endpoints for Internal Multi-Mill Pricing (/api/v1/prices/*)."""

from __future__ import annotations

from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status

from app.core.logging import request_id_ctx
from app.core.schemas import SimpleSuccessMeta, build_pagination_meta
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.presentation.dependencies import require_access
from app.modules.pricing.application.use_cases import PricingService
from app.modules.pricing.domain.entities import PriceQuoteStatus
from app.modules.pricing.presentation.schemas import (
    CreateDisbunPriceRequest,
    CreatePriceDraftRequest,
    DisbunPriceEnvelope,
    InternalPriceEnvelope,
    InternalPriceListEnvelope,
    PricingMetadataDto,
    PricingMetadataEnvelope,
    RevokePriceRequest,
    UpdatePriceDraftRequest,
    VerifyPriceRequest,
    category_to_dto,
    disbun_to_dto,
    quote_to_internal_dto,
    source_to_dto,
)

pricing_router = APIRouter(prefix="/api/v1/prices", tags=["Pricing"])


def get_pricing_service(request: Request) -> PricingService:
    """Resolve PricingService wired in composition root."""
    return cast(PricingService, request.app.state.pricing_service)


@pricing_router.get("/reference-meta", response_model=PricingMetadataEnvelope)
async def get_pricing_metadata(
    _principal: Annotated[
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
                required_permissions=("prices.read",),
            )
        ),
    ],
    service: Annotated[PricingService, Depends(get_pricing_service)],
) -> PricingMetadataEnvelope:
    sources, categories = await service.get_reference_metadata()
    return PricingMetadataEnvelope(
        data=PricingMetadataDto(
            sources=[source_to_dto(s) for s in sources],
            categories=[category_to_dto(c) for c in categories],
        ),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@pricing_router.get("", response_model=InternalPriceListEnvelope)
async def list_internal_prices(
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
                required_permissions=("prices.read",),
            )
        ),
    ],
    service: Annotated[PricingService, Depends(get_pricing_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    quote_status: Annotated[PriceQuoteStatus | None, Query(alias="status")] = None,
    mill_id: Annotated[UUID | None, Query()] = None,
) -> InternalPriceListEnvelope:
    rows, total = await service.list_internal_prices(
        principal=principal,
        status=quote_status,
        mill_id=mill_id,
        page=page,
        page_size=page_size,
    )
    return InternalPriceListEnvelope(
        data=[quote_to_internal_dto(r) for r in rows],
        meta=build_pagination_meta(
            page,
            page_size,
            total,
            simulation_notice="Data Simulasi — Harga non-publik tetap terlindungi oleh hak akses.",
        ),
        request_id=request_id_ctx.get(),
    )


@pricing_router.post("", response_model=InternalPriceEnvelope, status_code=status.HTTP_201_CREATED)
async def create_price_draft(
    payload: CreatePriceDraftRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS,),
                required_permissions=("prices.create",),
            )
        ),
    ],
    service: Annotated[PricingService, Depends(get_pricing_service)],
) -> InternalPriceEnvelope:
    created = await service.create_price_draft(
        principal=principal,
        mill_id=payload.mill_id,
        price_category_id=payload.price_category_id,
        source_id=payload.source_id,
        price_per_kg_raw=payload.price_per_kg,
        effective_from=payload.effective_from,
        effective_until=payload.effective_until,
        source_document_id=payload.source_document_id,
        notes=payload.notes,
    )
    return InternalPriceEnvelope(
        data=quote_to_internal_dto(created),
        meta=SimpleSuccessMeta(),
        request_id=request_id_ctx.get(),
    )


@pricing_router.post(
    "/disbun", response_model=DisbunPriceEnvelope, status_code=status.HTTP_201_CREATED
)
async def create_disbun_reference_price(
    payload: CreateDisbunPriceRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS,),
                required_permissions=("prices.create",),
            )
        ),
    ],
    service: Annotated[PricingService, Depends(get_pricing_service)],
) -> DisbunPriceEnvelope:
    created = await service.create_disbun_price(
        principal=principal,
        price_source_id=payload.price_source_id,
        price_category_id=payload.price_category_id,
        price_per_kg_raw=payload.price_per_kg,
        effective_from=payload.effective_from,
        effective_until=payload.effective_until,
        source_document_id=payload.source_document_id,
    )
    return DisbunPriceEnvelope(
        data=disbun_to_dto(created),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@pricing_router.get("/{price_quote_id}", response_model=InternalPriceEnvelope)
async def get_internal_price(
    price_quote_id: UUID,
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
                required_permissions=("prices.read",),
            )
        ),
    ],
    service: Annotated[PricingService, Depends(get_pricing_service)],
) -> InternalPriceEnvelope:
    quote = await service.get_internal_price(principal=principal, price_quote_id=price_quote_id)
    return InternalPriceEnvelope(
        data=quote_to_internal_dto(quote),
        meta=SimpleSuccessMeta(),
        request_id=request_id_ctx.get(),
    )


@pricing_router.patch("/{price_quote_id}", response_model=InternalPriceEnvelope)
async def update_price_draft(
    price_quote_id: UUID,
    payload: UpdatePriceDraftRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS,),
                required_permissions=("prices.create",),
            )
        ),
    ],
    service: Annotated[PricingService, Depends(get_pricing_service)],
) -> InternalPriceEnvelope:
    fields = payload.model_fields_set
    updated = await service.update_price_draft(
        principal=principal,
        price_quote_id=price_quote_id,
        expected_version=payload.version,
        price_per_kg_raw=payload.price_per_kg,
        effective_from=payload.effective_from,
        effective_until=payload.effective_until,
        update_effective_until="effective_until" in fields,
        source_document_id=payload.source_document_id,
        update_source_doc="source_document_id" in fields,
        notes=payload.notes,
        update_notes="notes" in fields,
    )
    return InternalPriceEnvelope(
        data=quote_to_internal_dto(updated),
        meta=SimpleSuccessMeta(),
        request_id=request_id_ctx.get(),
    )


@pricing_router.post("/{price_quote_id}/submit", response_model=InternalPriceEnvelope)
async def submit_price_for_verification(
    price_quote_id: UUID,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS,),
                required_permissions=("prices.submit",),
            )
        ),
    ],
    service: Annotated[PricingService, Depends(get_pricing_service)],
) -> InternalPriceEnvelope:
    updated = await service.submit_price(principal=principal, price_quote_id=price_quote_id)
    return InternalPriceEnvelope(
        data=quote_to_internal_dto(updated),
        meta=SimpleSuccessMeta(),
        request_id=request_id_ctx.get(),
    )


@pricing_router.post("/{price_quote_id}/verify", response_model=InternalPriceEnvelope)
async def verify_or_reject_price(
    price_quote_id: UUID,
    payload: VerifyPriceRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS, RoleCode.DIRECTOR),
                required_permissions=("prices.verify",),
            )
        ),
    ],
    service: Annotated[PricingService, Depends(get_pricing_service)],
) -> InternalPriceEnvelope:
    updated = await service.verify_or_reject_price(
        principal=principal,
        price_quote_id=price_quote_id,
        decision=payload.decision,
        reason=payload.reason,
    )
    return InternalPriceEnvelope(
        data=quote_to_internal_dto(updated),
        meta=SimpleSuccessMeta(),
        request_id=request_id_ctx.get(),
    )


@pricing_router.post("/{price_quote_id}/publish", response_model=InternalPriceEnvelope)
async def publish_price(
    price_quote_id: UUID,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS,),
                required_permissions=("prices.publish",),
            )
        ),
    ],
    service: Annotated[PricingService, Depends(get_pricing_service)],
) -> InternalPriceEnvelope:
    updated = await service.publish_price(principal=principal, price_quote_id=price_quote_id)
    return InternalPriceEnvelope(
        data=quote_to_internal_dto(updated),
        meta=SimpleSuccessMeta(),
        request_id=request_id_ctx.get(),
    )


@pricing_router.post("/{price_quote_id}/revoke", response_model=InternalPriceEnvelope)
async def revoke_price(
    price_quote_id: UUID,
    payload: RevokePriceRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS,),
                required_permissions=("prices.revoke",),
            )
        ),
    ],
    service: Annotated[PricingService, Depends(get_pricing_service)],
) -> InternalPriceEnvelope:
    updated = await service.revoke_price(
        principal=principal,
        price_quote_id=price_quote_id,
        reason=payload.reason,
    )
    return InternalPriceEnvelope(
        data=quote_to_internal_dto(updated),
        meta=SimpleSuccessMeta(),
        request_id=request_id_ctx.get(),
    )
