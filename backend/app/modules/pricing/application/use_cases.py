"""Use cases orchestrating multi-mill TBS pricing workflow SM-01, SOD-01, and cache safety."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.core.exceptions import AppError, ErrorCode
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.domain.rules import is_non_approver_admin
from app.modules.pricing.application.ports import (
    PricingRepositoryPort,
    PublicPricingCacheInvalidatorPort,
)
from app.modules.pricing.domain.entities import (
    DisbunReferencePriceEntity,
    MillPriceQuoteEntity,
    PriceCategoryEntity,
    PriceQuoteStatus,
    PriceSourceEntity,
    VerifyDecision,
)
from app.modules.pricing.domain.rules import (
    parse_positive_price_per_kg,
    validate_price_period,
)

_LIMITED_ROLE_READ_STATUSES = (PriceQuoteStatus.VERIFIED, PriceQuoteStatus.PUBLISHED)


def _is_limited_price_viewer(principal: AuthenticatedPrincipal) -> bool:
    return any(
        r in (RoleCode.FARMER, RoleCode.COOPERATIVE_OPERATOR) for r in principal.roles
    ) and not any(
        r in (RoleCode.PERUMDA_OPERATIONS, RoleCode.PERUMDA_FINANCE, RoleCode.DIRECTOR)
        for r in principal.roles
    )


class PricingService:
    """Internal TBS pricing management and Disbun reference administration."""

    def __init__(
        self,
        *,
        repo: PricingRepositoryPort,
        cache_invalidator: PublicPricingCacheInvalidatorPort,
    ) -> None:
        self._repo = repo
        self._cache = cache_invalidator

    async def get_reference_metadata(
        self,
    ) -> tuple[list[PriceSourceEntity], list[PriceCategoryEntity]]:
        return await self._repo.list_reference_metadata()

    async def list_internal_prices(
        self,
        *,
        principal: AuthenticatedPrincipal,
        status: PriceQuoteStatus | None,
        mill_id: UUID | None,
        page: int,
        page_size: int,
    ) -> tuple[list[MillPriceQuoteEntity], int]:
        allowed_statuses: tuple[PriceQuoteStatus, ...] | None = None
        if _is_limited_price_viewer(principal):
            if status is not None and status not in _LIMITED_ROLE_READ_STATUSES:
                raise AppError(
                    ErrorCode.AUTH_ACCESS_DENIED,
                    "Peran Anda hanya dapat melihat harga berstatus VERIFIED atau PUBLISHED.",
                )
            allowed_statuses = _LIMITED_ROLE_READ_STATUSES
        return await self._repo.list_internal_quotes(
            allowed_statuses=allowed_statuses,
            status_filter=status,
            mill_id=mill_id,
            page=page,
            page_size=page_size,
        )

    async def get_internal_price(
        self, *, principal: AuthenticatedPrincipal, price_quote_id: UUID
    ) -> MillPriceQuoteEntity:
        quote = await self._repo.get_quote_by_id(price_quote_id)
        if quote is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        if _is_limited_price_viewer(principal) and quote.status not in _LIMITED_ROLE_READ_STATUSES:
            raise AppError(ErrorCode.AUTH_ACCESS_DENIED)
        return quote

    async def create_price_draft(
        self,
        *,
        principal: AuthenticatedPrincipal,
        mill_id: UUID,
        price_category_id: UUID,
        source_id: UUID,
        price_per_kg_raw: str,
        effective_from: datetime,
        effective_until: datetime | None,
        source_document_id: UUID | None,
        notes: str | None,
    ) -> MillPriceQuoteEntity:
        price = parse_positive_price_per_kg(price_per_kg_raw)
        validate_price_period(effective_from, effective_until)
        return await self._repo.create_draft(
            mill_id=mill_id,
            price_category_id=price_category_id,
            source_id=source_id,
            price_per_kg=price,
            effective_from=effective_from,
            effective_until=effective_until,
            source_document_id=source_document_id,
            notes=notes.strip() if notes else None,
            actor_id=principal.user_id,
            now=datetime.now(UTC),
        )

    async def update_price_draft(
        self,
        *,
        principal: AuthenticatedPrincipal,
        price_quote_id: UUID,
        expected_version: int,
        price_per_kg_raw: str | None,
        effective_from: datetime | None,
        effective_until: datetime | None,
        update_effective_until: bool,
        source_document_id: UUID | None,
        update_source_doc: bool,
        notes: str | None,
        update_notes: bool,
    ) -> MillPriceQuoteEntity:
        price = (
            parse_positive_price_per_kg(price_per_kg_raw) if price_per_kg_raw is not None else None
        )
        if effective_from is not None and update_effective_until:
            validate_price_period(effective_from, effective_until)
        return await self._repo.update_draft(
            quote_id=price_quote_id,
            expected_version=expected_version,
            price_per_kg=price,
            effective_from=effective_from,
            effective_until=effective_until,
            update_effective_until=update_effective_until,
            source_document_id=source_document_id,
            update_source_doc=update_source_doc,
            notes=notes.strip() if notes else None,
            update_notes=update_notes,
            actor_id=principal.user_id,
            now=datetime.now(UTC),
        )

    async def submit_price(
        self, *, principal: AuthenticatedPrincipal, price_quote_id: UUID
    ) -> MillPriceQuoteEntity:
        return await self._repo.submit_for_verification(
            quote_id=price_quote_id,
            actor_id=principal.user_id,
            now=datetime.now(UTC),
        )

    async def verify_or_reject_price(
        self,
        *,
        principal: AuthenticatedPrincipal,
        price_quote_id: UUID,
        decision: VerifyDecision,
        reason: str | None,
    ) -> MillPriceQuoteEntity:
        if is_non_approver_admin(principal.roles):
            raise AppError(ErrorCode.AUTH_OPERATION_FORBIDDEN)
        clean_reason = reason.strip() if reason else None
        if decision == VerifyDecision.REJECT and not clean_reason:
            raise AppError(
                ErrorCode.VAL_REQUIRED_FIELD,
                "Alasan penolakan wajib diisi ketika menolak pengajuan harga.",
                details=[
                    {
                        "field": "reason",
                        "reason": "Alasan penolakan wajib diisi.",
                        "code": ErrorCode.VAL_REQUIRED_FIELD.value,
                    }
                ],
            )
        return await self._repo.verify_or_reject(
            quote_id=price_quote_id,
            decision=decision,
            reason=clean_reason,
            actor_id=principal.user_id,
            is_admin_forbidden=is_non_approver_admin(principal.roles),
            now=datetime.now(UTC),
        )

    async def publish_price(
        self, *, principal: AuthenticatedPrincipal, price_quote_id: UUID
    ) -> MillPriceQuoteEntity:
        published = await self._repo.publish_quote(
            quote_id=price_quote_id,
            actor_id=principal.user_id,
            now=datetime.now(UTC),
        )
        await self._cache.invalidate_public_prices()
        return published

    async def revoke_price(
        self, *, principal: AuthenticatedPrincipal, price_quote_id: UUID, reason: str
    ) -> MillPriceQuoteEntity:
        clean_reason = reason.strip()
        if len(clean_reason) < 5:
            raise AppError(ErrorCode.VAL_REQUIRED_FIELD, "Alasan pencabutan wajib minimal 5 huruf.")
        revoked = await self._repo.revoke_quote(
            quote_id=price_quote_id,
            reason=clean_reason,
            actor_id=principal.user_id,
            now=datetime.now(UTC),
        )
        await self._cache.invalidate_public_prices()
        return revoked

    async def create_disbun_price(
        self,
        *,
        principal: AuthenticatedPrincipal,
        price_source_id: UUID,
        price_category_id: UUID,
        price_per_kg_raw: str,
        effective_from: datetime,
        effective_until: datetime | None,
        source_document_id: UUID | None,
    ) -> DisbunReferencePriceEntity:
        price = parse_positive_price_per_kg(price_per_kg_raw)
        validate_price_period(effective_from, effective_until)
        created = await self._repo.create_disbun_price(
            price_source_id=price_source_id,
            price_category_id=price_category_id,
            price_per_kg=price,
            effective_from=effective_from,
            effective_until=effective_until,
            source_document_id=source_document_id,
            actor_id=principal.user_id,
            now=datetime.now(UTC),
        )
        await self._cache.invalidate_public_disbun()
        return created
