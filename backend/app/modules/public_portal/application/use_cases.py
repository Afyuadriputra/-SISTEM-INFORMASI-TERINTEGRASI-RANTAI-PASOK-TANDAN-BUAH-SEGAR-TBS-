"""Public Portal read use cases with Redis cache-aside and PostgreSQL fallback."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, date, datetime
from typing import Any, Literal
from uuid import UUID

from app.core.exceptions import AppError, ErrorCode
from app.modules.public_portal.application.ports import (
    PublicCachePort,
    PublicPortalRepositoryPort,
)
from app.modules.public_portal.domain.entities import (
    PublicDisbunPriceItem,
    PublicMillDetailData,
    PublicMillItem,
    PublicNoticeItem,
    PublicPriceDetailData,
    PublicPriceQuoteItem,
    PublicProfileData,
)


def _hash_query(parts: dict[str, Any]) -> str:
    serialized = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:24]


class PublicPortalService:
    """Serves unauthenticated curated portal endpoints with Redis caching & safe fallback."""

    def __init__(
        self,
        *,
        repo: PublicPortalRepositoryPort,
        cache: PublicCachePort,
    ) -> None:
        self._repo = repo
        self._cache = cache

    @staticmethod
    def price_list_cache_key(
        *,
        page: int,
        page_size: int,
        query: str | None,
        regency: str | None,
        category_code: str | None,
        effective_date: date | None,
        include_expired: bool,
        sort_by: str,
        sort_dir: str,
    ) -> str:
        digest = _hash_query(
            {
                "p": page,
                "ps": page_size,
                "q": query,
                "r": regency,
                "c": category_code,
                "d": effective_date,
                "ie": include_expired,
                "sb": sort_by,
                "sd": sort_dir,
            }
        )
        return f"public:prices:v1:list:{digest}"

    @staticmethod
    def mill_list_cache_key(
        *,
        page: int,
        page_size: int,
        query: str | None,
        regency: str | None,
        district: str | None,
    ) -> str:
        digest = _hash_query({"p": page, "ps": page_size, "q": query, "r": regency, "d": district})
        return f"public:mills:v1:list:{digest}"

    async def get_cached_payload(self, key: str) -> str | None:
        return await self._cache.get_json(key)

    async def set_cached_payload(self, key: str, raw_json: str, ttl_seconds: int) -> None:
        await self._cache.set_json(key, raw_json, ttl_seconds)

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
    ) -> tuple[list[PublicPriceQuoteItem], int]:
        return await self._repo.list_public_prices(
            page=page,
            page_size=page_size,
            query=query,
            regency=regency,
            category_code=category_code,
            effective_date=effective_date,
            include_expired=include_expired,
            sort_by=sort_by,
            sort_dir=sort_dir,
            now=datetime.now(UTC),
        )

    async def get_public_price_detail(self, price_quote_id: UUID) -> PublicPriceDetailData:
        detail = await self._repo.get_public_price_detail(
            price_quote_id=price_quote_id, now=datetime.now(UTC)
        )
        if detail is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        return detail

    async def list_public_disbun_prices(
        self, *, page: int, page_size: int
    ) -> tuple[list[PublicDisbunPriceItem], int]:
        return await self._repo.list_public_disbun_prices(page=page, page_size=page_size)

    async def list_public_mills(
        self,
        *,
        page: int,
        page_size: int,
        query: str | None,
        regency: str | None,
        district: str | None,
    ) -> tuple[list[PublicMillItem], int]:
        return await self._repo.list_public_mills(
            page=page,
            page_size=page_size,
            query=query,
            regency=regency,
            district=district,
            now=datetime.now(UTC),
        )

    async def get_public_mill_detail(self, mill_id: UUID) -> PublicMillDetailData:
        detail = await self._repo.get_public_mill_detail(mill_id=mill_id, now=datetime.now(UTC))
        if detail is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        return detail

    async def get_public_profile(self) -> PublicProfileData:
        return await self._repo.get_public_profile()

    async def list_public_notices(
        self, *, page: int, page_size: int
    ) -> tuple[list[PublicNoticeItem], int]:
        return await self._repo.list_public_notices(
            page=page, page_size=page_size, now=datetime.now(UTC)
        )
