"""Unauthenticated Public Portal endpoints with Redis cache-aside & PostgreSQL fallback."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from datetime import date
from typing import Annotated, Literal, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from app.core.logging import request_id_ctx, utc_now_iso
from app.core.schemas import SimpleSuccessMeta, StrictContractModel, build_pagination_meta
from app.modules.public_portal.application.use_cases import PublicPortalService
from app.modules.public_portal.presentation.schemas import (
    PublicDisbunPriceListEnvelope,
    PublicMillDetailEnvelope,
    PublicMillListEnvelope,
    PublicNoticeListEnvelope,
    PublicPriceDetailEnvelope,
    PublicPriceListEnvelope,
    PublicProfileEnvelope,
    to_public_disbun_dto,
    to_public_mill_detail_dto,
    to_public_mill_dto,
    to_public_notice_dto,
    to_public_price_detail_dto,
    to_public_price_dto,
    to_public_profile_dto,
)

public_portal_router = APIRouter(prefix="/api/v1/public", tags=["Public Portal"])


def get_public_portal_service(request: Request) -> PublicPortalService:
    """Resolve PublicPortalService wired in composition root."""
    return cast(PublicPortalService, request.app.state.public_portal_service)


type PublicPortalServiceDep = Annotated[PublicPortalService, Depends(get_public_portal_service)]


async def _cached_json_or_build[TEnvelope: StrictContractModel](
    service: PublicPortalService,
    *,
    cache_key: str,
    ttl_seconds: int,
    builder: Callable[[], Awaitable[TEnvelope]],
) -> JSONResponse | TEnvelope:
    """Serve versioned JSON from Redis cleanly while swapping live request_id."""
    cached = await service.get_cached_payload(cache_key)
    if cached is not None:
        payload = json.loads(cached)
        payload["request_id"] = request_id_ctx.get()
        return JSONResponse(status_code=200, content=payload)
    envelope = await builder()
    dumped = envelope.model_dump(mode="json")
    await service.set_cached_payload(cache_key, json.dumps(dumped), ttl_seconds)
    return envelope


@public_portal_router.get("/prices", response_model=PublicPriceListEnvelope)
async def list_public_prices(
    service: PublicPortalServiceDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None, max_length=120),
    regency: str | None = Query(default=None, max_length=100),
    category_code: str | None = Query(default=None, max_length=50),
    effective_date: date | None = Query(default=None),
    include_expired: bool = Query(default=False),
    sort_by: Literal["price_per_kg", "mill_name", "updated_at"] = Query(default="price_per_kg"),
    sort_dir: Literal["asc", "desc"] = Query(default="desc"),
):
    key = service.price_list_cache_key(
        page=page,
        page_size=page_size,
        query=q,
        regency=regency,
        category_code=category_code,
        effective_date=effective_date,
        include_expired=include_expired,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )

    async def _build() -> PublicPriceListEnvelope:
        rows, total = await service.list_public_prices(
            page=page,
            page_size=page_size,
            query=q,
            regency=regency,
            category_code=category_code,
            effective_date=effective_date,
            include_expired=include_expired,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        notice = (
            "Informasi harga terbaru belum tersedia untuk kriteria pilihan."
            if total == 0
            else "Data Simulasi — Bukan tarif komersial resmi Perumda."
        )
        return PublicPriceListEnvelope(
            data=[to_public_price_dto(r) for r in rows],
            meta=build_pagination_meta(
                page,
                page_size,
                total,
                data_freshness_at=utc_now_iso(),
                simulation_notice=notice,
            ),
            request_id=request_id_ctx.get(),
        )

    return await _cached_json_or_build(service, cache_key=key, ttl_seconds=60, builder=_build)


@public_portal_router.get("/prices/{price_quote_id}", response_model=PublicPriceDetailEnvelope)
async def get_public_price_detail(
    price_quote_id: UUID,
    service: PublicPortalServiceDep,
):
    key = f"public:prices:v1:detail:{price_quote_id}"

    async def _build() -> PublicPriceDetailEnvelope:
        detail = await service.get_public_price_detail(price_quote_id)
        return PublicPriceDetailEnvelope(
            data=to_public_price_detail_dto(detail),
            meta=SimpleSuccessMeta(
                data_freshness_at=utc_now_iso(),
                simulation_notice="Data Simulasi — Riwayat kategori setara.",
            ),
            request_id=request_id_ctx.get(),
        )

    return await _cached_json_or_build(service, cache_key=key, ttl_seconds=60, builder=_build)


@public_portal_router.get("/disbun-prices", response_model=PublicDisbunPriceListEnvelope)
async def list_public_disbun_prices(
    service: PublicPortalServiceDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    key = f"public:disbun:v1:list:{page}:{page_size}"

    async def _build() -> PublicDisbunPriceListEnvelope:
        rows, total = await service.list_public_disbun_prices(page=page, page_size=page_size)
        return PublicDisbunPriceListEnvelope(
            data=[to_public_disbun_dto(r) for r in rows],
            meta=build_pagination_meta(page, page_size, total, data_freshness_at=utc_now_iso()),
            request_id=request_id_ctx.get(),
        )

    return await _cached_json_or_build(service, cache_key=key, ttl_seconds=120, builder=_build)


@public_portal_router.get("/mills", response_model=PublicMillListEnvelope)
async def list_public_mills(
    service: PublicPortalServiceDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None, max_length=120),
    regency: str | None = Query(default=None, max_length=100),
    district: str | None = Query(default=None, max_length=100),
):
    key = service.mill_list_cache_key(
        page=page, page_size=page_size, query=q, regency=regency, district=district
    )

    async def _build() -> PublicMillListEnvelope:
        rows, total = await service.list_public_mills(
            page=page, page_size=page_size, query=q, regency=regency, district=district
        )
        return PublicMillListEnvelope(
            data=[to_public_mill_dto(r) for r in rows],
            meta=build_pagination_meta(page, page_size, total, data_freshness_at=utc_now_iso()),
            request_id=request_id_ctx.get(),
        )

    return await _cached_json_or_build(service, cache_key=key, ttl_seconds=120, builder=_build)


@public_portal_router.get("/mills/{mill_id}", response_model=PublicMillDetailEnvelope)
async def get_public_mill_detail(
    mill_id: UUID,
    service: PublicPortalServiceDep,
):
    key = f"public:mills:v1:detail:{mill_id}"

    async def _build() -> PublicMillDetailEnvelope:
        detail = await service.get_public_mill_detail(mill_id)
        return PublicMillDetailEnvelope(
            data=to_public_mill_detail_dto(detail),
            meta=SimpleSuccessMeta(data_freshness_at=utc_now_iso()),
            request_id=request_id_ctx.get(),
        )

    return await _cached_json_or_build(service, cache_key=key, ttl_seconds=120, builder=_build)


@public_portal_router.get("/profile", response_model=PublicProfileEnvelope)
async def get_public_profile(service: PublicPortalServiceDep):
    async def _build() -> PublicProfileEnvelope:
        profile = await service.get_public_profile()
        return PublicProfileEnvelope(
            data=to_public_profile_dto(profile),
            meta=SimpleSuccessMeta(data_freshness_at=utc_now_iso()),
            request_id=request_id_ctx.get(),
        )

    return await _cached_json_or_build(
        service, cache_key="public:profile:v1", ttl_seconds=300, builder=_build
    )


@public_portal_router.get("/notices", response_model=PublicNoticeListEnvelope)
async def list_public_notices(
    service: PublicPortalServiceDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    key = f"public:notices:v1:list:{page}:{page_size}"

    async def _build() -> PublicNoticeListEnvelope:
        rows, total = await service.list_public_notices(page=page, page_size=page_size)
        return PublicNoticeListEnvelope(
            data=[to_public_notice_dto(r) for r in rows],
            meta=build_pagination_meta(page, page_size, total, data_freshness_at=utc_now_iso()),
            request_id=request_id_ctx.get(),
        )

    return await _cached_json_or_build(service, cache_key=key, ttl_seconds=120, builder=_build)
