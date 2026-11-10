"""PostgreSQL repository implementation for TBS Receiving, Revisioned Weighing, and Grading."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import delete, func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from app.core.audit import AuditRecordInput, append_audit_event
from app.core.exceptions import AppError, ErrorCode
from app.core.idempotency import complete_idempotency_slot
from app.modules.master_data.infrastructure.models import (
    CooperativeMembershipModel,
    FarmerModel,
    FarmModel,
)
from app.modules.tbs_receiving.domain.entities import (
    GradingDeductionType,
    ReceiptGradingItemEntity,
    ReceiptStatus,
    ReceiptWeighingRevisionEntity,
    TbsReceiptEntity,
)
from app.modules.tbs_receiving.domain.rules import (
    GradingInputItem,
    assert_can_cancel_receipt,
    assert_receipt_mutable,
    compute_grading_deductions,
)
from app.modules.tbs_receiving.infrastructure.models import (
    ReceiptGradingItemModel,
    ReceiptWeighingRevisionModel,
    TbsReceiptModel,
)


def _receipt_load_options() -> tuple[Any, ...]:
    return (
        selectinload(TbsReceiptModel.weighing_revisions).selectinload(
            ReceiptWeighingRevisionModel.grading_items
        ),
    )


def _to_weighing_entity(row: ReceiptWeighingRevisionModel) -> ReceiptWeighingRevisionEntity:
    return ReceiptWeighingRevisionEntity(
        id=row.id,
        revision_number=row.revision_number,
        gross_weight_kg=row.gross_weight_kg,
        tare_weight_kg=row.tare_weight_kg,
        net_weight_kg=row.net_weight_kg,
        weighed_at=row.weighed_at,
        weighed_by=row.weighed_by,
        is_current=row.is_current,
        correction_reason=row.correction_reason,
    )


def _to_grading_entity(row: ReceiptGradingItemModel) -> ReceiptGradingItemEntity:
    return ReceiptGradingItemEntity(
        id=row.id,
        grading_category=row.grading_category,
        measurement_value=row.measurement_value,
        deduction_type=GradingDeductionType(row.deduction_type),
        deduction_value=row.deduction_value,
        deduction_weight_kg=row.deduction_weight_kg,
        deduction_amount=row.deduction_amount,
        calculation_basis=row.calculation_basis,
        is_simulation=row.is_simulation,
        notes=row.notes,
    )


def _build_receipt_entity(
    row: TbsReceiptModel,
    *,
    farmer_name: str,
    farm_name: str,
) -> TbsReceiptEntity:
    revisions_sorted = sorted(row.weighing_revisions, key=lambda r: r.revision_number)
    rev_entities = tuple(_to_weighing_entity(r) for r in revisions_sorted)
    current_row = next((r for r in revisions_sorted if r.is_current), None)
    current_entity = _to_weighing_entity(current_row) if current_row is not None else None
    grading_entities = (
        tuple(_to_grading_entity(g) for g in current_row.grading_items)
        if current_row is not None
        else ()
    )

    net_after_grading: Decimal | None = None
    if current_row is not None:
        total_weight_deduction = sum(
            (g.deduction_weight_kg for g in grading_entities if g.deduction_weight_kg is not None),
            start=Decimal("0.000"),
        )
        net_after_grading = (current_row.net_weight_kg - total_weight_deduction).quantize(
            Decimal("0.001"), rounding=ROUND_HALF_UP
        )

    return TbsReceiptEntity(
        id=row.id,
        receipt_number=row.receipt_number,
        farmer_id=row.farmer_id,
        farmer_name=farmer_name,
        farm_id=row.farm_id,
        farm_name=farm_name,
        cooperative_id=row.cooperative_id,
        harvest_date=row.harvest_date,
        received_at=row.received_at,
        status=ReceiptStatus(row.status),
        current_weighing=current_entity,
        net_weight_after_grading_kg=net_after_grading,
        weighing_revisions=rev_entities,
        grading_items=grading_entities,
        version=row.version,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _require_entity(entity: TbsReceiptEntity | None) -> TbsReceiptEntity:
    if entity is None:
        raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
    return entity


async def _fetch_receipt_with_names(
    session: AsyncSession, receipt_id: UUID
) -> TbsReceiptEntity | None:
    stmt = (
        select(TbsReceiptModel, FarmerModel.full_name, FarmModel.farm_name)
        .join(FarmerModel, FarmerModel.id == TbsReceiptModel.farmer_id)
        .join(FarmModel, FarmModel.id == TbsReceiptModel.farm_id)
        .options(*_receipt_load_options())
        .where(TbsReceiptModel.id == receipt_id)
    )
    row_tuple = (await session.execute(stmt)).first()
    if row_tuple is None:
        return None
    receipt_row, farmer_name, farm_name = row_tuple
    return _build_receipt_entity(receipt_row, farmer_name=farmer_name, farm_name=farm_name)


def _assert_coop_membership_scope(
    cooperative_id: UUID, allowed_cooperative_ids: set[UUID] | None
) -> None:
    if allowed_cooperative_ids is not None and cooperative_id not in allowed_cooperative_ids:
        raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)


class SqlAlchemyTbsReceivingRepository:
    """PostgreSQL implementation of TbsReceivingRepositoryPort."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def list_receipts(
        self,
        *,
        allowed_farmer_ids: set[UUID] | None,
        allowed_cooperative_ids: set[UUID] | None,
        status_filter: ReceiptStatus | None,
        date_from: date | None,
        date_to: date | None,
        page: int,
        page_size: int,
    ) -> tuple[list[TbsReceiptEntity], int]:
        filters: list[Any] = []
        if allowed_farmer_ids is not None:
            if not allowed_farmer_ids:
                return [], 0
            filters.append(TbsReceiptModel.farmer_id.in_(allowed_farmer_ids))
        if allowed_cooperative_ids is not None:
            if not allowed_cooperative_ids:
                return [], 0
            filters.append(TbsReceiptModel.cooperative_id.in_(allowed_cooperative_ids))
        if status_filter is not None:
            filters.append(TbsReceiptModel.status == status_filter.value)
        if date_from is not None:
            filters.append(func.date(TbsReceiptModel.received_at) >= date_from)
        if date_to is not None:
            filters.append(func.date(TbsReceiptModel.received_at) <= date_to)

        async with self._session_factory() as session:
            total = int(
                (
                    await session.execute(
                        select(func.count()).select_from(TbsReceiptModel).where(*filters)
                    )
                ).scalar_one()
            )
            stmt = (
                select(TbsReceiptModel, FarmerModel.full_name, FarmModel.farm_name)
                .join(FarmerModel, FarmerModel.id == TbsReceiptModel.farmer_id)
                .join(FarmModel, FarmModel.id == TbsReceiptModel.farm_id)
                .options(*_receipt_load_options())
                .where(*filters)
                .order_by(TbsReceiptModel.received_at.desc(), TbsReceiptModel.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            rows = (await session.execute(stmt)).all()
            return [
                _build_receipt_entity(r, farmer_name=f_name, farm_name=farm_name)
                for r, f_name, farm_name in rows
            ], total

    async def get_receipt_by_id(self, receipt_id: UUID) -> TbsReceiptEntity | None:
        async with self._session_factory() as session:
            return await _fetch_receipt_with_names(session, receipt_id)

    async def create_receipt_draft(
        self,
        *,
        farmer_id: UUID,
        farm_id: UUID,
        harvest_date: date | None,
        received_at: datetime,
        notes: str | None,
        allowed_cooperative_ids: set[UUID] | None,
        actor_id: UUID,
        idempotency_record_id: UUID,
    ) -> TbsReceiptEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                farmer = (
                    await session.execute(select(FarmerModel).where(FarmerModel.id == farmer_id))
                ).scalar_one_or_none()
                if farmer is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                if farmer.status != "ACTIVE":
                    raise AppError(
                        ErrorCode.VAL_INVALID_FORMAT,
                        details=[
                            {
                                "field": "farmer_id",
                                "reason": "Petani berstatus INACTIVE dan tidak dapat dicatat.",
                                "code": ErrorCode.VAL_INVALID_FORMAT.value,
                            }
                        ],
                    )

                farm = (
                    await session.execute(select(FarmModel).where(FarmModel.id == farm_id))
                ).scalar_one_or_none()
                if farm is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                if farm.farmer_id != farmer_id:
                    raise AppError(
                        ErrorCode.VAL_INVALID_FORMAT,
                        details=[
                            {
                                "field": "farm_id",
                                "reason": "Kebun yang dipilih bukan milik petani tersebut.",
                                "code": ErrorCode.VAL_INVALID_FORMAT.value,
                            }
                        ],
                    )

                membership = (
                    await session.execute(
                        select(CooperativeMembershipModel).where(
                            CooperativeMembershipModel.farmer_id == farmer_id,
                            CooperativeMembershipModel.status == "ACTIVE",
                            CooperativeMembershipModel.ended_at.is_(None),
                        )
                    )
                ).scalar_one_or_none()
                if membership is None:
                    raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)
                _assert_coop_membership_scope(membership.cooperative_id, allowed_cooperative_ids)

                seq_val = int(
                    (await session.execute(text("SELECT nextval('tbs_receipt_seq')"))).scalar_one()
                )
                receipt_number = (
                    f"RCV-{received_at.astimezone(UTC).strftime('%Y-%m%d')}-{seq_val:04d}"
                )

                receipt = TbsReceiptModel(
                    id=uuid4(),
                    receipt_number=receipt_number,
                    farmer_id=farmer_id,
                    farm_id=farm_id,
                    cooperative_id=membership.cooperative_id,
                    harvest_date=harvest_date,
                    received_at=received_at.astimezone(UTC),
                    status=ReceiptStatus.DRAFT.value,
                    notes=notes,
                    created_by=actor_id,
                    created_at=now,
                    updated_at=now,
                    version=1,
                )
                session.add(receipt)
                try:
                    await session.flush()
                except IntegrityError as exc:
                    raise AppError(ErrorCode.TBS_DUPLICATE_RECEIPT) from exc

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="RECEIPT_DRAFT_CREATED",
                        module="tbs_receiving",
                        resource_type="tbs_receipts",
                        resource_id=str(receipt.id),
                        previous_state=None,
                        new_state={
                            "receipt_number": receipt.receipt_number,
                            "farmer_id": str(farmer_id),
                            "farm_id": str(farm_id),
                            "cooperative_id": str(membership.cooperative_id),
                            "status": ReceiptStatus.DRAFT.value,
                        },
                        reason=notes,
                    ),
                )
                await complete_idempotency_slot(
                    session,
                    record_id=idempotency_record_id,
                    response_reference=receipt.id,
                )
                receipt_id = receipt.id

        async with self._session_factory() as read_session:
            return _require_entity(await _fetch_receipt_with_names(read_session, receipt_id))

    async def record_weighing(
        self,
        *,
        receipt_id: UUID,
        expected_version: int,
        gross_weight_kg: Decimal,
        tare_weight_kg: Decimal,
        net_weight_kg: Decimal,
        correction_reason: str | None,
        allowed_cooperative_ids: set[UUID] | None,
        actor_id: UUID,
    ) -> TbsReceiptEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                receipt = (
                    await session.execute(
                        select(TbsReceiptModel)
                        .where(TbsReceiptModel.id == receipt_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if receipt is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                _assert_coop_membership_scope(receipt.cooperative_id, allowed_cooperative_ids)

                current_status = ReceiptStatus(receipt.status)
                assert_receipt_mutable(current_status)
                if receipt.version != expected_version:
                    raise AppError(
                        ErrorCode.TBS_STALE_RECORD_VERSION,
                        details={"current_version": receipt.version},
                    )

                existing_revs = (
                    (
                        await session.execute(
                            select(ReceiptWeighingRevisionModel)
                            .where(ReceiptWeighingRevisionModel.receipt_id == receipt_id)
                            .order_by(ReceiptWeighingRevisionModel.revision_number)
                            .with_for_update()
                        )
                    )
                    .scalars()
                    .all()
                )
                if (
                    existing_revs or current_status == ReceiptStatus.VALIDATED
                ) and not correction_reason:
                    raise AppError(
                        ErrorCode.VAL_REQUIRED_FIELD,
                        details=[
                            {
                                "field": "correction_reason",
                                "reason": (
                                    "Alasan koreksi timbang wajib diisi untuk revisi (BR-WGT-001)."
                                ),
                                "code": ErrorCode.VAL_REQUIRED_FIELD.value,
                            }
                        ],
                    )

                prev_current = next((r for r in existing_revs if r.is_current), None)
                next_rev_num = (existing_revs[-1].revision_number + 1) if existing_revs else 1
                if prev_current is not None:
                    prev_current.is_current = False
                    await session.flush()

                new_rev = ReceiptWeighingRevisionModel(
                    id=uuid4(),
                    receipt_id=receipt_id,
                    revision_number=next_rev_num,
                    gross_weight_kg=gross_weight_kg,
                    tare_weight_kg=tare_weight_kg,
                    net_weight_kg=net_weight_kg,
                    weighed_at=now,
                    weighed_by=actor_id,
                    is_current=True,
                    correction_reason=correction_reason,
                    created_at=now,
                )
                session.add(new_rev)
                receipt.version += 1
                receipt.updated_at = now

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="RECEIPT_WEIGHING_RECORDED",
                        module="tbs_receiving",
                        resource_type="receipt_weighing_revisions",
                        resource_id=str(receipt.id),
                        previous_state=(
                            {
                                "revision_number": prev_current.revision_number,
                                "net_weight_kg": f"{prev_current.net_weight_kg:.3f}",
                            }
                            if prev_current is not None
                            else None
                        ),
                        new_state={
                            "revision_number": next_rev_num,
                            "gross_weight_kg": f"{gross_weight_kg:.3f}",
                            "tare_weight_kg": f"{tare_weight_kg:.3f}",
                            "net_weight_kg": f"{net_weight_kg:.3f}",
                            "version": receipt.version,
                        },
                        reason=correction_reason,
                    ),
                )

        async with self._session_factory() as read_session:
            return _require_entity(await _fetch_receipt_with_names(read_session, receipt_id))

    async def record_grading(
        self,
        *,
        receipt_id: UUID,
        expected_version: int,
        items: list[GradingInputItem],
        allowed_cooperative_ids: set[UUID] | None,
        actor_id: UUID,
    ) -> TbsReceiptEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                receipt = (
                    await session.execute(
                        select(TbsReceiptModel)
                        .where(TbsReceiptModel.id == receipt_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if receipt is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                _assert_coop_membership_scope(receipt.cooperative_id, allowed_cooperative_ids)

                current_status = ReceiptStatus(receipt.status)
                assert_receipt_mutable(current_status)
                if receipt.version != expected_version:
                    raise AppError(
                        ErrorCode.TBS_STALE_RECORD_VERSION,
                        details={"current_version": receipt.version},
                    )

                current_rev = (
                    await session.execute(
                        select(ReceiptWeighingRevisionModel)
                        .where(
                            ReceiptWeighingRevisionModel.receipt_id == receipt_id,
                            ReceiptWeighingRevisionModel.is_current.is_(True),
                        )
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if current_rev is None:
                    raise AppError(
                        ErrorCode.TBS_INVALID_STATE_TRANSITION,
                        details={"current_status": current_status.value},
                    )

                computed, net_after = compute_grading_deductions(
                    base_net_weight_kg=current_rev.net_weight_kg,
                    items=items,
                )

                await session.execute(
                    delete(ReceiptGradingItemModel).where(
                        ReceiptGradingItemModel.weighing_revision_id == current_rev.id
                    )
                )
                await session.flush()

                for item in computed:
                    session.add(
                        ReceiptGradingItemModel(
                            id=uuid4(),
                            weighing_revision_id=current_rev.id,
                            grading_category=item.grading_category,
                            measurement_value=item.measurement_value,
                            deduction_type=item.deduction_type.value,
                            deduction_value=item.deduction_value,
                            deduction_weight_kg=item.deduction_weight_kg,
                            deduction_amount=item.deduction_amount,
                            calculation_basis=item.calculation_basis,
                            is_simulation=True,
                            notes=item.notes,
                            created_at=now,
                        )
                    )

                receipt.version += 1
                receipt.updated_at = now

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="RECEIPT_GRADING_RECORDED",
                        module="tbs_receiving",
                        resource_type="receipt_grading_items",
                        resource_id=str(receipt.id),
                        previous_state=None,
                        new_state={
                            "weighing_revision_id": str(current_rev.id),
                            "items_count": len(computed),
                            "base_net_weight_kg": f"{current_rev.net_weight_kg:.3f}",
                            "net_weight_after_grading_kg": f"{net_after:.3f}",
                            "is_simulation": True,
                        },
                        reason=None,
                    ),
                )

        async with self._session_factory() as read_session:
            return _require_entity(await _fetch_receipt_with_names(read_session, receipt_id))

    async def validate_receipt(
        self,
        *,
        receipt_id: UUID,
        allowed_cooperative_ids: set[UUID] | None,
        actor_id: UUID,
    ) -> TbsReceiptEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                receipt = (
                    await session.execute(
                        select(TbsReceiptModel)
                        .where(TbsReceiptModel.id == receipt_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if receipt is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                _assert_coop_membership_scope(receipt.cooperative_id, allowed_cooperative_ids)

                current_status = ReceiptStatus(receipt.status)
                if current_status != ReceiptStatus.DRAFT:
                    raise AppError(
                        ErrorCode.TBS_INVALID_STATE_TRANSITION,
                        details={"current_status": current_status.value},
                    )

                current_rev = (
                    await session.execute(
                        select(ReceiptWeighingRevisionModel).where(
                            ReceiptWeighingRevisionModel.receipt_id == receipt_id,
                            ReceiptWeighingRevisionModel.is_current.is_(True),
                        )
                    )
                ).scalar_one_or_none()
                if current_rev is None:
                    raise AppError(
                        ErrorCode.TBS_INVALID_STATE_TRANSITION,
                        details={"current_status": current_status.value},
                    )

                receipt.status = ReceiptStatus.VALIDATED.value
                receipt.version += 1
                receipt.updated_at = now

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="RECEIPT_VALIDATED",
                        module="tbs_receiving",
                        resource_type="tbs_receipts",
                        resource_id=str(receipt.id),
                        previous_state={"status": ReceiptStatus.DRAFT.value},
                        new_state={
                            "status": ReceiptStatus.VALIDATED.value,
                            "current_weighing_revision": current_rev.revision_number,
                            "net_weight_kg": f"{current_rev.net_weight_kg:.3f}",
                        },
                        reason=None,
                    ),
                )

        async with self._session_factory() as read_session:
            return _require_entity(await _fetch_receipt_with_names(read_session, receipt_id))

    async def cancel_receipt(
        self,
        *,
        receipt_id: UUID,
        expected_version: int,
        reason: str,
        allowed_cooperative_ids: set[UUID] | None,
        actor_id: UUID,
    ) -> TbsReceiptEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                receipt = (
                    await session.execute(
                        select(TbsReceiptModel)
                        .where(TbsReceiptModel.id == receipt_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if receipt is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                _assert_coop_membership_scope(receipt.cooperative_id, allowed_cooperative_ids)

                current_status = ReceiptStatus(receipt.status)
                assert_can_cancel_receipt(current_status)
                if receipt.version != expected_version:
                    raise AppError(
                        ErrorCode.TBS_STALE_RECORD_VERSION,
                        details={"current_version": receipt.version},
                    )

                receipt.status = ReceiptStatus.CANCELLED.value
                receipt.version += 1
                receipt.updated_at = now

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="RECEIPT_CANCELLED",
                        module="tbs_receiving",
                        resource_type="tbs_receipts",
                        resource_id=str(receipt.id),
                        previous_state={"status": current_status.value},
                        new_state={"status": ReceiptStatus.CANCELLED.value},
                        reason=reason,
                    ),
                )

        async with self._session_factory() as read_session:
            return _require_entity(await _fetch_receipt_with_names(read_session, receipt_id))
