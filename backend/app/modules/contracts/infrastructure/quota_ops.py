"""Atomic SQL row-locking operations on quota periods shared by Contracts, Logistics & Weighing."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import AuditRecordInput, append_audit_event
from app.core.exceptions import AppError, ErrorCode
from app.modules.contracts.domain.entities import (
    ContractStatus,
    QuotaPeriodEntity,
    QuotaPeriodStatus,
    QuotaReservationStatus,
)
from app.modules.contracts.domain.rules import assert_quota_reservable
from app.modules.contracts.infrastructure.models import (
    ContractQuotaPeriodModel,
    QuotaReservationModel,
    TradeContractModel,
)
from app.modules.master_data.infrastructure.models import MillModel


async def compute_period_usage(
    session: AsyncSession, *, period: ContractQuotaPeriodModel
) -> QuotaPeriodEntity:
    """Compute exact PostgreSQL consumed, active_reserved, and available quota in kg."""
    consumed = Decimal(
        (
            await session.execute(
                select(func.coalesce(func.sum(QuotaReservationModel.consumed_weight_kg), 0)).where(
                    QuotaReservationModel.quota_period_id == period.id,
                    QuotaReservationModel.status == QuotaReservationStatus.CONSUMED.value,
                )
            )
        ).scalar_one()
    ).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

    reserved = Decimal(
        (
            await session.execute(
                select(func.coalesce(func.sum(QuotaReservationModel.reserved_weight_kg), 0)).where(
                    QuotaReservationModel.quota_period_id == period.id,
                    QuotaReservationModel.status == QuotaReservationStatus.RESERVED.value,
                )
            )
        ).scalar_one()
    ).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

    available = max(
        Decimal("0.000"),
        (period.quota_limit_kg - consumed - reserved).quantize(
            Decimal("0.001"), rounding=ROUND_HALF_UP
        ),
    )
    return QuotaPeriodEntity(
        id=period.id,
        contract_id=period.contract_id,
        period_start=period.period_start,
        period_end=period.period_end,
        quota_limit_kg=period.quota_limit_kg,
        consumed_weight_kg=consumed,
        active_reserved_kg=reserved,
        available_quota_kg=available,
        status=QuotaPeriodStatus(period.status),
    )


async def reserve_quota_in_tx(
    session: AsyncSession,
    *,
    contract_id: UUID,
    quota_period_id: UUID | None,
    delivery_order_id: UUID,
    reserved_weight_kg: Decimal,
    as_of_date: date,
    actor_id: UUID,
) -> QuotaReservationModel:
    """Acquire SELECT FOR UPDATE lock on contract + quota period and insert reservation safely."""
    contract = (
        await session.execute(
            select(TradeContractModel).where(TradeContractModel.id == contract_id).with_for_update()
        )
    ).scalar_one_or_none()
    if contract is None:
        raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)

    mill = (
        await session.execute(select(MillModel).where(MillModel.id == contract.mill_id))
    ).scalar_one()
    if mill.partnership_status != "ACTIVE":
        raise AppError(
            ErrorCode.CONTRACT_NOT_ACTIVE,
            details={"contract_status": contract.status},
        )

    period_stmt = select(ContractQuotaPeriodModel).where(
        ContractQuotaPeriodModel.contract_id == contract_id
    )
    if quota_period_id is not None:
        period_stmt = period_stmt.where(ContractQuotaPeriodModel.id == quota_period_id)
    else:
        period_stmt = period_stmt.where(
            ContractQuotaPeriodModel.status == QuotaPeriodStatus.ACTIVE.value,
            ContractQuotaPeriodModel.period_start <= as_of_date,
            ContractQuotaPeriodModel.period_end >= as_of_date,
        ).order_by(ContractQuotaPeriodModel.period_start.asc())

    periods = (await session.execute(period_stmt.with_for_update())).scalars().all()
    if not periods:
        if ContractStatus(contract.status) != ContractStatus.ACTIVE:
            raise AppError(
                ErrorCode.CONTRACT_NOT_ACTIVE,
                details={"contract_status": contract.status},
            )
        if as_of_date < contract.start_date or as_of_date > contract.end_date:
            raise AppError(
                ErrorCode.CONTRACT_EXPIRED,
                details={"contract_end_date": contract.end_date.isoformat()},
            )
        raise AppError(
            ErrorCode.CONTRACT_EXPIRED
            if quota_period_id is None
            else ErrorCode.SYS_RESOURCE_NOT_FOUND,
            details={"contract_end_date": contract.end_date.isoformat()},
        )

    period = periods[0]
    usage = await compute_period_usage(session, period=period)
    assert_quota_reservable(
        contract_status=ContractStatus(contract.status),
        contract_start=contract.start_date,
        contract_end=contract.end_date,
        period_status=QuotaPeriodStatus(period.status),
        period_start=period.period_start,
        period_end=period.period_end,
        available_quota_kg=usage.available_quota_kg,
        requested_weight_kg=reserved_weight_kg,
        as_of_date=as_of_date,
    )

    now = datetime.now(UTC)
    reservation = QuotaReservationModel(
        id=uuid4(),
        quota_period_id=period.id,
        delivery_order_id=delivery_order_id,
        reserved_weight_kg=reserved_weight_kg,
        consumed_weight_kg=Decimal("0.000"),
        status=QuotaReservationStatus.RESERVED.value,
        reserved_at=now,
        released_at=None,
        consumed_at=None,
    )
    session.add(reservation)
    try:
        await session.flush()
    except IntegrityError as exc:
        orig = getattr(exc, "orig", None)
        if getattr(orig, "sqlstate", None) == "23503":
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND) from exc
        raise AppError(ErrorCode.CONTRACT_CONCURRENT_CONFLICT) from exc

    append_audit_event(
        session,
        AuditRecordInput(
            actor_id=actor_id,
            event_type="QUOTA_RESERVED",
            module="contracts",
            resource_type="quota_reservations",
            resource_id=str(reservation.id),
            previous_state={"available_quota_kg": f"{usage.available_quota_kg:.3f}"},
            new_state={
                "quota_period_id": str(period.id),
                "delivery_order_id": str(delivery_order_id),
                "reserved_weight_kg": f"{reserved_weight_kg:.3f}",
                "status": QuotaReservationStatus.RESERVED.value,
            },
            reason=None,
        ),
    )
    return reservation


async def consume_quota_reservation_in_tx(
    session: AsyncSession,
    *,
    delivery_order_id: UUID,
    consumed_weight_kg: Decimal,
    actor_id: UUID,
) -> None:
    """Convert RESERVED -> CONSUMED once per e-DO; idempotently block double consumption."""
    res = (
        await session.execute(
            select(QuotaReservationModel)
            .where(
                QuotaReservationModel.delivery_order_id == delivery_order_id,
                QuotaReservationModel.status.in_(
                    [QuotaReservationStatus.RESERVED.value, QuotaReservationStatus.CONSUMED.value]
                ),
            )
            .with_for_update()
        )
    ).scalar_one_or_none()
    if res is None:
        return
    if res.status == QuotaReservationStatus.CONSUMED.value:
        raise AppError(ErrorCode.CONTRACT_CONCURRENT_CONFLICT)

    now = datetime.now(UTC)
    res.status = QuotaReservationStatus.CONSUMED.value
    res.consumed_weight_kg = consumed_weight_kg.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    res.consumed_at = now
    await session.flush()

    append_audit_event(
        session,
        AuditRecordInput(
            actor_id=actor_id,
            event_type="QUOTA_CONSUMED",
            module="contracts",
            resource_type="quota_reservations",
            resource_id=str(res.id),
            previous_state={"status": QuotaReservationStatus.RESERVED.value},
            new_state={
                "status": QuotaReservationStatus.CONSUMED.value,
                "consumed_weight_kg": f"{res.consumed_weight_kg:.3f}",
            },
            reason=None,
        ),
    )


async def release_quota_reservation_in_tx(
    session: AsyncSession,
    *,
    delivery_order_id: UUID,
    actor_id: UUID,
    reason: str | None,
) -> None:
    """Release active RESERVED quota reservation back to available pool upon e-DO cancellation."""
    res = (
        await session.execute(
            select(QuotaReservationModel)
            .where(
                QuotaReservationModel.delivery_order_id == delivery_order_id,
                QuotaReservationModel.status == QuotaReservationStatus.RESERVED.value,
            )
            .with_for_update()
        )
    ).scalar_one_or_none()
    if res is None:
        return

    now = datetime.now(UTC)
    res.status = QuotaReservationStatus.RELEASED.value
    res.released_at = now
    await session.flush()

    append_audit_event(
        session,
        AuditRecordInput(
            actor_id=actor_id,
            event_type="QUOTA_RELEASED",
            module="contracts",
            resource_type="quota_reservations",
            resource_id=str(res.id),
            previous_state={"status": QuotaReservationStatus.RESERVED.value},
            new_state={"status": QuotaReservationStatus.RELEASED.value},
            reason=reason,
        ),
    )
