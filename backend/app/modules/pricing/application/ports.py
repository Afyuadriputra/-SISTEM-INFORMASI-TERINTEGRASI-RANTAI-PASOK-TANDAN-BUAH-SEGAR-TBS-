"""Repository and public cache invalidation ports for Pricing (ADR-002)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from app.modules.pricing.domain.entities import (
    DisbunReferencePriceEntity,
    MillPriceQuoteEntity,
    PriceCategoryEntity,
    PriceQuoteStatus,
    PriceSourceEntity,
    VerifyDecision,
)


class PricingRepositoryPort(Protocol):
    """Async PostgreSQL repository port for price sources, categories, quotes, and Disbun."""

    async def list_reference_metadata(
        self,
    ) -> tuple[list[PriceSourceEntity], list[PriceCategoryEntity]]: ...

    async def get_quote_by_id(self, quote_id: UUID) -> MillPriceQuoteEntity | None: ...

    async def list_internal_quotes(
        self,
        *,
        allowed_statuses: tuple[PriceQuoteStatus, ...] | None,
        status_filter: PriceQuoteStatus | None,
        mill_id: UUID | None,
        page: int,
        page_size: int,
    ) -> tuple[list[MillPriceQuoteEntity], int]: ...

    async def create_draft(
        self,
        *,
        mill_id: UUID,
        price_category_id: UUID,
        source_id: UUID,
        price_per_kg: Decimal,
        effective_from: datetime,
        effective_until: datetime | None,
        source_document_id: UUID | None,
        notes: str | None,
        actor_id: UUID,
        now: datetime,
    ) -> MillPriceQuoteEntity: ...

    async def update_draft(
        self,
        *,
        quote_id: UUID,
        expected_version: int,
        price_per_kg: Decimal | None,
        effective_from: datetime | None,
        effective_until: datetime | None,
        update_effective_until: bool,
        source_document_id: UUID | None,
        update_source_doc: bool,
        notes: str | None,
        update_notes: bool,
        actor_id: UUID,
        now: datetime,
    ) -> MillPriceQuoteEntity: ...

    async def submit_for_verification(
        self, *, quote_id: UUID, actor_id: UUID, now: datetime
    ) -> MillPriceQuoteEntity: ...

    async def verify_or_reject(
        self,
        *,
        quote_id: UUID,
        decision: VerifyDecision,
        reason: str | None,
        actor_id: UUID,
        is_admin_forbidden: bool,
        now: datetime,
    ) -> MillPriceQuoteEntity: ...

    async def publish_quote(
        self, *, quote_id: UUID, actor_id: UUID, now: datetime
    ) -> MillPriceQuoteEntity: ...

    async def revoke_quote(
        self, *, quote_id: UUID, reason: str, actor_id: UUID, now: datetime
    ) -> MillPriceQuoteEntity: ...

    async def create_disbun_price(
        self,
        *,
        price_source_id: UUID,
        price_category_id: UUID,
        price_per_kg: Decimal,
        effective_from: datetime,
        effective_until: datetime | None,
        source_document_id: UUID | None,
        actor_id: UUID,
        now: datetime,
    ) -> DisbunReferencePriceEntity: ...


class PublicPricingCacheInvalidatorPort(Protocol):
    """Post-commit Redis cache invalidation for public price and mill directories."""

    async def invalidate_public_prices(self) -> None: ...

    async def invalidate_public_disbun(self) -> None: ...
