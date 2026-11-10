"""PostgreSQL repository implementation for Multi-Mill TBS Pricing and Disbun references."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import joinedload, selectinload

from app.core.audit import AuditRecordInput, append_audit_event
from app.core.exceptions import AppError, ErrorCode
from app.modules.master_data.infrastructure.models import MillModel
from app.modules.pricing.domain.entities import (
    DisbunReferencePriceEntity,
    MillPriceQuoteEntity,
    PriceCategoryEntity,
    PriceQuoteStatus,
    PriceSourceEntity,
    PriceSourceType,
    PriceVerificationEventEntity,
    VerifyDecision,
)
from app.modules.pricing.domain.rules import (
    assert_can_edit_draft,
    assert_can_publish,
    assert_can_revoke,
    assert_can_submit,
    periods_overlap,
    validate_price_period,
)
from app.modules.pricing.infrastructure.models import (
    DisbunReferencePriceModel,
    MillPriceQuoteModel,
    PriceCategoryModel,
    PriceSourceModel,
    PriceVerificationEventModel,
)


def _quote_eager_options() -> tuple[Any, ...]:
    return (
        joinedload(MillPriceQuoteModel.mill),
        joinedload(MillPriceQuoteModel.category),
        joinedload(MillPriceQuoteModel.source),
        selectinload(MillPriceQuoteModel.verification_events),
    )


def _to_quote_entity(row: MillPriceQuoteModel) -> MillPriceQuoteEntity:
    return MillPriceQuoteEntity(
        id=row.id,
        mill_id=row.mill_id,
        mill_name=row.mill.mill_name,
        mill_code=row.mill.mill_code,
        regency=row.mill.regency,
        price_category_id=row.price_category_id,
        price_category_code=row.category.category_code,
        price_category_name=row.category.name,
        unit=row.category.unit,
        source_id=row.source_id,
        source_name=row.source.source_name,
        source_type=PriceSourceType(row.source.source_type),
        price_per_kg=row.price_per_kg,
        effective_from=row.effective_from,
        effective_until=row.effective_until,
        status=PriceQuoteStatus(row.status),
        submitted_by=row.submitted_by,
        verified_by=row.verified_by,
        verified_at=row.verified_at,
        published_at=row.published_at,
        source_document_id=row.source_document_id,
        notes=row.notes,
        is_simulation=row.is_simulation,
        version=row.version,
        created_at=row.created_at,
        updated_at=row.updated_at,
        verification_events=tuple(
            PriceVerificationEventEntity(
                id=ev.id,
                action=ev.action,
                previous_status=PriceQuoteStatus(ev.previous_status),
                new_status=PriceQuoteStatus(ev.new_status),
                actor_id=ev.actor_id,
                reason=ev.reason,
                created_at=ev.created_at,
            )
            for ev in row.verification_events
        ),
    )


def _to_disbun_entity(row: DisbunReferencePriceModel) -> DisbunReferencePriceEntity:
    return DisbunReferencePriceEntity(
        id=row.id,
        price_source_id=row.price_source_id,
        source_name=row.source.source_name,
        price_category_id=row.price_category_id,
        category_code=row.category.category_code,
        category_name=row.category.name,
        age_group=row.category.age_group,
        price_per_kg=row.price_per_kg,
        effective_from=row.effective_from,
        effective_until=row.effective_until,
        verification_status=row.verification_status,
        created_at=row.created_at,
    )


class SqlAlchemyPricingRepository:
    """Async PostgreSQL adapter enforcing SM-01 locking, SOD-01, and history preservation."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

    async def list_reference_metadata(
        self,
    ) -> tuple[list[PriceSourceEntity], list[PriceCategoryEntity]]:
        async with self._sf() as session:
            sources = (
                (
                    await session.execute(
                        select(PriceSourceModel)
                        .where(PriceSourceModel.status == "ACTIVE")
                        .order_by(PriceSourceModel.source_code.asc())
                    )
                )
                .scalars()
                .all()
            )
            cats = (
                (
                    await session.execute(
                        select(PriceCategoryModel)
                        .where(PriceCategoryModel.is_active.is_(True))
                        .order_by(PriceCategoryModel.category_code.asc())
                    )
                )
                .scalars()
                .all()
            )
            return (
                [
                    PriceSourceEntity(
                        id=s.id,
                        source_code=s.source_code,
                        source_name=s.source_name,
                        source_type=PriceSourceType(s.source_type),
                        status=s.status,
                    )
                    for s in sources
                ],
                [
                    PriceCategoryEntity(
                        id=c.id,
                        category_code=c.category_code,
                        name=c.name,
                        unit=c.unit,
                        quality_basis=c.quality_basis,
                        age_group=c.age_group,
                        is_active=c.is_active,
                    )
                    for c in cats
                ],
            )

    async def get_quote_by_id(self, quote_id: UUID) -> MillPriceQuoteEntity | None:
        async with self._sf() as session:
            stmt = (
                select(MillPriceQuoteModel)
                .options(*_quote_eager_options())
                .where(MillPriceQuoteModel.id == quote_id)
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            return _to_quote_entity(row) if row is not None else None

    async def list_internal_quotes(
        self,
        *,
        allowed_statuses: tuple[PriceQuoteStatus, ...] | None,
        status_filter: PriceQuoteStatus | None,
        mill_id: UUID | None,
        page: int,
        page_size: int,
    ) -> tuple[list[MillPriceQuoteEntity], int]:
        async with self._sf() as session:
            filters: list[Any] = []
            if allowed_statuses is not None:
                filters.append(MillPriceQuoteModel.status.in_([s.value for s in allowed_statuses]))
            if status_filter is not None:
                filters.append(MillPriceQuoteModel.status == status_filter.value)
            if mill_id is not None:
                filters.append(MillPriceQuoteModel.mill_id == mill_id)

            total = int(
                (
                    await session.execute(
                        select(func.count(MillPriceQuoteModel.id)).where(*filters)
                    )
                ).scalar_one()
            )
            stmt = (
                select(MillPriceQuoteModel)
                .options(*_quote_eager_options())
                .where(*filters)
                .order_by(MillPriceQuoteModel.updated_at.desc(), MillPriceQuoteModel.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            rows = (await session.execute(stmt)).scalars().unique().all()
            return [_to_quote_entity(r) for r in rows], total

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
    ) -> MillPriceQuoteEntity:
        quote_id = uuid4()
        async with self._sf() as session:
            async with session.begin():
                mill = (
                    await session.execute(select(MillModel).where(MillModel.id == mill_id))
                ).scalar_one_or_none()
                if mill is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND, "PKS tujuan tidak ditemukan.")
                cat = (
                    await session.execute(
                        select(PriceCategoryModel).where(
                            PriceCategoryModel.id == price_category_id,
                            PriceCategoryModel.is_active.is_(True),
                        )
                    )
                ).scalar_one_or_none()
                if cat is None:
                    raise AppError(ErrorCode.VAL_INVALID_FORMAT, "Kategori harga tidak aktif.")
                src = (
                    await session.execute(
                        select(PriceSourceModel).where(
                            PriceSourceModel.id == source_id,
                            PriceSourceModel.status == "ACTIVE",
                        )
                    )
                ).scalar_one_or_none()
                if src is None or src.source_type == PriceSourceType.DISBUN.value:
                    raise AppError(
                        ErrorCode.VAL_INVALID_FORMAT,
                        "Sumber harga PKS tidak valid (harga Disbun dikelola terpisah).",
                    )

                session.add(
                    MillPriceQuoteModel(
                        id=quote_id,
                        mill_id=mill_id,
                        price_category_id=price_category_id,
                        source_id=source_id,
                        price_per_kg=price_per_kg,
                        effective_from=effective_from,
                        effective_until=effective_until,
                        status=PriceQuoteStatus.DRAFT.value,
                        submitted_by=actor_id,
                        verified_by=None,
                        verified_at=None,
                        published_at=None,
                        source_document_id=source_document_id,
                        notes=notes,
                        is_simulation=True,
                        version=1,
                        created_at=now,
                        updated_at=now,
                    )
                )
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="PRICE_DRAFT_CREATED",
                        module="pricing",
                        resource_type="mill_price_quotes",
                        resource_id=str(quote_id),
                        new_state={
                            "mill_id": str(mill_id),
                            "price_per_kg": f"{price_per_kg:.2f}",
                            "status": PriceQuoteStatus.DRAFT.value,
                        },
                        occurred_at=now,
                    ),
                )
        created = await self.get_quote_by_id(quote_id)
        if created is None:
            raise AppError(ErrorCode.SYS_INTERNAL_ERROR)
        return created

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
    ) -> MillPriceQuoteEntity:
        async with self._sf() as session:
            async with session.begin():
                row = (
                    await session.execute(
                        select(MillPriceQuoteModel)
                        .where(MillPriceQuoteModel.id == quote_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if row is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                assert_can_edit_draft(PriceQuoteStatus(row.status))
                if row.version != expected_version:
                    raise AppError(
                        ErrorCode.MD_STALE_RECORD_VERSION,
                        details={
                            "expected_version": expected_version,
                            "current_version": row.version,
                        },
                    )
                next_from = effective_from if effective_from is not None else row.effective_from
                next_until = effective_until if update_effective_until else row.effective_until
                validate_price_period(next_from, next_until)

                if price_per_kg is not None:
                    row.price_per_kg = price_per_kg
                row.effective_from = next_from
                row.effective_until = next_until
                if update_source_doc:
                    row.source_document_id = source_document_id
                if update_notes:
                    row.notes = notes
                row.version += 1
                row.updated_at = now
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="PRICE_DRAFT_UPDATED",
                        module="pricing",
                        resource_type="mill_price_quotes",
                        resource_id=str(quote_id),
                        new_state={
                            "price_per_kg": f"{row.price_per_kg:.2f}",
                            "version": row.version,
                        },
                        occurred_at=now,
                    ),
                )
        updated = await self.get_quote_by_id(quote_id)
        if updated is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        return updated

    async def submit_for_verification(
        self, *, quote_id: UUID, actor_id: UUID, now: datetime
    ) -> MillPriceQuoteEntity:
        async with self._sf() as session:
            async with session.begin():
                row = (
                    await session.execute(
                        select(MillPriceQuoteModel)
                        .where(MillPriceQuoteModel.id == quote_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if row is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                assert_can_submit(PriceQuoteStatus(row.status))
                prev_status = row.status
                row.status = PriceQuoteStatus.PENDING_VERIFICATION.value
                row.submitted_by = actor_id
                row.version += 1
                row.updated_at = now
                await session.flush()

                session.add(
                    PriceVerificationEventModel(
                        id=uuid4(),
                        price_quote_id=quote_id,
                        action="SUBMIT_PRICE_FOR_VERIFICATION",
                        previous_status=prev_status,
                        new_status=row.status,
                        actor_id=actor_id,
                        reason=None,
                        created_at=now,
                    )
                )
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="PRICE_SUBMITTED",
                        module="pricing",
                        resource_type="mill_price_quotes",
                        resource_id=str(quote_id),
                        previous_state={"status": prev_status},
                        new_state={"status": row.status},
                        occurred_at=now,
                    ),
                )
        updated = await self.get_quote_by_id(quote_id)
        if updated is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        return updated

    async def verify_or_reject(
        self,
        *,
        quote_id: UUID,
        decision: VerifyDecision,
        reason: str | None,
        actor_id: UUID,
        is_admin_forbidden: bool,
        now: datetime,
    ) -> MillPriceQuoteEntity:
        if is_admin_forbidden:
            raise AppError(ErrorCode.AUTH_OPERATION_FORBIDDEN)
        async with self._sf() as session:
            async with session.begin():
                row = (
                    await session.execute(
                        select(MillPriceQuoteModel)
                        .where(MillPriceQuoteModel.id == quote_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if row is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                if row.status != PriceQuoteStatus.PENDING_VERIFICATION.value:
                    raise AppError(
                        ErrorCode.PRICE_INVALID_STATE_TRANSITION,
                        details={"current_status": row.status, "requested_action": "VERIFY"},
                    )
                if row.submitted_by == actor_id:
                    raise AppError(
                        ErrorCode.AUTH_CONFLICT_OF_DUTIES,
                        details={"rule": "SOD-01", "submitted_by": str(row.submitted_by)},
                    )
                prev_status = row.status
                new_status = (
                    PriceQuoteStatus.VERIFIED.value
                    if decision == VerifyDecision.APPROVE
                    else PriceQuoteStatus.REJECTED.value
                )
                row.status = new_status
                row.verified_by = actor_id
                row.verified_at = now
                row.version += 1
                row.updated_at = now
                await session.flush()

                session.add(
                    PriceVerificationEventModel(
                        id=uuid4(),
                        price_quote_id=quote_id,
                        action=(
                            "APPROVE_PRICE_VERIFICATION"
                            if decision == VerifyDecision.APPROVE
                            else "REJECT_PRICE_VERIFICATION"
                        ),
                        previous_status=prev_status,
                        new_status=new_status,
                        actor_id=actor_id,
                        reason=reason,
                        created_at=now,
                    )
                )
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type=f"PRICE_{new_status}",
                        module="pricing",
                        resource_type="mill_price_quotes",
                        resource_id=str(quote_id),
                        previous_state={"status": prev_status},
                        new_state={"status": new_status},
                        reason=reason,
                        occurred_at=now,
                    ),
                )
        updated = await self.get_quote_by_id(quote_id)
        if updated is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        return updated

    async def publish_quote(
        self, *, quote_id: UUID, actor_id: UUID, now: datetime
    ) -> MillPriceQuoteEntity:
        async with self._sf() as session:
            async with session.begin():
                row = (
                    await session.execute(
                        select(MillPriceQuoteModel)
                        .where(MillPriceQuoteModel.id == quote_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if row is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)

                # Serialize concurrent publications per mill + category on PostgreSQL.
                mill_row = (
                    await session.execute(
                        select(MillModel).where(MillModel.id == row.mill_id).with_for_update()
                    )
                ).scalar_one()
                if mill_row.partnership_status != "ACTIVE":
                    raise AppError(
                        ErrorCode.PRICE_INVALID_STATE_TRANSITION,
                        "PKS berstatus nonaktif sehingga harga tidak dapat dipublikasikan.",
                    )

                assert_can_publish(PriceQuoteStatus(row.status))

                published_rows = (
                    (
                        await session.execute(
                            select(MillPriceQuoteModel)
                            .where(
                                MillPriceQuoteModel.mill_id == row.mill_id,
                                MillPriceQuoteModel.price_category_id == row.price_category_id,
                                MillPriceQuoteModel.status == PriceQuoteStatus.PUBLISHED.value,
                                MillPriceQuoteModel.id != quote_id,
                            )
                            .with_for_update()
                        )
                    )
                    .scalars()
                    .all()
                )
                for active_row in published_rows:
                    if periods_overlap(
                        row.effective_from,
                        row.effective_until,
                        active_row.effective_from,
                        active_row.effective_until,
                    ):
                        raise AppError(
                            ErrorCode.PRICE_OVERLAPPING_PERIOD,
                            details={"conflicting_price_quote_id": str(active_row.id)},
                        )

                prev_status = row.status
                row.status = PriceQuoteStatus.PUBLISHED.value
                row.published_at = now
                row.version += 1
                row.updated_at = now
                await session.flush()

                session.add(
                    PriceVerificationEventModel(
                        id=uuid4(),
                        price_quote_id=quote_id,
                        action="PUBLISH_PRICE",
                        previous_status=prev_status,
                        new_status=row.status,
                        actor_id=actor_id,
                        reason=None,
                        created_at=now,
                    )
                )
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="PRICE_PUBLISHED",
                        module="pricing",
                        resource_type="mill_price_quotes",
                        resource_id=str(quote_id),
                        previous_state={"status": prev_status},
                        new_state={"status": row.status, "mill_id": str(row.mill_id)},
                        occurred_at=now,
                    ),
                )
        updated = await self.get_quote_by_id(quote_id)
        if updated is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        return updated

    async def revoke_quote(
        self, *, quote_id: UUID, reason: str, actor_id: UUID, now: datetime
    ) -> MillPriceQuoteEntity:
        async with self._sf() as session:
            async with session.begin():
                row = (
                    await session.execute(
                        select(MillPriceQuoteModel)
                        .where(MillPriceQuoteModel.id == quote_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if row is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                assert_can_revoke(PriceQuoteStatus(row.status))
                prev_status = row.status
                row.status = PriceQuoteStatus.REVOKED.value
                row.version += 1
                row.updated_at = now
                await session.flush()

                session.add(
                    PriceVerificationEventModel(
                        id=uuid4(),
                        price_quote_id=quote_id,
                        action="REVOKE_PRICE",
                        previous_status=prev_status,
                        new_status=row.status,
                        actor_id=actor_id,
                        reason=reason,
                        created_at=now,
                    )
                )
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="PRICE_REVOKED",
                        module="pricing",
                        resource_type="mill_price_quotes",
                        resource_id=str(quote_id),
                        previous_state={"status": prev_status},
                        new_state={"status": row.status},
                        reason=reason,
                        occurred_at=now,
                    ),
                )
        updated = await self.get_quote_by_id(quote_id)
        if updated is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        return updated

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
    ) -> DisbunReferencePriceEntity:
        did = uuid4()
        async with self._sf() as session:
            async with session.begin():
                src = (
                    await session.execute(
                        select(PriceSourceModel).where(
                            PriceSourceModel.id == price_source_id,
                            PriceSourceModel.status == "ACTIVE",
                        )
                    )
                ).scalar_one_or_none()
                if src is None or src.source_type != PriceSourceType.DISBUN.value:
                    raise AppError(
                        ErrorCode.VAL_INVALID_FORMAT,
                        "Harga acuan Disbun wajib memilih sumber bertipe DISBUN yang aktif.",
                    )
                cat = (
                    await session.execute(
                        select(PriceCategoryModel).where(
                            PriceCategoryModel.id == price_category_id,
                            PriceCategoryModel.is_active.is_(True),
                        )
                    )
                ).scalar_one_or_none()
                if cat is None:
                    raise AppError(ErrorCode.VAL_INVALID_FORMAT, "Kategori harga tidak aktif.")

                session.add(
                    DisbunReferencePriceModel(
                        id=did,
                        price_source_id=price_source_id,
                        price_category_id=price_category_id,
                        price_per_kg=price_per_kg,
                        effective_from=effective_from,
                        effective_until=effective_until,
                        source_document_id=source_document_id,
                        verification_status="PUBLISHED",
                        created_at=now,
                    )
                )
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="DISBUN_PRICE_CREATED",
                        module="pricing",
                        resource_type="disbun_reference_prices",
                        resource_id=str(did),
                        new_state={"price_per_kg": f"{price_per_kg:.2f}"},
                        occurred_at=now,
                    ),
                )
        async with self._sf() as session:
            stmt = (
                select(DisbunReferencePriceModel)
                .options(
                    joinedload(DisbunReferencePriceModel.source),
                    joinedload(DisbunReferencePriceModel.category),
                )
                .where(DisbunReferencePriceModel.id == did)
            )
            row = (await session.execute(stmt)).scalar_one()
            return _to_disbun_entity(row)
