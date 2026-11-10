"""Pure domain projections and HTML sanitization helpers for Portal Publik (BR-PUB-001..005)."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def sanitize_public_text(raw: str) -> str:
    """Strip unsafe markup and unescape/normalize cleanly before public API serialization."""
    no_scripts = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", raw)
    stripped = _HTML_TAG_RE.sub("", no_scripts)
    return html.unescape(stripped).strip()


@dataclass(frozen=True, slots=True)
class PublicPriceQuoteItem:
    id: UUID
    mill_id: UUID
    mill_name: str
    mill_code: str
    regency: str
    price_category_code: str
    price_category_name: str
    unit: str
    source_name: str
    source_type: str
    price_per_kg: Decimal
    effective_from: datetime
    effective_until: datetime | None
    is_expired: bool
    updated_at: datetime
    published_at: datetime
    is_simulation: bool


@dataclass(frozen=True, slots=True)
class PublicHistoricalPricePoint:
    id: UUID
    price_per_kg: Decimal
    effective_from: datetime
    effective_until: datetime | None
    published_at: datetime


@dataclass(frozen=True, slots=True)
class PublicPriceDetailData:
    quote: PublicPriceQuoteItem
    historical_trend: tuple[PublicHistoricalPricePoint, ...]


@dataclass(frozen=True, slots=True)
class PublicDisbunPriceItem:
    id: UUID
    source_name: str
    category_code: str
    category_name: str
    age_group: str | None
    price_per_kg: Decimal
    effective_from: datetime
    effective_until: datetime | None
    verification_status: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class PublicMillItem:
    id: UUID
    mill_code: str
    mill_name: str
    company_name: str
    address: str
    district: str
    regency: str
    province: str
    latitude: Decimal | None
    longitude: Decimal | None
    has_verified_coordinates: bool
    public_contact_phone: str | None
    active_public_price_per_kg: Decimal | None
    active_price_category: str | None
    active_price_updated_at: datetime | None


@dataclass(frozen=True, slots=True)
class PublicMillDetailData:
    mill: PublicMillItem
    latest_prices: tuple[PublicPriceQuoteItem, ...]


@dataclass(frozen=True, slots=True)
class PublicOfficeItem:
    id: UUID
    office_name: str
    address: str
    latitude: Decimal | None
    longitude: Decimal | None
    public_contact: str | None


@dataclass(frozen=True, slots=True)
class PublicProfileData:
    organization_name: str
    business_unit_name: str
    excluded_units_notice: str
    about_title: str
    about_summary: str
    partnership_title: str
    partnership_summary: str
    partnership_requirements: tuple[str, ...]
    offices: tuple[PublicOfficeItem, ...]


@dataclass(frozen=True, slots=True)
class PublicNoticeItem:
    id: UUID
    title: str
    body: str
    start_at: datetime
    end_at: datetime | None
