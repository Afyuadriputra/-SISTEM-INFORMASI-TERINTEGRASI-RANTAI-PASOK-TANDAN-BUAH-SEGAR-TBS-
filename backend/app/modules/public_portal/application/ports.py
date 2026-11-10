"""Repository and graceful Redis cache ports for Portal Publik."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Protocol
from uuid import UUID

from app.modules.public_portal.domain.entities import (
    PublicDisbunPriceItem,
    PublicMillDetailData,
    PublicMillItem,
    PublicNoticeItem,
    PublicPriceDetailData,
    PublicPriceQuoteItem,
    PublicProfileData,
)


class PublicPortalRepositoryPort(Protocol):
    """Curated read-only public query contract exposing strictly verified public entities."""

    async def list_public_prices(
        self,
        *,
        page: int,
        page_size: int,
        query: str | None,
        regency: str | None,
        category_code: str | None,
        effective_date: date | None,
        include_expired: bool,
        sort_by: Literal["price_per_kg", "mill_name", "updated_at"],
        sort_dir: Literal["asc", "desc"],
        now: datetime,
    ) -> tuple[list[PublicPriceQuoteItem], int]: ...

    async def get_public_price_detail(
        self, *, price_quote_id: UUID, now: datetime
    ) -> PublicPriceDetailData | None: ...

    async def list_public_disbun_prices(
        self, *, page: int, page_size: int
    ) -> tuple[list[PublicDisbunPriceItem], int]: ...

    async def list_public_mills(
        self,
        *,
        page: int,
        page_size: int,
        query: str | None,
        regency: str | None,
        district: str | None,
        now: datetime,
    ) -> tuple[list[PublicMillItem], int]: ...

    async def get_public_mill_detail(
        self, *, mill_id: UUID, now: datetime
    ) -> PublicMillDetailData | None: ...

    async def get_public_profile(self) -> PublicProfileData: ...

    async def list_public_notices(
        self, *, page: int, page_size: int, now: datetime
    ) -> tuple[list[PublicNoticeItem], int]: ...


class PublicCachePort(Protocol):
    """Non-critical Redis JSON cache contract allowing graceful fallback on Redis errors."""

    async def get_json(self, key: str) -> str | None: ...

    async def set_json(self, key: str, value: str, ttl_seconds: int) -> None: ...
