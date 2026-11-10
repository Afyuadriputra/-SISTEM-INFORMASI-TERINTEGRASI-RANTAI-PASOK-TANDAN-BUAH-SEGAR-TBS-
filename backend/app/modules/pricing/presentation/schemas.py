"""Strict Pydantic schemas aligned 1:1 with OpenAPI Pricing & Disbun contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from app.core.logging import format_utc_iso
from app.core.schemas import (
    PaginationMeta,
    SimpleSuccessMeta,
    StrictContractModel,
    format_decimal,
)
from app.modules.pricing.domain.entities import (
    DisbunReferencePriceEntity,
    MillPriceQuoteEntity,
    PriceCategoryEntity,
    PriceDisplayStatus,
    PriceQuoteStatus,
    PriceSourceEntity,
    PriceSourceType,
    VerifyDecision,
)


class PriceSourceDto(StrictContractModel):
    id: UUID
    source_code: str
    source_name: str
    source_type: PriceSourceType
    status: str


class PriceCategoryDto(StrictContractModel):
    id: UUID
    category_code: str
    name: str
    unit: str
    quality_basis: str
    age_group: str | None
    is_active: bool


class PricingMetadataDto(StrictContractModel):
    sources: list[PriceSourceDto]
    categories: list[PriceCategoryDto]


class PricingMetadataEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: PricingMetadataDto
    meta: dict[str, Any] | None = None
    request_id: str


class PriceVerificationEventDto(StrictContractModel):
    id: UUID
    action: str
    previous_status: PriceQuoteStatus
    new_status: PriceQuoteStatus
    actor_id: UUID
    reason: str | None
    created_at: str


class InternalPriceQuoteDto(StrictContractModel):
    id: UUID
    mill_id: UUID
    mill_name: str
    mill_code: str
    regency: str
    price_category_id: UUID
    price_category_code: str
    price_category_name: str
    unit: str
    source_id: UUID
    source_name: str
    source_type: Literal["DISBUN", "MILL_OFFICIAL", "MILL_DOCUMENT", "MANUAL"]
    price_per_kg: str
    effective_from: str
    effective_until: str | None
    status: PriceQuoteStatus
    display_status: PriceDisplayStatus
    is_expired: bool
    submitted_by: UUID
    verified_by: UUID | None
    verified_at: str | None
    published_at: str | None
    source_document_id: UUID | None
    notes: str | None
    version: int = Field(ge=1)
    is_simulation: bool
    created_at: str
    updated_at: str
    verification_events: list[PriceVerificationEventDto]


class InternalPriceEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: InternalPriceQuoteDto
    meta: SimpleSuccessMeta | None = None
    request_id: str


class InternalPriceListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[InternalPriceQuoteDto]
    meta: PaginationMeta
    request_id: str


class CreatePriceDraftRequest(StrictContractModel):
    mill_id: UUID
    price_category_id: UUID
    source_id: UUID
    price_per_kg: str
    effective_from: datetime
    effective_until: datetime | None = None
    source_document_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=1000)


class UpdatePriceDraftRequest(StrictContractModel):
    price_per_kg: str | None = None
    effective_from: datetime | None = None
    effective_until: datetime | None = None
    source_document_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=1000)
    version: int = Field(ge=1)


class VerifyPriceRequest(StrictContractModel):
    decision: VerifyDecision
    reason: str | None = Field(default=None, max_length=500)


class RevokePriceRequest(StrictContractModel):
    reason: str = Field(min_length=5, max_length=500)


class CreateDisbunPriceRequest(StrictContractModel):
    price_source_id: UUID
    price_category_id: UUID
    price_per_kg: str
    effective_from: datetime
    effective_until: datetime | None = None
    source_document_id: UUID | None = None


class PublicDisbunPriceDto(StrictContractModel):
    id: UUID
    source_name: str
    category_code: str
    category_name: str
    age_group: str | None
    price_per_kg: str
    effective_from: str
    effective_until: str | None
    verification_status: Literal["VERIFIED", "PUBLISHED"]
    created_at: str


class DisbunPriceEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: PublicDisbunPriceDto
    meta: dict[str, Any] | None = None
    request_id: str


def _internal_source_type(
    raw: PriceSourceType,
) -> Literal["DISBUN", "MILL_OFFICIAL", "MILL_DOCUMENT", "MANUAL"]:
    if raw == PriceSourceType.VERIFIED_MANUAL:
        return "MANUAL"
    return raw.value  # type: ignore[return-value]


def quote_to_internal_dto(e: MillPriceQuoteEntity) -> InternalPriceQuoteDto:
    now = datetime.now(UTC)
    return InternalPriceQuoteDto(
        id=e.id,
        mill_id=e.mill_id,
        mill_name=e.mill_name,
        mill_code=e.mill_code,
        regency=e.regency,
        price_category_id=e.price_category_id,
        price_category_code=e.price_category_code,
        price_category_name=e.price_category_name,
        unit=e.unit,
        source_id=e.source_id,
        source_name=e.source_name,
        source_type=_internal_source_type(e.source_type),
        price_per_kg=format_decimal(e.price_per_kg, 2) or "0.00",
        effective_from=format_utc_iso(e.effective_from) or "",
        effective_until=format_utc_iso(e.effective_until),
        status=e.status,
        display_status=e.display_status_at(now),
        is_expired=e.is_expired_at(now),
        submitted_by=e.submitted_by,
        verified_by=e.verified_by,
        verified_at=format_utc_iso(e.verified_at),
        published_at=format_utc_iso(e.published_at),
        source_document_id=e.source_document_id,
        notes=e.notes,
        version=e.version,
        is_simulation=e.is_simulation,
        created_at=format_utc_iso(e.created_at) or "",
        updated_at=format_utc_iso(e.updated_at) or "",
        verification_events=[
            PriceVerificationEventDto(
                id=ev.id,
                action=ev.action,
                previous_status=ev.previous_status,
                new_status=ev.new_status,
                actor_id=ev.actor_id,
                reason=ev.reason,
                created_at=format_utc_iso(ev.created_at) or "",
            )
            for ev in e.verification_events
        ],
    )


def source_to_dto(s: PriceSourceEntity) -> PriceSourceDto:
    return PriceSourceDto(
        id=s.id,
        source_code=s.source_code,
        source_name=s.source_name,
        source_type=s.source_type,
        status=s.status,
    )


def category_to_dto(c: PriceCategoryEntity) -> PriceCategoryDto:
    return PriceCategoryDto(
        id=c.id,
        category_code=c.category_code,
        name=c.name,
        unit=c.unit,
        quality_basis=c.quality_basis,
        age_group=c.age_group,
        is_active=c.is_active,
    )


def disbun_to_dto(d: DisbunReferencePriceEntity) -> PublicDisbunPriceDto:
    ver_stat: Literal["VERIFIED", "PUBLISHED"] = (
        "VERIFIED" if d.verification_status == "VERIFIED" else "PUBLISHED"
    )
    return PublicDisbunPriceDto(
        id=d.id,
        source_name=d.source_name,
        category_code=d.category_code,
        category_name=d.category_name,
        age_group=d.age_group,
        price_per_kg=format_decimal(d.price_per_kg, 2) or "0.00",
        effective_from=format_utc_iso(d.effective_from) or "",
        effective_until=format_utc_iso(d.effective_until),
        verification_status=ver_stat,
        created_at=format_utc_iso(d.created_at) or "",
    )
