"""Curated PostgreSQL read queries for Public Portal respecting BR-PUB-001..005."""

from __future__ import annotations

from datetime import UTC, date, datetime, time
from typing import Any, Literal
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import joinedload

from app.modules.master_data.infrastructure.models import MillModel, PerumdaOfficeModel
from app.modules.pricing.domain.entities import PriceQuoteStatus
from app.modules.pricing.infrastructure.models import (
    DisbunReferencePriceModel,
    MillPriceQuoteModel,
    PriceCategoryModel,
    PriceSourceModel,
)
from app.modules.public_portal.domain.entities import (
    PublicDisbunPriceItem,
    PublicHistoricalPricePoint,
    PublicMillDetailData,
    PublicMillItem,
    PublicNoticeItem,
    PublicOfficeItem,
    PublicPriceDetailData,
    PublicPriceQuoteItem,
    PublicProfileData,
    sanitize_public_text,
)
from app.modules.public_portal.infrastructure.models import PublicNoticeModel, PublicPageModel


def _to_public_quote(row: MillPriceQuoteModel, *, now: datetime) -> PublicPriceQuoteItem:
    is_expired = row.effective_until is not None and row.effective_until < now
    return PublicPriceQuoteItem(
        id=row.id,
        mill_id=row.mill_id,
        mill_name=row.mill.mill_name,
        mill_code=row.mill.mill_code,
        regency=row.mill.regency,
        price_category_code=row.category.category_code,
        price_category_name=row.category.name,
        unit=row.category.unit,
        source_name=row.source.source_name,
        source_type=row.source.source_type,
        price_per_kg=row.price_per_kg,
        effective_from=row.effective_from,
        effective_until=row.effective_until,
        is_expired=is_expired,
        updated_at=row.updated_at,
        published_at=row.published_at or row.updated_at,
        is_simulation=row.is_simulation,
    )


def _to_public_mill(
    row: MillModel,
    latest_quote: MillPriceQuoteModel | None,
) -> PublicMillItem:
    verified = (
        row.location_verified_at is not None
        and row.latitude is not None
        and row.longitude is not None
    )
    return PublicMillItem(
        id=row.id,
        mill_code=row.mill_code,
        mill_name=row.mill_name,
        company_name=row.mill_company.company_name,
        address=row.address,
        district=row.district,
        regency=row.regency,
        province=row.province,
        latitude=row.latitude if verified else None,
        longitude=row.longitude if verified else None,
        has_verified_coordinates=verified,
        public_contact_phone=row.contact_phone if row.is_public else None,
        active_public_price_per_kg=latest_quote.price_per_kg if latest_quote else None,
        active_price_category=latest_quote.category.category_code if latest_quote else None,
        active_price_updated_at=latest_quote.updated_at if latest_quote else None,
    )


