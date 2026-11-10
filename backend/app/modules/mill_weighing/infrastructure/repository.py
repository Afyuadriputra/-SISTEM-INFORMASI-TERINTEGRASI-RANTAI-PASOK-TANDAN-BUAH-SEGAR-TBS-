"""PostgreSQL repository implementation for Mill Weighing Tickets & Arrival Receipt trigger."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from app.core.audit import AuditRecordInput, append_audit_event
from app.core.exceptions import AppError, ErrorCode
from app.core.idempotency import complete_idempotency_slot
from app.modules.contracts.infrastructure.quota_ops import consume_quota_reservation_in_tx
from app.modules.files.infrastructure.models import FileAssetModel
from app.modules.finance.infrastructure.models import InvoiceModel
from app.modules.logistics.domain.entities import DeliveryOrderStatus
from app.modules.logistics.infrastructure.models import (
    DeliveryOrderModel,
    DeliveryStatusEventModel,
)
from app.modules.mill_weighing.domain.entities import (
    MillGradingDeductionType,
    MillGradingItemEntity,
    MillTicketStatus,
    MillWeighingTicketEntity,
)
from app.modules.mill_weighing.domain.rules import (
    ValidatedMillGradingItem,
    assert_ticket_can_revise,
    assert_ticket_can_verify,
)
from app.modules.mill_weighing.infrastructure.models import (
    MillGradingItemModel,
    MillWeighingTicketModel,
)
from app.modules.reconciliation.infrastructure.models import ReconciliationCaseModel


def _to_ticket_entity(row: MillWeighingTicketModel) -> MillWeighingTicketEntity:
    return MillWeighingTicketEntity(
        id=row.id,
        delivery_order_id=row.delivery_order_id,
        mill_id=row.mill_id,
        ticket_number=row.ticket_number,
        revision_number=row.revision_number,
        previous_ticket_id=row.previous_ticket_id,
        gross_weight_kg=row.gross_weight_kg,
        tare_weight_kg=row.tare_weight_kg,
        net_weight_kg=row.net_weight_kg,
        weighed_at=row.weighed_at,
        verified_at=row.verified_at,
        verified_by=row.verified_by,
        is_current=row.is_current,
        status=MillTicketStatus(row.status),
        proof_file_id=row.proof_file_id,
        correction_reason=row.correction_reason,
        grading_items=tuple(
            MillGradingItemEntity(
                id=g.id,
                grading_category=g.grading_category,
                deduction_type=MillGradingDeductionType(g.deduction_type),
                deduction_value=g.deduction_value,
                calculation_basis=g.calculation_basis,
                is_simulation=g.is_simulation,
                notes=g.notes,
            )
            for g in row.grading_items
        ),
        created_at=row.created_at,
    )


def _require_ticket(entity: MillWeighingTicketEntity | None) -> MillWeighingTicketEntity:
    if entity is None:
        raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
    return entity


async def _has_issued_invoice(session: AsyncSession, delivery_order_id: UUID) -> bool:
    return (
        await session.execute(
            select(InvoiceModel.id)
            .join(
                ReconciliationCaseModel,
                ReconciliationCaseModel.id == InvoiceModel.reconciliation_case_id,
            )
            .where(
                ReconciliationCaseModel.delivery_order_id == delivery_order_id,
                InvoiceModel.status == "ISSUED",
            )
            .limit(1)
        )
    ).scalar_one_or_none() is not None


async def _fetch_ticket(session: AsyncSession, ticket_id: UUID) -> MillWeighingTicketEntity | None:
    row = (
        await session.execute(
            select(MillWeighingTicketModel)
            .options(selectinload(MillWeighingTicketModel.grading_items))
            .where(MillWeighingTicketModel.id == ticket_id)
        )
    ).scalar_one_or_none()
    return _to_ticket_entity(row) if row is not None else None


class SqlAlchemyMillWeighingRepository:
    """PostgreSQL implementation of MillWeighingRepositoryPort."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def list_tickets(
        self,
        *,
        allowed_mill_ids: set[UUID] | None,
        allowed_cooperative_ids: set[UUID] | None,
        status_filter: MillTicketStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[MillWeighingTicketEntity], int]:
        filters: list[Any] = [MillWeighingTicketModel.is_current.is_(True)]
        if allowed_mill_ids is not None:
            if not allowed_mill_ids:
                return [], 0
            filters.append(MillWeighingTicketModel.mill_id.in_(allowed_mill_ids))
        if allowed_cooperative_ids is not None:
            if not allowed_cooperative_ids:
                return [], 0
            do_subq = select(DeliveryOrderModel.id).where(
                DeliveryOrderModel.cooperative_id.in_(allowed_cooperative_ids)
            )
            filters.append(MillWeighingTicketModel.delivery_order_id.in_(do_subq))
        if status_filter is not None:
            filters.append(MillWeighingTicketModel.status == status_filter.value)

        async with self._session_factory() as session:
            total = int(
                (
                    await session.execute(
                        select(func.count()).select_from(MillWeighingTicketModel).where(*filters)
                    )
                ).scalar_one()
            )
            rows = (
                (
                    await session.execute(
                        select(MillWeighingTicketModel)
                        .options(selectinload(MillWeighingTicketModel.grading_items))
                        .where(*filters)
                        .order_by(
                            MillWeighingTicketModel.weighed_at.desc(),
                            MillWeighingTicketModel.id.desc(),
                        )
                        .offset((page - 1) * page_size)
                        .limit(page_size)
                    )
                )
                .scalars()
                .all()
            )
            return [_to_ticket_entity(r) for r in rows], total

    async def get_ticket_by_id(self, ticket_id: UUID) -> MillWeighingTicketEntity | None:
        async with self._session_factory() as session:
            return await _fetch_ticket(session, ticket_id)

    async def get_ticket_coop_id(self, ticket_id: UUID) -> UUID | None:
        async with self._session_factory() as session:
            return (
                await session.execute(
                    select(DeliveryOrderModel.cooperative_id)
                    .join(
                        MillWeighingTicketModel,
                        MillWeighingTicketModel.delivery_order_id == DeliveryOrderModel.id,
                    )
                    .where(MillWeighingTicketModel.id == ticket_id)
                )
            ).scalar_one_or_none()

    async def create_ticket(
        self,
        *,
        delivery_order_id: UUID,
        ticket_number: str,
        gross_weight_kg: Decimal,
        tare_weight_kg: Decimal,
        net_weight_kg: Decimal,
        weighed_at: datetime,
        proof_file_id: UUID | None,
        grading_items: list[ValidatedMillGradingItem],
        allowed_mill_ids: set[UUID] | None,
        actor_id: UUID,
        idempotency_record_id: UUID,
    ) -> MillWeighingTicketEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                do = (
                    await session.execute(
                        select(DeliveryOrderModel)
                        .where(DeliveryOrderModel.id == delivery_order_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if do is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                if allowed_mill_ids is not None and do.mill_id not in allowed_mill_ids:
                    raise AppError(ErrorCode.MILL_EDO_MILL_MISMATCH)

                existing_current = (
                    await session.execute(
                        select(MillWeighingTicketModel).where(
                            MillWeighingTicketModel.delivery_order_id == delivery_order_id,
                            MillWeighingTicketModel.is_current.is_(True),
                        )
                    )
                ).scalar_one_or_none()
                if existing_current is not None:
                    raise AppError(
                        ErrorCode.MILL_DUPLICATE_TICKET,
                        details={"ticket_number": existing_current.ticket_number},
                    )
                if do.status != DeliveryOrderStatus.ARRIVED.value:
                    raise AppError(
                        ErrorCode.MILL_EDO_NOT_ELIGIBLE,
                        details={"delivery_status": do.status},
                    )

                if proof_file_id is not None:
                    proof = await session.get(FileAssetModel, proof_file_id)
                    if proof is None:
                        raise AppError(
                            ErrorCode.VAL_INVALID_FORMAT,
                            details=[
                                {
                                    "field": "proof_file_id",
                                    "reason": "Referensi bukti file tidak ditemukan.",
                                    "code": ErrorCode.VAL_INVALID_FORMAT.value,
                                }
                            ],
                        )

                ticket = MillWeighingTicketModel(
                    id=uuid4(),
                    delivery_order_id=delivery_order_id,
                    mill_id=do.mill_id,
                    ticket_number=ticket_number,
                    revision_number=1,
                    previous_ticket_id=None,
                    gross_weight_kg=gross_weight_kg,
                    tare_weight_kg=tare_weight_kg,
                    net_weight_kg=net_weight_kg,
                    weighed_at=weighed_at.astimezone(UTC),
                    verified_at=None,
                    verified_by=None,
                    is_current=True,
                    status=MillTicketStatus.SUBMITTED.value,
                    proof_file_id=proof_file_id,
                    correction_reason=None,
                    created_by=actor_id,
                    created_at=now,
                )
                session.add(ticket)
                try:
                    await session.flush()
                except IntegrityError as exc:
                    raise AppError(
                        ErrorCode.MILL_DUPLICATE_TICKET,
                        details={"ticket_number": ticket_number},
                    ) from exc

                for g in grading_items:
                    session.add(
                        MillGradingItemModel(
                            id=uuid4(),
                            mill_ticket_id=ticket.id,
                            grading_category=g.grading_category,
                            deduction_type=g.deduction_type.value,
                            deduction_value=g.deduction_value,
                            calculation_basis=g.calculation_basis,
                            is_simulation=True,
                            notes=g.notes,
                            created_at=now,
                        )
                    )

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="MILL_TICKET_CREATED",
                        module="mill_weighing",
                        resource_type="mill_weighing_tickets",
                        resource_id=str(ticket.id),
                        previous_state=None,
                        new_state={
                            "delivery_order_id": str(delivery_order_id),
                            "ticket_number": ticket_number,
                            "net_weight_kg": f"{net_weight_kg:.3f}",
                            "status": MillTicketStatus.SUBMITTED.value,
                        },
                        reason=None,
                    ),
                )
                await complete_idempotency_slot(
                    session,
                    record_id=idempotency_record_id,
                    response_reference=ticket.id,
                )
                ticket_id = ticket.id

        async with self._session_factory() as read_session:
            return _require_ticket(await _fetch_ticket(read_session, ticket_id))

    async def revise_ticket(
        self,
        *,
        ticket_id: UUID,
        gross_weight_kg: Decimal,
        tare_weight_kg: Decimal,
        net_weight_kg: Decimal,
        proof_file_id: UUID | None,
        correction_reason: str,
        allowed_mill_ids: set[UUID] | None,
        actor_id: UUID,
    ) -> MillWeighingTicketEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                cur = (
                    await session.execute(
                        select(MillWeighingTicketModel)
                        .where(MillWeighingTicketModel.id == ticket_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if cur is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                if allowed_mill_ids is not None and cur.mill_id not in allowed_mill_ids:
                    raise AppError(ErrorCode.MILL_EDO_MILL_MISMATCH)

                do = (
                    await session.execute(
                        select(DeliveryOrderModel)
                        .where(DeliveryOrderModel.id == cur.delivery_order_id)
                        .with_for_update()
                    )
                ).scalar_one()

                assert_ticket_can_revise(
                    is_current=cur.is_current,
                    do_completed=(do.status == DeliveryOrderStatus.COMPLETED.value),
                )
                if await _has_issued_invoice(session, do.id):
                    raise AppError(ErrorCode.MILL_TICKET_ALREADY_FINAL)

                if proof_file_id is not None:
                    proof = await session.get(FileAssetModel, proof_file_id)
                    if proof is None:
                        raise AppError(ErrorCode.VAL_INVALID_FORMAT)

                cur.is_current = False
                await session.flush()

                new_ticket = MillWeighingTicketModel(
                    id=uuid4(),
                    delivery_order_id=cur.delivery_order_id,
                    mill_id=cur.mill_id,
                    ticket_number=cur.ticket_number,
                    revision_number=cur.revision_number + 1,
                    previous_ticket_id=cur.id,
                    gross_weight_kg=gross_weight_kg,
                    tare_weight_kg=tare_weight_kg,
                    net_weight_kg=net_weight_kg,
                    weighed_at=cur.weighed_at,
                    verified_at=None,
                    verified_by=None,
                    is_current=True,
                    status=MillTicketStatus.SUBMITTED.value,
                    proof_file_id=proof_file_id if proof_file_id is not None else cur.proof_file_id,
                    correction_reason=correction_reason,
                    created_by=actor_id,
                    created_at=now,
                )
                session.add(new_ticket)
                await session.flush()

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="MILL_TICKET_REVISED",
                        module="mill_weighing",
                        resource_type="mill_weighing_tickets",
                        resource_id=str(new_ticket.id),
                        previous_state={
                            "ticket_id": str(cur.id),
                            "revision_number": cur.revision_number,
                            "net_weight_kg": f"{cur.net_weight_kg:.3f}",
                        },
                        new_state={
                            "revision_number": new_ticket.revision_number,
                            "net_weight_kg": f"{net_weight_kg:.3f}",
                        },
                        reason=correction_reason,
                    ),
                )
                new_id = new_ticket.id

        async with self._session_factory() as read_session:
            return _require_ticket(await _fetch_ticket(read_session, new_id))

    async def verify_ticket(
        self,
        *,
        ticket_id: UUID,
        allowed_mill_ids: set[UUID] | None,
        actor_id: UUID,
    ) -> MillWeighingTicketEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                ticket = (
                    await session.execute(
                        select(MillWeighingTicketModel)
                        .where(MillWeighingTicketModel.id == ticket_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if ticket is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                if allowed_mill_ids is not None and ticket.mill_id not in allowed_mill_ids:
                    raise AppError(ErrorCode.MILL_EDO_MILL_MISMATCH)

                do = (
                    await session.execute(
                        select(DeliveryOrderModel)
                        .where(DeliveryOrderModel.id == ticket.delivery_order_id)
                        .with_for_update()
                    )
                ).scalar_one()

                assert_ticket_can_verify(
                    is_current=ticket.is_current,
                    status=MillTicketStatus(ticket.status),
                    do_completed=(do.status == DeliveryOrderStatus.COMPLETED.value),
                )
                if await _has_issued_invoice(session, do.id):
                    raise AppError(ErrorCode.MILL_TICKET_ALREADY_FINAL)

                ticket.status = MillTicketStatus.VERIFIED.value
                ticket.verified_at = now
                ticket.verified_by = actor_id

                if do.status == DeliveryOrderStatus.ARRIVED.value:
                    do.status = DeliveryOrderStatus.RECEIVED.value
                    do.version += 1
                    do.updated_at = now
                    session.add(
                        DeliveryStatusEventModel(
                            id=uuid4(),
                            delivery_order_id=do.id,
                            previous_status=DeliveryOrderStatus.ARRIVED.value,
                            new_status=DeliveryOrderStatus.RECEIVED.value,
                            actor_id=actor_id,
                            event_time=now,
                            reason=f"Tiket timbang PKS {ticket.ticket_number} terverifikasi.",
                            metadata_json=None,
                        )
                    )
                    await consume_quota_reservation_in_tx(
                        session,
                        delivery_order_id=do.id,
                        consumed_weight_kg=ticket.net_weight_kg,
                        actor_id=actor_id,
                    )

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="MILL_TICKET_VERIFIED",
                        module="mill_weighing",
                        resource_type="mill_weighing_tickets",
                        resource_id=str(ticket.id),
                        previous_state={"status": MillTicketStatus.SUBMITTED.value},
                        new_state={
                            "status": MillTicketStatus.VERIFIED.value,
                            "delivery_order_status": do.status,
                            "net_weight_kg": f"{ticket.net_weight_kg:.3f}",
                        },
                        reason=None,
                    ),
                )

        async with self._session_factory() as read_session:
            return _require_ticket(await _fetch_ticket(read_session, ticket_id))
