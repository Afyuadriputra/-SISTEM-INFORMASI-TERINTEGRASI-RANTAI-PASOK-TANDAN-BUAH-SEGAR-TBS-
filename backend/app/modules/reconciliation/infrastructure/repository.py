"""PostgreSQL repository implementation for Reconciliation SM-07, Disputes SM-08 & Allocations."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Row, Select, delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from app.core.audit import AuditRecordInput, append_audit_event
from app.core.exceptions import AppError, ErrorCode
from app.core.idempotency import complete_idempotency_slot
from app.core.system_rules import RULE_RECONCILIATION_TOLERANCE_ID, SystemRuleVersionModel
from app.modules.contracts.domain.entities import PolicyClassification
from app.modules.contracts.infrastructure.models import TradeContractModel
from app.modules.files.infrastructure.models import FileAssetModel
from app.modules.logistics.domain.entities import DeliveryOrderStatus
from app.modules.logistics.infrastructure.models import (
    DeliveryOrderLineModel,
    DeliveryOrderModel,
)
from app.modules.master_data.infrastructure.models import FarmerModel
from app.modules.mill_weighing.domain.entities import MillTicketStatus
from app.modules.mill_weighing.infrastructure.models import MillWeighingTicketModel
from app.modules.reconciliation.domain.entities import (
    AllocationMode,
    AllocationRecordStatus,
    DisputeDecision,
    DisputeReviewEntity,
    FarmerSettlementAllocationEntity,
    ReconciliationCaseEntity,
    ReconciliationStatus,
    WeightBasis,
)
from app.modules.reconciliation.domain.rules import (
    AllocationLineInput,
    assert_can_resolve_dispute,
    assert_equivalent_weight_basis,
    compute_proportional_allocations,
    compute_reconciliation_diff,
    resolve_settlement_weight,
)
from app.modules.reconciliation.infrastructure.models import (
    DisputeReviewModel,
    FarmerSettlementAllocationModel,
    ReconciliationCaseModel,
)


def _require_case(entity: ReconciliationCaseEntity | None) -> ReconciliationCaseEntity:
    if entity is None:
        raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
    return entity


def _policy_from_rule_status(approval_status: str) -> PolicyClassification:
    if approval_status == "APPROVED":
        return PolicyClassification.CONFIRMED
    if approval_status == "PENDING_SOP":
        return PolicyClassification.PENDING_SOP
    return PolicyClassification.SIMULATION_ONLY


def _case_detail_stmt() -> Select[tuple[ReconciliationCaseModel, str]]:
    return (
        select(ReconciliationCaseModel, DeliveryOrderModel.delivery_order_number)
        .join(
            DeliveryOrderModel,
            DeliveryOrderModel.id == ReconciliationCaseModel.delivery_order_id,
        )
        .options(
            selectinload(ReconciliationCaseModel.dispute_reviews),
            selectinload(ReconciliationCaseModel.farmer_allocations),
        )
    )


def _map_case_row(
    row: ReconciliationCaseModel,
    do_number: str,
    farmer_names: dict[UUID, str],
) -> ReconciliationCaseEntity:
    reviews = tuple(
        DisputeReviewEntity(
            id=r.id,
            reviewer_id=r.reviewer_id,
            previous_status=ReconciliationStatus(r.previous_status),
            decision=DisputeDecision(r.decision),
            reason=r.reason,
            evidence_file_id=r.evidence_file_id,
            approved_by=r.approved_by,
            reviewed_at=r.reviewed_at,
        )
        for r in row.dispute_reviews
    )
    allocs = tuple(
        FarmerSettlementAllocationEntity(
            id=a.id,
            receipt_id=a.receipt_id,
            farmer_id=a.farmer_id,
            farmer_name=farmer_names.get(a.farmer_id, "Petani"),
            allocation_basis_weight_kg=a.allocation_basis_weight_kg,
            agreed_weight_kg=a.agreed_weight_kg,
            allocation_policy_version_id=a.allocation_policy_version_id,
            gross_amount=a.gross_amount,
            deduction_amount=a.deduction_amount,
            net_amount=a.net_amount,
            status=AllocationRecordStatus(a.status),
            policy_classification=PolicyClassification(a.policy_classification),
        )
        for a in row.farmer_allocations
    )
    return ReconciliationCaseEntity(
        id=row.id,
        delivery_order_id=row.delivery_order_id,
        delivery_order_number=do_number,
        mill_ticket_id=row.mill_ticket_id,
        revision_number=row.revision_number,
        origin_weight_kg=row.origin_weight_kg,
        mill_weight_kg=row.mill_weight_kg,
        difference_weight_kg=row.difference_weight_kg,
        difference_percent=row.difference_percent,
        tolerance_percent=row.tolerance_percent,
        rule_version_id=row.rule_version_id,
        tolerance_policy_classification=PolicyClassification(row.tolerance_policy_classification),
        is_negative_difference=row.is_negative_difference,
        status=ReconciliationStatus(row.status),
        is_current=row.is_current,
        agreed_settlement_weight_kg=row.agreed_settlement_weight_kg,
        calculated_at=row.calculated_at,
        resolved_at=row.resolved_at,
        dispute_reviews=reviews,
        farmer_allocations=allocs,
    )


async def _hydrate_case_rows(
    session: AsyncSession,
    row_tuples: Sequence[Row[tuple[ReconciliationCaseModel, str]]],
) -> list[ReconciliationCaseEntity]:
    if not row_tuples:
        return []
    farmer_ids = {a.farmer_id for row, _ in row_tuples for a in row.farmer_allocations}
    farmer_names: dict[UUID, str] = {}
    if farmer_ids:
        f_rows = (
            await session.execute(
                select(FarmerModel.id, FarmerModel.full_name).where(FarmerModel.id.in_(farmer_ids))
            )
        ).all()
        farmer_names = {fid: fname for fid, fname in f_rows}
    return [_map_case_row(row, do_number, farmer_names) for row, do_number in row_tuples]


async def _fetch_case_detail(
    session: AsyncSession, reconciliation_id: UUID
) -> ReconciliationCaseEntity | None:
    row_tuples = (
        await session.execute(
            _case_detail_stmt().where(ReconciliationCaseModel.id == reconciliation_id)
        )
    ).all()
    items = await _hydrate_case_rows(session, row_tuples)
    return items[0] if items else None


async def _load_active_tolerance_rule(
    session: AsyncSession,
) -> tuple[UUID, Decimal, PolicyClassification]:
    row = (
        (
            await session.execute(
                select(SystemRuleVersionModel)
                .where(
                    SystemRuleVersionModel.rule_code == "RECONCILIATION_TOLERANCE",
                    SystemRuleVersionModel.approval_status.in_(
                        ["SIMULATION_ONLY", "APPROVED", "PENDING_SOP"]
                    ),
                )
                .order_by(SystemRuleVersionModel.version_number.desc())
            )
        )
        .scalars()
        .first()
    )
    if row is None:
        return (
            RULE_RECONCILIATION_TOLERANCE_ID,
            Decimal("1.5000"),
            PolicyClassification.SIMULATION_ONLY,
        )
    raw_tol = str(
        row.rule_config.get("tolerance_percent")
        or row.rule_config.get("max_shrinkage_percent")
        or "1.5000"
    )
    return row.id, Decimal(raw_tol), _policy_from_rule_status(row.approval_status)


class SqlAlchemyReconciliationRepository:
    """PostgreSQL implementation of ReconciliationRepositoryPort."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def list_cases(
        self,
        *,
        allowed_cooperative_ids: set[UUID] | None,
        status_filter: ReconciliationStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ReconciliationCaseEntity], int]:
        filters: list[Any] = [ReconciliationCaseModel.is_current.is_(True)]
        if allowed_cooperative_ids is not None:
            if not allowed_cooperative_ids:
                return [], 0
            do_subq = select(DeliveryOrderModel.id).where(
                DeliveryOrderModel.cooperative_id.in_(allowed_cooperative_ids)
            )
            filters.append(ReconciliationCaseModel.delivery_order_id.in_(do_subq))
        if status_filter is not None:
            filters.append(ReconciliationCaseModel.status == status_filter.value)

        async with self._session_factory() as session:
            total = int(
                (
                    await session.execute(
                        select(func.count()).select_from(ReconciliationCaseModel).where(*filters)
                    )
                ).scalar_one()
            )
            if total == 0:
                return [], 0
            row_tuples = (
                await session.execute(
                    _case_detail_stmt()
                    .where(*filters)
                    .order_by(
                        ReconciliationCaseModel.created_at.desc(),
                        ReconciliationCaseModel.id.desc(),
                    )
                    .offset((page - 1) * page_size)
                    .limit(page_size)
                )
            ).all()
            items = await _hydrate_case_rows(session, row_tuples)
            return items, total

    async def get_case_by_id(self, reconciliation_id: UUID) -> ReconciliationCaseEntity | None:
        async with self._session_factory() as session:
            return await _fetch_case_detail(session, reconciliation_id)

    async def get_case_coop_id(self, reconciliation_id: UUID) -> UUID | None:
        async with self._session_factory() as session:
            return (
                await session.execute(
                    select(DeliveryOrderModel.cooperative_id)
                    .join(
                        ReconciliationCaseModel,
                        ReconciliationCaseModel.delivery_order_id == DeliveryOrderModel.id,
                    )
                    .where(ReconciliationCaseModel.id == reconciliation_id)
                )
            ).scalar_one_or_none()

    async def create_or_trigger(
        self,
        *,
        delivery_order_id: UUID,
        weight_basis: WeightBasis,
        actor_id: UUID,
        idempotency_record_id: UUID,
    ) -> ReconciliationCaseEntity:
        assert_equivalent_weight_basis(weight_basis)
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
                if do.status == DeliveryOrderStatus.CANCELLED.value:
                    raise AppError(
                        ErrorCode.REC_INVALID_STATE_TRANSITION,
                        details={"current_status": do.status},
                    )

                ticket = (
                    await session.execute(
                        select(MillWeighingTicketModel).where(
                            MillWeighingTicketModel.delivery_order_id == delivery_order_id,
                            MillWeighingTicketModel.is_current.is_(True),
                        )
                    )
                ).scalar_one_or_none()
                if ticket is None or ticket.status != MillTicketStatus.VERIFIED.value:
                    raise AppError(ErrorCode.REC_NOT_READY)

                existing_current = (
                    await session.execute(
                        select(ReconciliationCaseModel)
                        .where(
                            ReconciliationCaseModel.delivery_order_id == delivery_order_id,
                            ReconciliationCaseModel.is_current.is_(True),
                        )
                        .with_for_update()
                    )
                ).scalar_one_or_none()

                if existing_current is not None and existing_current.mill_ticket_id == ticket.id:
                    raise AppError(
                        ErrorCode.REC_INVALID_STATE_TRANSITION,
                        details={"current_status": existing_current.status},
                    )

                rule_id, tol_pct, tol_policy = await _load_active_tolerance_rule(session)
                diff = compute_reconciliation_diff(
                    origin_weight_kg=do.total_origin_weight_kg,
                    mill_weight_kg=ticket.net_weight_kg,
                    tolerance_percent=tol_pct,
                )

                next_rev = 1
                if existing_current is not None:
                    next_rev = existing_current.revision_number + 1
                    existing_current.is_current = False
                    await session.flush()

                case = ReconciliationCaseModel(
                    id=uuid4(),
                    delivery_order_id=delivery_order_id,
                    mill_ticket_id=ticket.id,
                    revision_number=next_rev,
                    origin_weight_kg=diff.origin_weight_kg,
                    mill_weight_kg=diff.mill_weight_kg,
                    difference_weight_kg=diff.difference_weight_kg,
                    difference_percent=diff.difference_percent,
                    tolerance_percent=tol_pct,
                    rule_version_id=rule_id,
                    tolerance_policy_classification=tol_policy.value,
                    is_negative_difference=diff.is_negative_difference,
                    status=diff.resulting_status.value,
                    is_current=True,
                    agreed_settlement_weight_kg=(
                        diff.mill_weight_kg
                        if diff.resulting_status == ReconciliationStatus.MATCHED
                        else None
                    ),
                    calculated_at=now,
                    resolved_at=None,
                    created_by=actor_id,
                    created_at=now,
                )
                session.add(case)
                try:
                    await session.flush()
                except IntegrityError as exc:
                    raise AppError(
                        ErrorCode.REC_INVALID_STATE_TRANSITION,
                        details={"current_status": ReconciliationStatus.READY.value},
                    ) from exc

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="RECONCILIATION_CALCULATED",
                        module="reconciliation",
                        resource_type="reconciliation_cases",
                        resource_id=str(case.id),
                        previous_state=None,
                        new_state={
                            "delivery_order_id": str(delivery_order_id),
                            "mill_ticket_id": str(ticket.id),
                            "revision_number": next_rev,
                            "difference_weight_kg": f"{diff.difference_weight_kg:.3f}",
                            "difference_percent": f"{diff.difference_percent:.4f}",
                            "tolerance_percent": f"{tol_pct:.4f}",
                            "is_negative_difference": diff.is_negative_difference,
                            "status": diff.resulting_status.value,
                        },
                        reason=None,
                    ),
                )
                await complete_idempotency_slot(
                    session,
                    record_id=idempotency_record_id,
                    response_reference=case.id,
                )
                case_id = case.id

        async with self._session_factory() as read_session:
            return _require_case(await _fetch_case_detail(read_session, case_id))

    async def calculate(
        self,
        *,
        reconciliation_id: UUID,
        actor_id: UUID,
        idempotency_record_id: UUID,
    ) -> ReconciliationCaseEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                case = (
                    await session.execute(
                        select(ReconciliationCaseModel)
                        .where(ReconciliationCaseModel.id == reconciliation_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if case is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                if not case.is_current or case.status not in (
                    ReconciliationStatus.WAITING_TICKET.value,
                    ReconciliationStatus.READY.value,
                ):
                    raise AppError(
                        ErrorCode.REC_INVALID_STATE_TRANSITION,
                        details={"current_status": case.status},
                    )

                do = await session.get(DeliveryOrderModel, case.delivery_order_id)
                if do is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                ticket = (
                    await session.execute(
                        select(MillWeighingTicketModel).where(
                            MillWeighingTicketModel.delivery_order_id == case.delivery_order_id,
                            MillWeighingTicketModel.is_current.is_(True),
                        )
                    )
                ).scalar_one_or_none()
                if ticket is None or ticket.status != MillTicketStatus.VERIFIED.value:
                    raise AppError(ErrorCode.REC_NOT_READY)

                rule_id, tol_pct, tol_policy = await _load_active_tolerance_rule(session)
                diff = compute_reconciliation_diff(
                    origin_weight_kg=do.total_origin_weight_kg,
                    mill_weight_kg=ticket.net_weight_kg,
                    tolerance_percent=tol_pct,
                )
                prev_status = case.status
                case.mill_ticket_id = ticket.id
                case.origin_weight_kg = diff.origin_weight_kg
                case.mill_weight_kg = diff.mill_weight_kg
                case.difference_weight_kg = diff.difference_weight_kg
                case.difference_percent = diff.difference_percent
                case.tolerance_percent = tol_pct
                case.rule_version_id = rule_id
                case.tolerance_policy_classification = tol_policy.value
                case.is_negative_difference = diff.is_negative_difference
                case.status = diff.resulting_status.value
                case.agreed_settlement_weight_kg = (
                    diff.mill_weight_kg
                    if diff.resulting_status == ReconciliationStatus.MATCHED
                    else None
                )
                case.calculated_at = now

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="RECONCILIATION_CALCULATED",
                        module="reconciliation",
                        resource_type="reconciliation_cases",
                        resource_id=str(case.id),
                        previous_state={"status": prev_status},
                        new_state={"status": case.status},
                        reason=None,
                    ),
                )
                await complete_idempotency_slot(
                    session,
                    record_id=idempotency_record_id,
                    response_reference=case.id,
                )

        async with self._session_factory() as read_session:
            return _require_case(await _fetch_case_detail(read_session, reconciliation_id))

    async def submit_review(
        self,
        *,
        reconciliation_id: UUID,
        decision: DisputeDecision,
        reason: str,
        evidence_file_id: UUID | None,
        proposed_settlement_weight_raw: str | None,
        actor_id: UUID,
    ) -> ReconciliationCaseEntity:
        now = datetime.now(UTC)
        proposed_kg = (
            Decimal(proposed_settlement_weight_raw.strip())
            if proposed_settlement_weight_raw
            else None
        )
        async with self._session_factory() as session:
            async with session.begin():
                case = (
                    await session.execute(
                        select(ReconciliationCaseModel)
                        .where(ReconciliationCaseModel.id == reconciliation_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if case is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                if case.status != ReconciliationStatus.DISPUTE_HOLD.value:
                    raise AppError(
                        ErrorCode.REC_INVALID_STATE_TRANSITION,
                        details={"current_status": case.status},
                    )
                if (
                    evidence_file_id is not None
                    and await session.get(FileAssetModel, evidence_file_id) is None
                ):
                    raise AppError(ErrorCode.VAL_INVALID_FORMAT)

                review = DisputeReviewModel(
                    id=uuid4(),
                    reconciliation_case_id=case.id,
                    reviewer_id=actor_id,
                    previous_status=case.status,
                    decision=decision.value,
                    proposed_settlement_weight_kg=proposed_kg,
                    reason=reason,
                    evidence_file_id=evidence_file_id,
                    approved_by=None,
                    reviewed_at=now,
                    created_at=now,
                )
                session.add(review)
                case.status = ReconciliationStatus.UNDER_REVIEW.value

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="DISPUTE_REVIEW_SUBMITTED",
                        module="reconciliation",
                        resource_type="reconciliation_cases",
                        resource_id=str(case.id),
                        previous_state={"status": ReconciliationStatus.DISPUTE_HOLD.value},
                        new_state={
                            "status": ReconciliationStatus.UNDER_REVIEW.value,
                            "decision": decision.value,
                        },
                        reason=reason,
                    ),
                )

        async with self._session_factory() as read_session:
            return _require_case(await _fetch_case_detail(read_session, reconciliation_id))

    async def resolve_dispute(
        self,
        *,
        reconciliation_id: UUID,
        decision: DisputeDecision,
        final_outcome: ReconciliationStatus,
        agreed_settlement_weight_raw: str | None,
        reason: str,
        evidence_file_id: UUID | None,
        actor_id: UUID,
        non_approver_admin: bool,
    ) -> ReconciliationCaseEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                case = (
                    await session.execute(
                        select(ReconciliationCaseModel)
                        .where(ReconciliationCaseModel.id == reconciliation_id)
                        .options(selectinload(ReconciliationCaseModel.dispute_reviews))
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if case is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)

                reviewer_ids = {r.reviewer_id for r in case.dispute_reviews}
                assert_can_resolve_dispute(
                    current_status=ReconciliationStatus(case.status),
                    reviewer_ids=reviewer_ids,
                    actor_id=actor_id,
                    non_approver_admin=non_approver_admin,
                )
                if (
                    evidence_file_id is not None
                    and await session.get(FileAssetModel, evidence_file_id) is None
                ):
                    raise AppError(ErrorCode.VAL_INVALID_FORMAT)

                agreed_weight = resolve_settlement_weight(
                    decision=decision,
                    final_outcome=final_outcome,
                    origin_weight_kg=case.origin_weight_kg,
                    mill_weight_kg=case.mill_weight_kg,
                    agreed_raw=agreed_settlement_weight_raw,
                )

                for rev in case.dispute_reviews:
                    if rev.approved_by is None:
                        rev.approved_by = actor_id

                session.add(
                    DisputeReviewModel(
                        id=uuid4(),
                        reconciliation_case_id=case.id,
                        reviewer_id=actor_id,
                        previous_status=case.status,
                        decision=decision.value,
                        proposed_settlement_weight_kg=agreed_weight,
                        reason=reason,
                        evidence_file_id=evidence_file_id,
                        approved_by=actor_id,
                        reviewed_at=now,
                        created_at=now,
                    )
                )
                prev_status = case.status
                case.status = final_outcome.value
                case.agreed_settlement_weight_kg = agreed_weight
                case.resolved_at = now

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="DISPUTE_RESOLVED",
                        module="reconciliation",
                        resource_type="reconciliation_cases",
                        resource_id=str(case.id),
                        previous_state={"status": prev_status},
                        new_state={
                            "status": final_outcome.value,
                            "decision": decision.value,
                            "agreed_settlement_weight_kg": (
                                f"{agreed_weight:.3f}" if agreed_weight is not None else None
                            ),
                        },
                        reason=reason,
                    ),
                )

        async with self._session_factory() as read_session:
            return _require_case(await _fetch_case_detail(read_session, reconciliation_id))

    async def compute_allocations(
        self,
        *,
        reconciliation_id: UUID,
        mode: AllocationMode,
        allocation_policy_version_id: UUID,
        actor_id: UUID,
    ) -> list[FarmerSettlementAllocationEntity]:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                case = (
                    await session.execute(
                        select(ReconciliationCaseModel)
                        .where(ReconciliationCaseModel.id == reconciliation_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if case is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)

                if case.status in (
                    ReconciliationStatus.DISPUTE_HOLD.value,
                    ReconciliationStatus.UNDER_REVIEW.value,
                ):
                    raise AppError(
                        ErrorCode.REC_WEIGHT_DISPUTE,
                        details={
                            "reconciliation_status": case.status,
                            "difference_weight_kg": f"{case.difference_weight_kg:.3f}",
                            "difference_percent": f"{case.difference_percent:.4f}",
                            "tolerance_percent": f"{case.tolerance_percent:.4f}",
                            "policy_classification": case.tolerance_policy_classification,
                        },
                    )
                if case.status not in (
                    ReconciliationStatus.MATCHED.value,
                    ReconciliationStatus.RESOLVED.value,
                ):
                    raise AppError(
                        ErrorCode.REC_INVALID_STATE_TRANSITION,
                        details={"current_status": case.status},
                    )

                policy = await session.get(SystemRuleVersionModel, allocation_policy_version_id)
                if policy is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)

                if mode == AllocationMode.FINAL and policy.approval_status != "APPROVED":
                    raise AppError(
                        ErrorCode.REC_ALLOCATION_POLICY_UNCONFIRMED,
                        details={"pending_decision_id": "BSD-DEC-013"},
                    )

                do = await session.get(DeliveryOrderModel, case.delivery_order_id)
                if do is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                contract = await session.get(TradeContractModel, do.contract_id)
                unit_price = (
                    contract.agreed_price_per_kg
                    if contract is not None and contract.agreed_price_per_kg is not None
                    else Decimal("0.00")
                )

                from app.modules.tbs_receiving.infrastructure.models import TbsReceiptModel

                line_rows = (
                    await session.execute(
                        select(
                            DeliveryOrderLineModel.receipt_id,
                            TbsReceiptModel.farmer_id,
                            FarmerModel.full_name,
                            DeliveryOrderLineModel.origin_weight_snapshot_kg,
                        )
                        .join(
                            TbsReceiptModel,
                            TbsReceiptModel.id == DeliveryOrderLineModel.receipt_id,
                        )
                        .join(FarmerModel, FarmerModel.id == TbsReceiptModel.farmer_id)
                        .where(
                            DeliveryOrderLineModel.delivery_order_id == do.id,
                            DeliveryOrderLineModel.allocation_status == "ACTIVE",
                        )
                        .order_by(
                            DeliveryOrderLineModel.created_at.asc(),
                            TbsReceiptModel.receipt_number.asc(),
                            DeliveryOrderLineModel.id.asc(),
                        )
                    )
                ).all()

                target_weight = case.agreed_settlement_weight_kg or case.mill_weight_kg
                computed = compute_proportional_allocations(
                    lines=[
                        AllocationLineInput(
                            receipt_id=rid,
                            farmer_id=fid,
                            farmer_name=fname,
                            origin_weight_kg=w_kg,
                        )
                        for rid, fid, fname, w_kg in line_rows
                    ],
                    target_total_weight_kg=target_weight,
                    unit_price_per_kg=unit_price,
                )

                await session.execute(
                    delete(FarmerSettlementAllocationModel).where(
                        FarmerSettlementAllocationModel.reconciliation_case_id == case.id
                    )
                )
                await session.flush()

                row_status = (
                    AllocationRecordStatus.APPROVED.value
                    if mode == AllocationMode.FINAL
                    else AllocationRecordStatus.SIMULATED.value
                )
                policy_cls = (
                    PolicyClassification.CONFIRMED.value
                    if mode == AllocationMode.FINAL
                    else PolicyClassification.SIMULATION_ONLY.value
                )

                entities: list[FarmerSettlementAllocationEntity] = []
                for idx, item in enumerate(computed):
                    aid = uuid4()
                    session.add(
                        FarmerSettlementAllocationModel(
                            id=aid,
                            reconciliation_case_id=case.id,
                            receipt_id=item.receipt_id,
                            farmer_id=item.farmer_id,
                            allocation_basis_weight_kg=item.allocation_basis_weight_kg,
                            agreed_weight_kg=item.agreed_weight_kg,
                            allocation_policy_version_id=policy.id,
                            gross_amount=item.gross_amount,
                            deduction_amount=item.deduction_amount,
                            net_amount=item.net_amount,
                            status=row_status,
                            policy_classification=policy_cls,
                            approved_at=now if mode == AllocationMode.FINAL else None,
                            created_at=now + timedelta(microseconds=idx),
                        )
                    )
                    entities.append(
                        FarmerSettlementAllocationEntity(
                            id=aid,
                            receipt_id=item.receipt_id,
                            farmer_id=item.farmer_id,
                            farmer_name=item.farmer_name,
                            allocation_basis_weight_kg=item.allocation_basis_weight_kg,
                            agreed_weight_kg=item.agreed_weight_kg,
                            allocation_policy_version_id=policy.id,
                            gross_amount=item.gross_amount,
                            deduction_amount=item.deduction_amount,
                            net_amount=item.net_amount,
                            status=AllocationRecordStatus(row_status),
                            policy_classification=PolicyClassification(policy_cls),
                        )
                    )

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="FARMER_ALLOCATIONS_COMPUTED",
                        module="reconciliation",
                        resource_type="farmer_settlement_allocations",
                        resource_id=str(case.id),
                        previous_state=None,
                        new_state={
                            "mode": mode.value,
                            "rows_count": len(entities),
                            "target_total_weight_kg": f"{target_weight:.3f}",
                        },
                        reason=None,
                    ),
                )
                return entities
