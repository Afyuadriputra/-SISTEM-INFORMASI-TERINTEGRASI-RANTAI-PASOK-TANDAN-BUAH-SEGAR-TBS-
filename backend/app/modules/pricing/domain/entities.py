"""Pure domain entities for Pricing (DBD §8)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


class PriceSourceType(StrEnum):
    DISBUN = "DISBUN"
    MILL_OFFICIAL = "MILL_OFFICIAL"
    MILL_DOCUMENT = "MILL_DOCUMENT"
    VERIFIED_MANUAL = "VERIFIED_MANUAL"


class PriceQuoteStatus(StrEnum):
    DRAFT = "DRAFT"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"
    REVOKED = "REVOKED"


class PriceDisplayStatus(StrEnum):
    DRAFT = "DRAFT"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class VerifyDecision(StrEnum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"


@dataclass(frozen=True, slots=True)
class PriceSourceEntity:
    id: UUID
    source_code: str
    source_name: str
    source_type: PriceSourceType
    status: str


@dataclass(frozen=True, slots=True)
class PriceCategoryEntity:
    id: UUID
    category_code: str
    name: str
    unit: str
    quality_basis: str
    age_group: str | None
    is_active: bool


@dataclass(frozen=True, slots=True)
class PriceVerificationEventEntity:
    id: UUID
    action: str
    previous_status: PriceQuoteStatus
    new_status: PriceQuoteStatus
    actor_id: UUID
    reason: str | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class MillPriceQuoteEntity:
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
    source_type: PriceSourceType
    price_per_kg: Decimal
    effective_from: datetime
    effective_until: datetime | None
    status: PriceQuoteStatus
    submitted_by: UUID
    verified_by: UUID | None
    verified_at: datetime | None
    published_at: datetime | None
    source_document_id: UUID | None
    notes: str | None
    is_simulation: bool
    version: int
    created_at: datetime
    updated_at: datetime
    verification_events: tuple[PriceVerificationEventEntity, ...] = ()

    def is_expired_at(self, moment: datetime) -> bool:
        return (
            self.status == PriceQuoteStatus.PUBLISHED
            and self.effective_until is not None
            and self.effective_until < moment
        )

    def display_status_at(self, moment: datetime) -> PriceDisplayStatus:
        if self.is_expired_at(moment):
            return PriceDisplayStatus.EXPIRED
        return PriceDisplayStatus(self.status.value)


@dataclass(frozen=True, slots=True)
class DisbunReferencePriceEntity:
    id: UUID
    price_source_id: UUID
    source_name: str
    price_category_id: UUID
    category_code: str
    category_name: str
    age_group: str | None
    price_per_kg: Decimal
    effective_from: datetime
    effective_until: datetime | None
    verification_status: str
    created_at: datetime
