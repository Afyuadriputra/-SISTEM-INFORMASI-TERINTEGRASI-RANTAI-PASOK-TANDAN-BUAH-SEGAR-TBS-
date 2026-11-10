"""Strict Pydantic schemas aligned 1:1 with OpenAPI Public Portal contracts."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from app.core.logging import format_utc_iso
from app.core.schemas import (
    PaginationMeta,
    SimpleSuccessMeta,
    StrictContractModel,
    format_decimal,
)
from app.modules.pricing.presentation.schemas import PublicDisbunPriceDto
from app.modules.public_portal.domain.entities import (
    PublicDisbunPriceItem,
    PublicMillDetailData,
    PublicMillItem,
    PublicNoticeItem,
    PublicPriceDetailData,
    PublicPriceQuoteItem,
    PublicProfileData,
)


class PublicPriceQuoteDto(StrictContractModel):
    id: UUID
    mill_id: UUID
    mill_name: str
    mill_code: str
    regency: str
    price_category_code: str
    price_category_name: str
    unit: str
    source_name: str
    source_type: Literal["MILL_OFFICIAL", "MILL_DOCUMENT", "VERIFIED_MANUAL"]
    price_per_kg: str
    effective_from: str
    effective_until: str | None
    status: Literal["PUBLISHED"] = "PUBLISHED"
    display_status: Literal["PUBLISHED", "EXPIRED"]
    is_expired: bool
    updated_at: str
    published_at: str
    is_simulation: bool


class PublicHistoricalTrendPointDto(StrictContractModel):
    id: UUID
    price_per_kg: str
    effective_from: str
    effective_until: str | None
    published_at: str


class PublicPriceDetailDto(StrictContractModel):
    quote: PublicPriceQuoteDto
    historical_trend: list[PublicHistoricalTrendPointDto]


class PublicPriceListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[PublicPriceQuoteDto]
    meta: PaginationMeta
    request_id: str


class PublicPriceDetailEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: PublicPriceDetailDto
    meta: SimpleSuccessMeta
    request_id: str


class PublicDisbunPriceListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[PublicDisbunPriceDto]
    meta: PaginationMeta
    request_id: str


class PublicMillSummaryDto(StrictContractModel):
    id: UUID
    mill_code: str
    mill_name: str
    company_name: str
    address: str
    district: str
    regency: str
    province: str
    latitude: str | None
    longitude: str | None
    has_verified_coordinates: bool
    public_contact_phone: str | None
    active_public_price_per_kg: str | None
    active_price_category: str | None
    active_price_updated_at: str | None


class PublicMillListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[PublicMillSummaryDto]
    meta: PaginationMeta
    request_id: str


class PublicMillDetailDto(StrictContractModel):
    mill: PublicMillSummaryDto
    latest_prices: list[PublicPriceQuoteDto]
    privacy_notice: str


class PublicMillDetailEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: PublicMillDetailDto
    meta: SimpleSuccessMeta
    request_id: str


class PublicOfficeDto(StrictContractModel):
    id: UUID
    office_name: str
    address: str
    latitude: str | None
    longitude: str | None
    public_contact: str | None


class PublicProfileDto(StrictContractModel):
    organization_name: str
    business_unit_name: str
    excluded_units_notice: str
    about_title: str
    about_summary: str
    partnership_title: str
    partnership_summary: str
    partnership_requirements: list[str]
    offices: list[PublicOfficeDto]


class PublicProfileEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: PublicProfileDto
    meta: SimpleSuccessMeta
    request_id: str


class PublicNoticeDto(StrictContractModel):
    id: UUID
    title: str
    body: str
    start_at: str
    end_at: str | None


class PublicNoticeListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[PublicNoticeDto]
    meta: PaginationMeta
    request_id: str


def to_public_price_dto(e: PublicPriceQuoteItem) -> PublicPriceQuoteDto:
    src: Literal["MILL_OFFICIAL", "MILL_DOCUMENT", "VERIFIED_MANUAL"] = (
        e.source_type
        if e.source_type in ("MILL_OFFICIAL", "MILL_DOCUMENT", "VERIFIED_MANUAL")
        else "MILL_OFFICIAL"
    )  # type: ignore[assignment]
    return PublicPriceQuoteDto(
        id=e.id,
        mill_id=e.mill_id,
        mill_name=e.mill_name,
        mill_code=e.mill_code,
        regency=e.regency,
        price_category_code=e.price_category_code,
        price_category_name=e.price_category_name,
        unit=e.unit,
        source_name=e.source_name,
        source_type=src,
        price_per_kg=format_decimal(e.price_per_kg, 2) or "0.00",
        effective_from=format_utc_iso(e.effective_from) or "",
        effective_until=format_utc_iso(e.effective_until),
        status="PUBLISHED",
        display_status="EXPIRED" if e.is_expired else "PUBLISHED",
        is_expired=e.is_expired,
        updated_at=format_utc_iso(e.updated_at) or "",
        published_at=format_utc_iso(e.published_at) or "",
        is_simulation=e.is_simulation,
    )


def to_public_price_detail_dto(d: PublicPriceDetailData) -> PublicPriceDetailDto:
    return PublicPriceDetailDto(
        quote=to_public_price_dto(d.quote),
        historical_trend=[
            PublicHistoricalTrendPointDto(
                id=h.id,
                price_per_kg=format_decimal(h.price_per_kg, 2) or "0.00",
                effective_from=format_utc_iso(h.effective_from) or "",
                effective_until=format_utc_iso(h.effective_until),
                published_at=format_utc_iso(h.published_at) or "",
            )
            for h in d.historical_trend
        ],
    )


def to_public_disbun_dto(d: PublicDisbunPriceItem) -> PublicDisbunPriceDto:
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


def to_public_mill_dto(m: PublicMillItem) -> PublicMillSummaryDto:
    return PublicMillSummaryDto(
        id=m.id,
        mill_code=m.mill_code,
        mill_name=m.mill_name,
        company_name=m.company_name,
        address=m.address,
        district=m.district,
        regency=m.regency,
        province=m.province,
        latitude=format_decimal(m.latitude, 6),
        longitude=format_decimal(m.longitude, 6),
        has_verified_coordinates=m.has_verified_coordinates,
        public_contact_phone=m.public_contact_phone,
        active_public_price_per_kg=format_decimal(m.active_public_price_per_kg, 2),
        active_price_category=m.active_price_category,
        active_price_updated_at=format_utc_iso(m.active_price_updated_at),
    )


def to_public_mill_detail_dto(d: PublicMillDetailData) -> PublicMillDetailDto:
    return PublicMillDetailDto(
        mill=to_public_mill_dto(d.mill),
        latest_prices=[to_public_price_dto(p) for p in d.latest_prices],
        privacy_notice=(
            "BR-PUB-003: Nomor kontrak, kuota pasokan, biaya logistik, "
            "dan data petani tidak dipublikasikan."
        ),
    )


def to_public_profile_dto(p: PublicProfileData) -> PublicProfileDto:
    return PublicProfileDto(
        organization_name=p.organization_name,
        business_unit_name=p.business_unit_name,
        excluded_units_notice=p.excluded_units_notice,
        about_title=p.about_title,
        about_summary=p.about_summary,
        partnership_title=p.partnership_title,
        partnership_summary=p.partnership_summary,
        partnership_requirements=list(p.partnership_requirements),
        offices=[
            PublicOfficeDto(
                id=o.id,
                office_name=o.office_name,
                address=o.address,
                latitude=format_decimal(o.latitude, 6),
                longitude=format_decimal(o.longitude, 6),
                public_contact=o.public_contact,
            )
            for o in p.offices
        ],
    )


def to_public_notice_dto(n: PublicNoticeItem) -> PublicNoticeDto:
    return PublicNoticeDto(
        id=n.id,
        title=n.title,
        body=n.body,
        start_at=format_utc_iso(n.start_at) or "",
        end_at=format_utc_iso(n.end_at),
    )