class SqlAlchemyPublicPortalRepository:
    """Strictly curated PostgreSQL read adapter for unauthenticated public endpoints."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

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
    ) -> tuple[list[PublicPriceQuoteItem], int]:
        async with self._sf() as session:
            filters: list[Any] = [
                MillPriceQuoteModel.status == PriceQuoteStatus.PUBLISHED.value,
                MillModel.is_public.is_(True),
                MillModel.partnership_status == "ACTIVE",
                PriceSourceModel.source_type != "DISBUN",
            ]
            if not include_expired:
                filters.append(
                    or_(
                        MillPriceQuoteModel.effective_until.is_(None),
                        MillPriceQuoteModel.effective_until >= now,
                    )
                )
            if query and query.strip():
                pat = f"%{query.strip()}%"
                filters.append(
                    or_(
                        MillModel.mill_name.ilike(pat),
                        MillModel.mill_code.ilike(pat),
                        MillModel.regency.ilike(pat),
                    )
                )
            if regency and regency.strip():
                filters.append(MillModel.regency.ilike(regency.strip()))
            if category_code and category_code.strip():
                filters.append(PriceCategoryModel.category_code == category_code.strip())
            if effective_date is not None:
                day_start = datetime.combine(effective_date, time.min, tzinfo=UTC)
                day_end = datetime.combine(effective_date, time.max, tzinfo=UTC)
                filters.append(MillPriceQuoteModel.effective_from <= day_end)
                filters.append(
                    or_(
                        MillPriceQuoteModel.effective_until.is_(None),
                        MillPriceQuoteModel.effective_until >= day_start,
                    )
                )

            base_from = (
                select(MillPriceQuoteModel)
                .join(MillPriceQuoteModel.mill)
                .join(MillPriceQuoteModel.category)
                .join(MillPriceQuoteModel.source)
                .where(*filters)
            )
            total = int(
                (
                    await session.execute(select(func.count()).select_from(base_from.subquery()))
                ).scalar_one()
            )

            sort_col_map: dict[str, Any] = {
                "price_per_kg": MillPriceQuoteModel.price_per_kg,
                "mill_name": MillModel.mill_name,
                "updated_at": MillPriceQuoteModel.updated_at,
            }
            sort_col = sort_col_map[sort_by]
            order_expr = sort_col.desc() if sort_dir == "desc" else sort_col.asc()

            stmt = (
                base_from.options(
                    joinedload(MillPriceQuoteModel.mill),
                    joinedload(MillPriceQuoteModel.category),
                    joinedload(MillPriceQuoteModel.source),
                )
                .order_by(order_expr, MillPriceQuoteModel.id.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return [_to_public_quote(r, now=now) for r in rows], total

    async def get_public_price_detail(
        self, *, price_quote_id: UUID, now: datetime
    ) -> PublicPriceDetailData | None:
        async with self._sf() as session:
            stmt = (
                select(MillPriceQuoteModel)
                .join(MillPriceQuoteModel.mill)
                .options(
                    joinedload(MillPriceQuoteModel.mill),
                    joinedload(MillPriceQuoteModel.category),
                    joinedload(MillPriceQuoteModel.source),
                )
                .where(
                    MillPriceQuoteModel.id == price_quote_id,
                    MillPriceQuoteModel.status == PriceQuoteStatus.PUBLISHED.value,
                    MillModel.is_public.is_(True),
                )
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            if row is None:
                return None

            hist_stmt = (
                select(MillPriceQuoteModel)
                .where(
                    MillPriceQuoteModel.mill_id == row.mill_id,
                    MillPriceQuoteModel.price_category_id == row.price_category_id,
                    MillPriceQuoteModel.status == PriceQuoteStatus.PUBLISHED.value,
                )
                .order_by(MillPriceQuoteModel.effective_from.desc())
                .limit(20)
            )
            hist_rows = (await session.execute(hist_stmt)).scalars().all()
            return PublicPriceDetailData(
                quote=_to_public_quote(row, now=now),
                historical_trend=tuple(
                    PublicHistoricalPricePoint(
                        id=h.id,
                        price_per_kg=h.price_per_kg,
                        effective_from=h.effective_from,
                        effective_until=h.effective_until,
                        published_at=h.published_at or h.updated_at,
                    )
                    for h in hist_rows
                ),
            )

    async def list_public_disbun_prices(
        self, *, page: int, page_size: int
    ) -> tuple[list[PublicDisbunPriceItem], int]:
        async with self._sf() as session:
            filters = [DisbunReferencePriceModel.verification_status.in_(("VERIFIED", "PUBLISHED"))]
            total = int(
                (
                    await session.execute(
                        select(func.count(DisbunReferencePriceModel.id)).where(*filters)
                    )
                ).scalar_one()
            )
            stmt = (
                select(DisbunReferencePriceModel)
                .options(
                    joinedload(DisbunReferencePriceModel.source),
                    joinedload(DisbunReferencePriceModel.category),
                )
                .where(*filters)
                .order_by(DisbunReferencePriceModel.effective_from.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return [
                PublicDisbunPriceItem(
                    id=r.id,
                    source_name=r.source.source_name,
                    category_code=r.category.category_code,
                    category_name=r.category.name,
                    age_group=r.category.age_group,
                    price_per_kg=r.price_per_kg,
                    effective_from=r.effective_from,
                    effective_until=r.effective_until,
                    verification_status=r.verification_status,
                    created_at=r.created_at,
                )
                for r in rows
            ], total

    async def _fetch_latest_quotes_for_mills(
        self, session: AsyncSession, mill_ids: list[UUID], now: datetime
    ) -> dict[UUID, MillPriceQuoteModel]:
        if not mill_ids:
            return {}
        stmt = (
            select(MillPriceQuoteModel)
            .options(joinedload(MillPriceQuoteModel.category))
            .where(
                MillPriceQuoteModel.mill_id.in_(mill_ids),
                MillPriceQuoteModel.status == PriceQuoteStatus.PUBLISHED.value,
                or_(
                    MillPriceQuoteModel.effective_until.is_(None),
                    MillPriceQuoteModel.effective_until >= now,
                ),
            )
            .order_by(
                MillPriceQuoteModel.mill_id.asc(),
                MillPriceQuoteModel.published_at.desc(),
                MillPriceQuoteModel.updated_at.desc(),
            )
        )
        rows = (await session.execute(stmt)).scalars().all()
        latest: dict[UUID, MillPriceQuoteModel] = {}
        for row in rows:
            if row.mill_id not in latest:
                latest[row.mill_id] = row
        return latest

    async def list_public_mills(
        self,
        *,
        page: int,
        page_size: int,
        query: str | None,
        regency: str | None,
        district: str | None,
        now: datetime,
    ) -> tuple[list[PublicMillItem], int]:
        async with self._sf() as session:
            filters: list[Any] = [
                MillModel.is_public.is_(True),
                MillModel.partnership_status == "ACTIVE",
            ]
            if query and query.strip():
                pat = f"%{query.strip()}%"
                filters.append(
                    or_(
                        MillModel.mill_name.ilike(pat),
                        MillModel.mill_code.ilike(pat),
                        MillModel.district.ilike(pat),
                        MillModel.regency.ilike(pat),
                    )
                )
            if regency and regency.strip():
                filters.append(MillModel.regency.ilike(regency.strip()))
            if district and district.strip():
                filters.append(MillModel.district.ilike(district.strip()))

            total = int(
                (
                    await session.execute(select(func.count(MillModel.id)).where(*filters))
                ).scalar_one()
            )
            stmt = (
                select(MillModel)
                .options(joinedload(MillModel.mill_company))
                .where(*filters)
                .order_by(MillModel.mill_name.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            mills = (await session.execute(stmt)).scalars().all()
            latest_map = await self._fetch_latest_quotes_for_mills(
                session, [m.id for m in mills], now
            )
            return [_to_public_mill(m, latest_map.get(m.id)) for m in mills], total

    async def get_public_mill_detail(
        self, *, mill_id: UUID, now: datetime
    ) -> PublicMillDetailData | None:
        async with self._sf() as session:
            mill = (
                await session.execute(
                    select(MillModel)
                    .options(joinedload(MillModel.mill_company))
                    .where(
                        MillModel.id == mill_id,
                        MillModel.is_public.is_(True),
                        MillModel.partnership_status == "ACTIVE",
                    )
                )
            ).scalar_one_or_none()
            if mill is None:
                return None

            quotes = (
                (
                    await session.execute(
                        select(MillPriceQuoteModel)
                        .options(
                            joinedload(MillPriceQuoteModel.mill),
                            joinedload(MillPriceQuoteModel.category),
                            joinedload(MillPriceQuoteModel.source),
                        )
                        .where(
                            MillPriceQuoteModel.mill_id == mill_id,
                            MillPriceQuoteModel.status == PriceQuoteStatus.PUBLISHED.value,
                            or_(
                                MillPriceQuoteModel.effective_until.is_(None),
                                MillPriceQuoteModel.effective_until >= now,
                            ),
                        )
                        .order_by(MillPriceQuoteModel.published_at.desc())
                    )
                )
                .scalars()
                .all()
            )
            latest = quotes[0] if quotes else None
            return PublicMillDetailData(
                mill=_to_public_mill(mill, latest),
                latest_prices=tuple(_to_public_quote(q, now=now) for q in quotes),
            )

    async def get_public_profile(self) -> PublicProfileData:
        async with self._sf() as session:
            pages = {
                p.slug: p
                for p in (
                    await session.execute(
                        select(PublicPageModel).where(
                            PublicPageModel.publication_status == "PUBLISHED"
                        )
                    )
                )
                .scalars()
                .all()
            }
            offices = (
                (
                    await session.execute(
                        select(PerumdaOfficeModel)
                        .where(PerumdaOfficeModel.is_public.is_(True))
                        .order_by(PerumdaOfficeModel.office_name.asc())
                    )
                )
                .scalars()
                .all()
            )

        about = pages.get("about-agroniaga")
        partner = pages.get("partnership-info")
        return PublicProfileData(
            organization_name="Perumda Tuah Sekata (Kabupaten Pelalawan)",
            business_unit_name="Unit Agro Niaga — Perdagangan TBS Kelapa Sawit",
            excluded_units_notice=(
                "Unit Listrik dan Gas berada di luar cakupan sistem informasi Agro Niaga."
            ),
            about_title=sanitize_public_text(about.title)
            if about
            else "Tentang Unit Agro Niaga Perumda Tuah Sekata",
            about_summary=sanitize_public_text(about.content)
            if about
            else (
                "Menghubungkan petani swadaya, koperasi mitra, dan PKS di Kabupaten Pelalawan "
                "dengan informasi harga TBS terverifikasi serta tata kelola niaga transparan."
            ),
            partnership_title=sanitize_public_text(partner.title)
            if partner
            else "Kemitraan Pasokan TBS Sawit",
            partnership_summary=sanitize_public_text(partner.content)
            if partner
            else "Informasi kemitraan koperasi tani dan PKS mitra Unit Agro Niaga.",
            partnership_requirements=(
                "Koperasi atau badan usaha resmi berbadan hukum",
                "Data identitas kebun dan ketelusuran asal TBS petani terverifikasi",
                "Kepatuhan prosedur penimbangan, surat jalan elektronik (e-DO), & rekonsiliasi",
            ),
            offices=tuple(
                PublicOfficeItem(
                    id=o.id,
                    office_name=o.office_name,
                    address=o.address,
                    latitude=o.latitude,
                    longitude=o.longitude,
                    public_contact=o.public_contact,
                )
                for o in offices
            ),
        )

    async def list_public_notices(
        self, *, page: int, page_size: int, now: datetime
    ) -> tuple[list[PublicNoticeItem], int]:
        async with self._sf() as session:
            filters = [
                PublicNoticeModel.status == "PUBLISHED",
                PublicNoticeModel.start_at <= now,
                or_(PublicNoticeModel.end_at.is_(None), PublicNoticeModel.end_at >= now),
            ]
            total = int(
                (
                    await session.execute(select(func.count(PublicNoticeModel.id)).where(*filters))
                ).scalar_one()
            )
            stmt = (
                select(PublicNoticeModel)
                .where(*filters)
                .order_by(PublicNoticeModel.start_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return [
                PublicNoticeItem(
                    id=r.id,
                    title=sanitize_public_text(r.title),
                    body=sanitize_public_text(r.body),
                    start_at=r.start_at,
                    end_at=r.end_at,
                )
                for r in rows
            ], total
