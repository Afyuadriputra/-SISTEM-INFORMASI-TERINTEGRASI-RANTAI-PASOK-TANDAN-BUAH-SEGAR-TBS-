"""PostgreSQL repository implementation for Logistics, atomic e-DO issue, SM-05 & QR."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import func, or_, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from app.core.audit import AuditRecordInput, append_audit_event
from app.core.exceptions import AppError, ErrorCode
from app.core.idempotency import complete_idempotency_slot
from app.modules.contracts.domain.entities import ContractStatus
from app.modules.contracts.infrastructure.models import TradeContractModel
from app.modules.contracts.infrastructure.quota_ops import (
    release_quota_reservation_in_tx,
    reserve_quota_in_tx,
)
from app.modules.logistics.domain.entities import (
    AllocationStatus,
    DeliveryOrderEntity,
    DeliveryOrderLineEntity,
    DeliveryOrderStatus,
    DeliveryStatusEventEntity,
)
from app.modules.logistics.domain.rules import (
    assert_can_cancel_edo,
    assert_can_issue_edo,
    assert_can_transition_edo,
    generate_edo_qr_token_and_hash,
)
from app.modules.logistics.infrastructure.models import (
    DeliveryOrderLineModel,
    DeliveryOrderModel,
    DeliveryStatusEventModel,
)
from app.modules.master_data.infrastructure.models import (
    DriverModel,
    FarmerModel,
    MillModel,
    VehicleModel,
)
from app.modules.tbs_receiving.domain.entities import ReceiptStatus
from app.modules.tbs_receiving.infrastructure.models import (
    ReceiptWeighingRevisionModel,
    TbsReceiptModel,
)


def _require_do(entity: DeliveryOrderEntity | None) -> DeliveryOrderEntity:
    if entity is None:
        raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
    return entity


async def _fetch_do_entity(
    session: AsyncSession,
    delivery_order_id: UUID,
    *,
    filter_farmer_ids: set[UUID] | None = None,
) -> DeliveryOrderEntity | None:
    stmt = (
        select(
            DeliveryOrderModel,
            MillModel.mill_name,
            VehicleModel.plate_number,
            DriverModel.full_name,
        )
        .join(MillModel, MillModel.id == DeliveryOrderModel.mill_id)
        .join(VehicleModel, VehicleModel.id == DeliveryOrderModel.vehicle_id)
        .join(DriverModel, DriverModel.id == DeliveryOrderModel.driver_id)
        .options(
            selectinload(DeliveryOrderModel.lines),
            selectinload(DeliveryOrderModel.status_events),
        )
        .where(DeliveryOrderModel.id == delivery_order_id)
    )
    row_tuple = (await session.execute(stmt)).first()
    if row_tuple is None:
        return None
    do_row, mill_name, plate_number, driver_name = row_tuple

    line_receipt_ids = [ln.receipt_id for ln in do_row.lines]
    receipt_meta: dict[UUID, tuple[str, UUID, str]] = {}
    if line_receipt_ids:
        rm_rows = (
            await session.execute(
                select(
                    TbsReceiptModel.id,
                    TbsReceiptModel.receipt_number,
                    TbsReceiptModel.farmer_id,
                    FarmerModel.full_name,
                )
                .join(FarmerModel, FarmerModel.id == TbsReceiptModel.farmer_id)
                .where(TbsReceiptModel.id.in_(line_receipt_ids))
            )
        ).all()
        receipt_meta = {rid: (rnum, fid, fname) for rid, rnum, fid, fname in rm_rows}

    line_entities: list[DeliveryOrderLineEntity] = []
    for ln in do_row.lines:
        rnum, fid, fname = receipt_meta[ln.receipt_id]
        if filter_farmer_ids is not None and fid not in filter_farmer_ids:
            continue
        line_entities.append(
            DeliveryOrderLineEntity(
                id=ln.id,
                receipt_id=ln.receipt_id,
                receipt_number=rnum,
                farmer_id=fid,
                farmer_name=fname,
                origin_weight_snapshot_kg=ln.origin_weight_snapshot_kg,
                allocation_status=AllocationStatus(ln.allocation_status),
            )
        )

    event_entities = tuple(
        DeliveryStatusEventEntity(
            id=ev.id,
            previous_status=(
                DeliveryOrderStatus(ev.previous_status) if ev.previous_status else None
            ),
            new_status=DeliveryOrderStatus(ev.new_status),
            actor_id=ev.actor_id,
            event_time=ev.event_time,
            reason=ev.reason,
        )
        for ev in sorted(do_row.status_events, key=lambda e: e.event_time)
    )

    return DeliveryOrderEntity(
        id=do_row.id,
        delivery_order_number=do_row.delivery_order_number,
        cooperative_id=do_row.cooperative_id,
        mill_id=do_row.mill_id,
        mill_name=mill_name,
        contract_id=do_row.contract_id,
        vehicle_id=do_row.vehicle_id,
        vehicle_plate=plate_number,
        driver_id=do_row.driver_id,
        driver_name=driver_name,
        total_origin_weight_kg=do_row.total_origin_weight_kg,
        status=DeliveryOrderStatus(do_row.status),
        qr_verification_token=do_row.qr_verification_token,
        lines=tuple(line_entities),
        status_events=event_entities,
        issued_at=do_row.issued_at,
        departed_at=do_row.departed_at,
        arrived_at=do_row.arrived_at,
        completed_at=do_row.completed_at,
        version=do_row.version,
        created_at=do_row.created_at,
    )


class SqlAlchemyLogisticsRepository:
    """PostgreSQL implementation of LogisticsRepositoryPort."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def list_delivery_orders(
        self,
        *,
        allowed_farmer_ids: set[UUID] | None,
        allowed_cooperative_ids: set[UUID] | None,
        allowed_mill_ids: set[UUID] | None,
        status_filter: DeliveryOrderStatus | None,
        mill_id: UUID | None,
        page: int,
        page_size: int,
    ) -> tuple[list[DeliveryOrderEntity], int]:
        filters: list[Any] = []
        if allowed_cooperative_ids is not None:
            if not allowed_cooperative_ids:
                return [], 0
            filters.append(DeliveryOrderModel.cooperative_id.in_(allowed_cooperative_ids))
        if allowed_mill_ids is not None:
            if not allowed_mill_ids:
                return [], 0
            filters.append(DeliveryOrderModel.mill_id.in_(allowed_mill_ids))
        if allowed_farmer_ids is not None:
            if not allowed_farmer_ids:
                return [], 0
            subq = (
                select(DeliveryOrderLineModel.delivery_order_id)
                .join(TbsReceiptModel, TbsReceiptModel.id == DeliveryOrderLineModel.receipt_id)
                .where(TbsReceiptModel.farmer_id.in_(allowed_farmer_ids))
            )
            filters.append(DeliveryOrderModel.id.in_(subq))
        if status_filter is not None:
            filters.append(DeliveryOrderModel.status == status_filter.value)
        if mill_id is not None:
            filters.append(DeliveryOrderModel.mill_id == mill_id)

        async with self._session_factory() as session:
            total = int(
                (
                    await session.execute(
                        select(func.count()).select_from(DeliveryOrderModel).where(*filters)
                    )
                ).scalar_one()
            )
            ids = (
                (
                    await session.execute(
                        select(DeliveryOrderModel.id)
                        .where(*filters)
                        .order_by(
                            DeliveryOrderModel.created_at.desc(),
                            DeliveryOrderModel.id.desc(),
                        )
                        .offset((page - 1) * page_size)
                        .limit(page_size)
                    )
                )
                .scalars()
                .all()
            )
            results: list[DeliveryOrderEntity] = []
            for do_id in ids:
                ent = await _fetch_do_entity(session, do_id, filter_farmer_ids=allowed_farmer_ids)
                if ent is not None:
                    results.append(ent)
            return results, total

    async def get_delivery_order_by_id(
        self,
        delivery_order_id: UUID,
        *,
        filter_farmer_ids: set[UUID] | None = None,
    ) -> DeliveryOrderEntity | None:
        async with self._session_factory() as session:
            return await _fetch_do_entity(
                session, delivery_order_id, filter_farmer_ids=filter_farmer_ids
            )

    async def create_draft(
        self,
        *,
        mill_id: UUID,
        contract_id: UUID,
        vehicle_id: UUID,
        driver_id: UUID,
        receipt_ids: list[UUID],
        allowed_cooperative_ids: set[UUID] | None,
        actor_id: UUID,
    ) -> DeliveryOrderEntity:
        now = datetime.now(UTC)
        sorted_receipt_ids = sorted(receipt_ids)
        async with self._session_factory() as session:
            async with session.begin():
                mill = await session.get(MillModel, mill_id)
                contract = await session.get(TradeContractModel, contract_id)
                vehicle = await session.get(VehicleModel, vehicle_id)
                driver = await session.get(DriverModel, driver_id)
                if mill is None or contract is None or vehicle is None or driver is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                if (
                    mill.partnership_status != "ACTIVE"
                    or vehicle.status != "ACTIVE"
                    or driver.status != "ACTIVE"
                ):
                    raise AppError(ErrorCode.VAL_INVALID_FORMAT)
                if contract.mill_id != mill_id:
                    raise AppError(
                        ErrorCode.VAL_INVALID_FORMAT,
                        details=[
                            {
                                "field": "contract_id",
                                "reason": "Kontrak niaga bukan untuk PKS tujuan tersebut.",
                                "code": ErrorCode.VAL_INVALID_FORMAT.value,
                            }
                        ],
                    )
                if ContractStatus(contract.status) != ContractStatus.ACTIVE:
                    raise AppError(
                        ErrorCode.CONTRACT_NOT_ACTIVE,
                        details={"contract_status": contract.status},
                    )

                receipt_rows = (
                    (
                        await session.execute(
                            select(TbsReceiptModel)
                            .where(TbsReceiptModel.id.in_(sorted_receipt_ids))
                            .order_by(TbsReceiptModel.id.asc())
                            .with_for_update()
                        )
                    )
                    .scalars()
                    .all()
                )
                if len(receipt_rows) != len(sorted_receipt_ids):
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)

                coop_ids = {r.cooperative_id for r in receipt_rows}
                if len(coop_ids) != 1:
                    raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)
                coop_id = next(iter(coop_ids))
                if allowed_cooperative_ids is not None and coop_id not in allowed_cooperative_ids:
                    raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)

                existing_active = (
                    (
                        await session.execute(
                            select(DeliveryOrderLineModel.receipt_id).where(
                                DeliveryOrderLineModel.receipt_id.in_(sorted_receipt_ids),
                                DeliveryOrderLineModel.allocation_status == "ACTIVE",
                            )
                        )
                    )
                    .scalars()
                    .all()
                )
                if existing_active:
                    raise AppError(
                        ErrorCode.LOG_DELIVERY_ALREADY_ASSIGNED,
                        details={"conflicting_receipt_ids": [str(rid) for rid in existing_active]},
                    )

                not_validated = [
                    r for r in receipt_rows if ReceiptStatus(r.status) != ReceiptStatus.VALIDATED
                ]
                if not_validated:
                    locked = [
                        str(r.id)
                        for r in not_validated
                        if r.status in ("ALLOCATED", "SHIPPED", "CLOSED")
                    ]
                    if locked:
                        raise AppError(
                            ErrorCode.LOG_DELIVERY_ALREADY_ASSIGNED,
                            details={"conflicting_receipt_ids": locked},
                        )
                    raise AppError(
                        ErrorCode.TBS_INVALID_STATE_TRANSITION,
                        details={"current_status": not_validated[0].status},
                    )

                current_weighings = (
                    (
                        await session.execute(
                            select(ReceiptWeighingRevisionModel).where(
                                ReceiptWeighingRevisionModel.receipt_id.in_(sorted_receipt_ids),
                                ReceiptWeighingRevisionModel.is_current.is_(True),
                            )
                        )
                    )
                    .scalars()
                    .all()
                )
                weighing_by_receipt = {w.receipt_id: w for w in current_weighings}
                if len(weighing_by_receipt) != len(sorted_receipt_ids):
                    raise AppError(
                        ErrorCode.TBS_INVALID_STATE_TRANSITION,
                        details={"current_status": "DRAFT"},
                    )

                total_weight = sum(
                    (weighing_by_receipt[r.id].net_weight_kg for r in receipt_rows),
                    start=Decimal("0.000"),
                ).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

                seq_val = int(
                    (
                        await session.execute(text("SELECT nextval('delivery_order_seq')"))
                    ).scalar_one()
                )
                do_number = f"EDO-{now.strftime('%Y-%m%d')}-{seq_val:04d}-DRAFT"

                do = DeliveryOrderModel(
                    id=uuid4(),
                    delivery_order_number=do_number,
                    cooperative_id=coop_id,
                    mill_id=mill_id,
                    contract_id=contract_id,
                    vehicle_id=vehicle_id,
                    driver_id=driver_id,
                    total_origin_weight_kg=total_weight,
                    status=DeliveryOrderStatus.DRAFT.value,
                    issued_at=None,
                    departed_at=None,
                    arrived_at=None,
                    completed_at=None,
                    qr_verification_token=None,
                    qr_reference_hash=None,
                    created_by=actor_id,
                    version=1,
                    created_at=now,
                    updated_at=now,
                )
                session.add(do)
                await session.flush()

                for r in receipt_rows:
                    session.add(
                        DeliveryOrderLineModel(
                            id=uuid4(),
                            delivery_order_id=do.id,
                            receipt_id=r.id,
                            origin_weight_snapshot_kg=weighing_by_receipt[r.id].net_weight_kg,
                            allocation_status=AllocationStatus.ACTIVE.value,
                            created_at=now,
                            released_at=None,
                        )
                    )
                session.add(
                    DeliveryStatusEventModel(
                        id=uuid4(),
                        delivery_order_id=do.id,
                        previous_status=None,
                        new_status=DeliveryOrderStatus.DRAFT.value,
                        actor_id=actor_id,
                        event_time=now,
                        reason=None,
                        metadata_json=None,
                    )
                )
                try:
                    await session.flush()
                except IntegrityError as exc:
                    raise AppError(
                        ErrorCode.LOG_DELIVERY_ALREADY_ASSIGNED,
                        details={
                            "conflicting_receipt_ids": [str(rid) for rid in sorted_receipt_ids]
                        },
                    ) from exc

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="DELIVERY_ORDER_DRAFT_CREATED",
                        module="logistics",
                        resource_type="delivery_orders",
                        resource_id=str(do.id),
                        previous_state=None,
                        new_state={
                            "delivery_order_number": do.delivery_order_number,
                            "total_origin_weight_kg": f"{total_weight:.3f}",
                            "lines_count": len(receipt_rows),
                        },
                        reason=None,
                    ),
                )
                do_id = do.id

        async with self._session_factory() as read_session:
            return _require_do(await _fetch_do_entity(read_session, do_id))

    async def issue_delivery_order(
        self,
        *,
        delivery_order_id: UUID,
        expected_version: int,
        allowed_cooperative_ids: set[UUID] | None,
        actor_id: UUID,
        idempotency_record_id: UUID,
    ) -> DeliveryOrderEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                do = (
                    await session.execute(
                        select(DeliveryOrderModel)
                        .where(DeliveryOrderModel.id == delivery_order_id)
                        .options(selectinload(DeliveryOrderModel.lines))
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if do is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                if (
                    allowed_cooperative_ids is not None
                    and do.cooperative_id not in allowed_cooperative_ids
                ):
                    raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)

                assert_can_issue_edo(
                    current_status=DeliveryOrderStatus(do.status),
                    expected_version=expected_version,
                    actual_version=do.version,
                )

                active_lines = [ln for ln in do.lines if ln.allocation_status == "ACTIVE"]
                if not active_lines:
                    raise AppError(
                        ErrorCode.LOG_INVALID_STATE_TRANSITION,
                        details={"current_status": do.status, "requested_status": "READY"},
                    )
                receipt_ids = sorted(ln.receipt_id for ln in active_lines)
                receipts = (
                    (
                        await session.execute(
                            select(TbsReceiptModel)
                            .where(TbsReceiptModel.id.in_(receipt_ids))
                            .order_by(TbsReceiptModel.id.asc())
                            .with_for_update()
                        )
                    )
                    .scalars()
                    .all()
                )
                non_validated = [
                    str(r.id)
                    for r in receipts
                    if ReceiptStatus(r.status) != ReceiptStatus.VALIDATED
                ]
                if non_validated:
                    raise AppError(
                        ErrorCode.LOG_DELIVERY_ALREADY_ASSIGNED,
                        details={"conflicting_receipt_ids": non_validated},
                    )

                await reserve_quota_in_tx(
                    session,
                    contract_id=do.contract_id,
                    quota_period_id=None,
                    delivery_order_id=do.id,
                    reserved_weight_kg=do.total_origin_weight_kg,
                    as_of_date=now.date(),
                    actor_id=actor_id,
                )

                for r in receipts:
                    r.status = ReceiptStatus.ALLOCATED.value
                    r.version += 1
                    r.updated_at = now

                final_number = do.delivery_order_number.removesuffix("-DRAFT")
                token, qr_hash = generate_edo_qr_token_and_hash(delivery_order_number=final_number)
                do.delivery_order_number = final_number
                do.status = DeliveryOrderStatus.READY.value
                do.issued_at = now
                do.qr_verification_token = token
                do.qr_reference_hash = qr_hash
                do.version += 1
                do.updated_at = now

                session.add(
                    DeliveryStatusEventModel(
                        id=uuid4(),
                        delivery_order_id=do.id,
                        previous_status=DeliveryOrderStatus.DRAFT.value,
                        new_status=DeliveryOrderStatus.READY.value,
                        actor_id=actor_id,
                        event_time=now,
                        reason="Penerbitan e-DO dan penguncian muatan serta kuota.",
                        metadata_json=None,
                    )
                )
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="DELIVERY_ORDER_ISSUED",
                        module="logistics",
                        resource_type="delivery_orders",
                        resource_id=str(do.id),
                        previous_state={"status": DeliveryOrderStatus.DRAFT.value},
                        new_state={
                            "delivery_order_number": final_number,
                            "status": DeliveryOrderStatus.READY.value,
                            "total_origin_weight_kg": f"{do.total_origin_weight_kg:.3f}",
                        },
                        reason=None,
                    ),
                )
                await complete_idempotency_slot(
                    session,
                    record_id=idempotency_record_id,
                    response_reference=do.id,
                )

        async with self._session_factory() as read_session:
            return _require_do(await _fetch_do_entity(read_session, delivery_order_id))

    async def transition_status(
        self,
        *,
        delivery_order_id: UUID,
        target_status: DeliveryOrderStatus,
        reason: str | None,
        expected_version: int,
        allowed_cooperative_ids: set[UUID] | None,
        has_global_ops: bool,
        actor_id: UUID,
    ) -> DeliveryOrderEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                do = (
                    await session.execute(
                        select(DeliveryOrderModel)
                        .where(DeliveryOrderModel.id == delivery_order_id)
                        .options(selectinload(DeliveryOrderModel.lines))
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if do is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                if (
                    allowed_cooperative_ids is not None
                    and do.cooperative_id not in allowed_cooperative_ids
                ):
                    raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)

                current = DeliveryOrderStatus(do.status)
                assert_can_transition_edo(
                    current_status=current,
                    target_status=target_status,
                    expected_version=expected_version,
                    actual_version=do.version,
                    has_global_ops=has_global_ops,
                )

                receipt_ids = sorted(
                    ln.receipt_id for ln in do.lines if ln.allocation_status == "ACTIVE"
                )
                if receipt_ids:
                    receipts = (
                        (
                            await session.execute(
                                select(TbsReceiptModel)
                                .where(TbsReceiptModel.id.in_(receipt_ids))
                                .order_by(TbsReceiptModel.id.asc())
                                .with_for_update()
                            )
                        )
                        .scalars()
                        .all()
                    )
                    next_receipt_status = (
                        ReceiptStatus.SHIPPED.value
                        if target_status == DeliveryOrderStatus.IN_TRANSIT
                        else ReceiptStatus.CLOSED.value
                    )
                    for r in receipts:
                        r.status = next_receipt_status
                        r.version += 1
                        r.updated_at = now

                do.status = target_status.value
                if target_status == DeliveryOrderStatus.IN_TRANSIT:
                    do.departed_at = now
                elif target_status == DeliveryOrderStatus.COMPLETED:
                    do.completed_at = now
                do.version += 1
                do.updated_at = now

                session.add(
                    DeliveryStatusEventModel(
                        id=uuid4(),
                        delivery_order_id=do.id,
                        previous_status=current.value,
                        new_status=target_status.value,
                        actor_id=actor_id,
                        event_time=now,
                        reason=reason,
                        metadata_json=None,
                    )
                )
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="DELIVERY_ORDER_TRANSITIONED",
                        module="logistics",
                        resource_type="delivery_orders",
                        resource_id=str(do.id),
                        previous_state={"status": current.value},
                        new_state={"status": target_status.value},
                        reason=reason,
                    ),
                )

        async with self._session_factory() as read_session:
            return _require_do(await _fetch_do_entity(read_session, delivery_order_id))

    async def cancel_delivery_order(
        self,
        *,
        delivery_order_id: UUID,
        reason: str,
        expected_version: int,
        allowed_cooperative_ids: set[UUID] | None,
        has_global_ops: bool,
        actor_id: UUID,
    ) -> DeliveryOrderEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                do = (
                    await session.execute(
                        select(DeliveryOrderModel)
                        .where(DeliveryOrderModel.id == delivery_order_id)
                        .options(selectinload(DeliveryOrderModel.lines))
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if do is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                if (
                    allowed_cooperative_ids is not None
                    and do.cooperative_id not in allowed_cooperative_ids
                ):
                    raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)

                current = DeliveryOrderStatus(do.status)
                assert_can_cancel_edo(
                    current_status=current,
                    expected_version=expected_version,
                    actual_version=do.version,
                    has_global_ops=has_global_ops,
                )

                active_lines = [ln for ln in do.lines if ln.allocation_status == "ACTIVE"]
                for ln in active_lines:
                    ln.allocation_status = AllocationStatus.RELEASED.value
                    ln.released_at = now

                receipt_ids = sorted(ln.receipt_id for ln in active_lines)
                if receipt_ids and current != DeliveryOrderStatus.DRAFT:
                    receipts = (
                        (
                            await session.execute(
                                select(TbsReceiptModel)
                                .where(TbsReceiptModel.id.in_(receipt_ids))
                                .order_by(TbsReceiptModel.id.asc())
                                .with_for_update()
                            )
                        )
                        .scalars()
                        .all()
                    )
                    for r in receipts:
                        if r.status in (ReceiptStatus.ALLOCATED.value, ReceiptStatus.SHIPPED.value):
                            r.status = ReceiptStatus.VALIDATED.value
                            r.version += 1
                            r.updated_at = now

                await release_quota_reservation_in_tx(
                    session,
                    delivery_order_id=do.id,
                    actor_id=actor_id,
                    reason=reason,
                )

                do.status = DeliveryOrderStatus.CANCELLED.value
                do.version += 1
                do.updated_at = now
                session.add(
                    DeliveryStatusEventModel(
                        id=uuid4(),
                        delivery_order_id=do.id,
                        previous_status=current.value,
                        new_status=DeliveryOrderStatus.CANCELLED.value,
                        actor_id=actor_id,
                        event_time=now,
                        reason=reason,
                        metadata_json=None,
                    )
                )
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="DELIVERY_ORDER_CANCELLED",
                        module="logistics",
                        resource_type="delivery_orders",
                        resource_id=str(do.id),
                        previous_state={"status": current.value},
                        new_state={"status": DeliveryOrderStatus.CANCELLED.value},
                        reason=reason,
                    ),
                )

        async with self._session_factory() as read_session:
            return _require_do(await _fetch_do_entity(read_session, delivery_order_id))

    async def verify_qr_arrival(
        self,
        *,
        qr_token_or_edo_number: str,
        observed_plate_number: str | None,
        allowed_mill_ids: set[UUID] | None,
        has_global_ops: bool,
        actor_id: UUID,
    ) -> DeliveryOrderEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                do = (
                    await session.execute(
                        select(DeliveryOrderModel)
                        .where(
                            or_(
                                DeliveryOrderModel.qr_verification_token == qr_token_or_edo_number,
                                DeliveryOrderModel.delivery_order_number == qr_token_or_edo_number,
                            )
                        )
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if do is None or do.status in (
                    DeliveryOrderStatus.DRAFT.value,
                    DeliveryOrderStatus.CANCELLED.value,
                ):
                    raise AppError(ErrorCode.LOG_QR_VERIFICATION_FAILED)

                if not has_global_ops:
                    if allowed_mill_ids is None or do.mill_id not in allowed_mill_ids:
                        raise AppError(ErrorCode.MILL_EDO_MILL_MISMATCH)

                current = DeliveryOrderStatus(do.status)
                if current != DeliveryOrderStatus.IN_TRANSIT:
                    raise AppError(
                        ErrorCode.LOG_INVALID_STATE_TRANSITION,
                        details={
                            "current_status": current.value,
                            "requested_status": DeliveryOrderStatus.ARRIVED.value,
                        },
                    )

                do.status = DeliveryOrderStatus.ARRIVED.value
                do.arrived_at = now
                do.version += 1
                do.updated_at = now
                session.add(
                    DeliveryStatusEventModel(
                        id=uuid4(),
                        delivery_order_id=do.id,
                        previous_status=current.value,
                        new_status=DeliveryOrderStatus.ARRIVED.value,
                        actor_id=actor_id,
                        event_time=now,
                        reason="Verifikasi QR kedatangan di gerbang PKS.",
                        metadata_json=(
                            {"observed_plate_number": observed_plate_number}
                            if observed_plate_number
                            else None
                        ),
                    )
                )
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="DELIVERY_ORDER_ARRIVAL_VERIFIED",
                        module="logistics",
                        resource_type="delivery_orders",
                        resource_id=str(do.id),
                        previous_state={"status": current.value},
                        new_state={"status": DeliveryOrderStatus.ARRIVED.value},
                        reason=observed_plate_number,
                    ),
                )
                do_id = do.id

        async with self._session_factory() as read_session:
            return _require_do(await _fetch_do_entity(read_session, do_id))
