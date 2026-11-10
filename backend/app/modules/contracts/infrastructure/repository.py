"""PostgreSQL repository implementation for Commercial Contracts and Quota Periods."""

from __future__ import annotations

from datetime import UTC, date, datetime
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
from app.core.system_rules import RULE_BUSINESS_MODEL_POLICY_ID, SystemRuleVersionModel
from app.modules.contracts.domain.entities import (
    BusinessModelCode,
    ContractStatus,
    PerumdaRoleCode,
    PriceRuleType,
    QuotaPeriodEntity,
    QuotaReservationEntity,
    QuotaReservationStatus,
    TradeContractEntity,
)
from app.modules.contracts.domain.rules import (
    assert_can_approve_contract,
    derive_contract_policy_classification,
)
from app.modules.contracts.infrastructure.models import (
    ContractApprovalEventModel,
    ContractQuotaPeriodModel,
    QuotaReservationModel,
    TradeContractModel,
)
from app.modules.contracts.infrastructure.quota_ops import (
    compute_period_usage,
    reserve_quota_in_tx,
)
from app.modules.master_data.infrastructure.models import MillModel, PartyModel


def _require_contract(entity: TradeContractEntity | None) -> TradeContractEntity:
    if entity is None:
        raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
    return entity


async def _build_contract_entity(
    session: AsyncSession,
    row: TradeContractModel,
    *,
    mill_name: str,
    rule_approval_status: str,
) -> TradeContractEntity:
    periods = [
        await compute_period_usage(session, period=qp)
        for qp in sorted(row.quota_periods, key=lambda p: p.period_start)
    ]
    bmc = BusinessModelCode(row.business_model_code)
    return TradeContractEntity(
        id=row.id,
        contract_number=row.contract_number,
        mill_id=row.mill_id,
        mill_name=mill_name,
        start_date=row.start_date,
        end_date=row.end_date,
        price_rule_type=PriceRuleType(row.price_rule_type),
        agreed_price_per_kg=row.agreed_price_per_kg,
        business_model_code=bmc,
        perumda_role=PerumdaRoleCode(row.perumda_role),
        seller_party_id=row.seller_party_id,
        buyer_party_id=row.buyer_party_id,
        agent_party_id=row.agent_party_id,
        represented_party_id=row.represented_party_id,
        business_model_rule_version=row.business_model_rule_version,
        payment_terms=row.payment_terms,
        status=ContractStatus(row.status),
        policy_classification=derive_contract_policy_classification(
            business_model_code=bmc,
            rule_approval_status=rule_approval_status,
        ),
        quota_periods=tuple(periods),
        approved_by=row.approved_by,
        approved_at=row.approved_at,
        created_by=row.created_by,
        version=row.version,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


async def _fetch_contract_detail(
    session: AsyncSession, contract_id: UUID
) -> TradeContractEntity | None:
    stmt = (
        select(
            TradeContractModel,
            MillModel.mill_name,
            SystemRuleVersionModel.approval_status,
        )
        .join(MillModel, MillModel.id == TradeContractModel.mill_id)
        .join(
            SystemRuleVersionModel,
            SystemRuleVersionModel.id == TradeContractModel.business_model_rule_version,
        )
        .options(selectinload(TradeContractModel.quota_periods))
        .where(TradeContractModel.id == contract_id)
    )
    row_tuple = (await session.execute(stmt)).first()
    if row_tuple is None:
        return None
    row, mill_name, rule_status = row_tuple
    return await _build_contract_entity(
        session, row, mill_name=mill_name, rule_approval_status=rule_status
    )


def _to_reservation_entity(row: QuotaReservationModel) -> QuotaReservationEntity:
    return QuotaReservationEntity(
        id=row.id,
        quota_period_id=row.quota_period_id,
        delivery_order_id=row.delivery_order_id,
        reserved_weight_kg=row.reserved_weight_kg,
        consumed_weight_kg=row.consumed_weight_kg,
        status=QuotaReservationStatus(row.status),
        reserved_at=row.reserved_at,
    )


class SqlAlchemyContractsRepository:
    """PostgreSQL implementation of ContractsRepositoryPort."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def list_contracts(
        self,
        *,
        status_filter: ContractStatus | None,
        mill_id: UUID | None,
        page: int,
        page_size: int,
    ) -> tuple[list[TradeContractEntity], int]:
        filters: list[Any] = []
        if status_filter is not None:
            filters.append(TradeContractModel.status == status_filter.value)
        if mill_id is not None:
            filters.append(TradeContractModel.mill_id == mill_id)

        async with self._session_factory() as session:
            total = int(
                (
                    await session.execute(
                        select(func.count()).select_from(TradeContractModel).where(*filters)
                    )
                ).scalar_one()
            )
            stmt = (
                select(
                    TradeContractModel,
                    MillModel.mill_name,
                    SystemRuleVersionModel.approval_status,
                )
                .join(MillModel, MillModel.id == TradeContractModel.mill_id)
                .join(
                    SystemRuleVersionModel,
                    SystemRuleVersionModel.id == TradeContractModel.business_model_rule_version,
                )
                .options(selectinload(TradeContractModel.quota_periods))
                .where(*filters)
                .order_by(TradeContractModel.created_at.desc(), TradeContractModel.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            rows = (await session.execute(stmt)).all()
            entities: list[TradeContractEntity] = []
            for row, mill_name, rule_status in rows:
                entities.append(
                    await _build_contract_entity(
                        session,
                        row,
                        mill_name=mill_name,
                        rule_approval_status=rule_status,
                    )
                )
            return entities, total

    async def get_contract_by_id(self, contract_id: UUID) -> TradeContractEntity | None:
        async with self._session_factory() as session:
            return await _fetch_contract_detail(session, contract_id)

    async def create_contract(
        self,
        *,
        contract_number: str,
        mill_id: UUID,
        start_date: date,
        end_date: date,
        price_rule_type: PriceRuleType,
        agreed_price_per_kg: Decimal | None,
        business_model_code: BusinessModelCode,
        perumda_role: PerumdaRoleCode,
        seller_party_id: UUID,
        buyer_party_id: UUID,
        agent_party_id: UUID | None,
        represented_party_id: UUID | None,
        payment_terms: str,
        initial_quota_kg: Decimal,
        actor_id: UUID,
    ) -> TradeContractEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                mill = (
                    await session.execute(select(MillModel).where(MillModel.id == mill_id))
                ).scalar_one_or_none()
                if mill is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                if mill.partnership_status != "ACTIVE":
                    raise AppError(
                        ErrorCode.VAL_INVALID_FORMAT,
                        details=[
                            {
                                "field": "mill_id",
                                "reason": "PKS mitra tidak berstatus ACTIVE.",
                                "code": ErrorCode.VAL_INVALID_FORMAT.value,
                            }
                        ],
                    )

                party_ids = {seller_party_id, buyer_party_id}
                if agent_party_id is not None:
                    party_ids.add(agent_party_id)
                if represented_party_id is not None:
                    party_ids.add(represented_party_id)
                found_parties = {
                    p
                    for p in (
                        await session.execute(
                            select(PartyModel.id).where(PartyModel.id.in_(party_ids))
                        )
                    )
                    .scalars()
                    .all()
                }
                if len(found_parties) != len(party_ids):
                    raise AppError(
                        ErrorCode.VAL_INVALID_FORMAT,
                        details=[
                            {
                                "field": "seller_party_id",
                                "reason": "Salah satu entitas party kontrak tidak ditemukan.",
                                "code": ErrorCode.VAL_INVALID_FORMAT.value,
                            }
                        ],
                    )

                rule_row = (
                    await session.execute(
                        select(SystemRuleVersionModel)
                        .where(SystemRuleVersionModel.rule_code == "BUSINESS_MODEL_POLICY")
                        .order_by(SystemRuleVersionModel.version_number.desc())
                    )
                ).scalar_one_or_none()
                rule_id = rule_row.id if rule_row is not None else RULE_BUSINESS_MODEL_POLICY_ID

                contract = TradeContractModel(
                    id=uuid4(),
                    contract_number=contract_number,
                    mill_id=mill_id,
                    start_date=start_date,
                    end_date=end_date,
                    price_rule_type=price_rule_type.value,
                    agreed_price_per_kg=agreed_price_per_kg,
                    grading_policy_reference="BSD-DEC-006-SIMULATION",
                    business_model_code=business_model_code.value,
                    perumda_role=perumda_role.value,
                    seller_party_id=seller_party_id,
                    buyer_party_id=buyer_party_id,
                    agent_party_id=agent_party_id,
                    represented_party_id=represented_party_id,
                    business_model_rule_version=rule_id,
                    payment_terms=payment_terms,
                    status=ContractStatus.PENDING_APPROVAL.value,
                    created_by=actor_id,
                    approved_by=None,
                    approved_at=None,
                    version=1,
                    created_at=now,
                    updated_at=now,
                )
                session.add(contract)
                try:
                    await session.flush()
                except IntegrityError as exc:
                    raise AppError(ErrorCode.MD_DUPLICATE_CODE) from exc

                period = ContractQuotaPeriodModel(
                    id=uuid4(),
                    contract_id=contract.id,
                    period_start=start_date,
                    period_end=end_date,
                    quota_limit_kg=initial_quota_kg,
                    status="ACTIVE",
                    created_at=now,
                    updated_at=now,
                )
                session.add(period)
                session.add(
                    ContractApprovalEventModel(
                        id=uuid4(),
                        contract_id=contract.id,
                        action="SUBMIT_CONTRACT",
                        previous_status=ContractStatus.DRAFT.value,
                        new_status=ContractStatus.PENDING_APPROVAL.value,
                        actor_id=actor_id,
                        reason=None,
                        created_at=now,
                    )
                )

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="CONTRACT_CREATED",
                        module="contracts",
                        resource_type="trade_contracts",
                        resource_id=str(contract.id),
                        previous_state=None,
                        new_state={
                            "contract_number": contract_number,
                            "business_model_code": business_model_code.value,
                            "perumda_role": perumda_role.value,
                            "status": ContractStatus.PENDING_APPROVAL.value,
                            "initial_quota_kg": f"{initial_quota_kg:.3f}",
                        },
                        reason=None,
                    ),
                )
                contract_id = contract.id

        async with self._session_factory() as read_session:
            return _require_contract(await _fetch_contract_detail(read_session, contract_id))

    async def approve_contract(
        self,
        *,
        contract_id: UUID,
        actor_id: UUID,
        non_approver_admin: bool,
    ) -> TradeContractEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                contract = (
                    await session.execute(
                        select(TradeContractModel)
                        .where(TradeContractModel.id == contract_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if contract is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)

                prev_status = ContractStatus(contract.status)
                assert_can_approve_contract(
                    status=prev_status,
                    created_by=contract.created_by,
                    actor_id=actor_id,
                    non_approver_admin=non_approver_admin,
                )

                mill = (
                    await session.execute(select(MillModel).where(MillModel.id == contract.mill_id))
                ).scalar_one()
                if mill.partnership_status != "ACTIVE":
                    raise AppError(
                        ErrorCode.CONTRACT_NOT_ACTIVE,
                        details={"contract_status": prev_status.value},
                    )

                contract.status = ContractStatus.ACTIVE.value
                contract.approved_by = actor_id
                contract.approved_at = now
                contract.version += 1
                contract.updated_at = now

                session.add(
                    ContractApprovalEventModel(
                        id=uuid4(),
                        contract_id=contract.id,
                        action="APPROVE_CONTRACT",
                        previous_status=prev_status.value,
                        new_status=ContractStatus.ACTIVE.value,
                        actor_id=actor_id,
                        reason=None,
                        created_at=now,
                    )
                )
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="CONTRACT_APPROVED",
                        module="contracts",
                        resource_type="trade_contracts",
                        resource_id=str(contract.id),
                        previous_state={"status": prev_status.value},
                        new_state={"status": ContractStatus.ACTIVE.value},
                        reason=None,
                    ),
                )

        async with self._session_factory() as read_session:
            return _require_contract(await _fetch_contract_detail(read_session, contract_id))

    async def get_quota_periods(self, contract_id: UUID) -> list[QuotaPeriodEntity]:
        async with self._session_factory() as session:
            exists = (
                await session.execute(
                    select(TradeContractModel.id).where(TradeContractModel.id == contract_id)
                )
            ).scalar_one_or_none()
            if exists is None:
                raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
            periods = (
                (
                    await session.execute(
                        select(ContractQuotaPeriodModel)
                        .where(ContractQuotaPeriodModel.contract_id == contract_id)
                        .order_by(ContractQuotaPeriodModel.period_start.asc())
                    )
                )
                .scalars()
                .all()
            )
            return [await compute_period_usage(session, period=p) for p in periods]

    async def get_reservation_by_id(self, reservation_id: UUID) -> QuotaReservationEntity | None:
        async with self._session_factory() as session:
            row = await session.get(QuotaReservationModel, reservation_id)
            return _to_reservation_entity(row) if row is not None else None

    async def reserve_quota(
        self,
        *,
        contract_id: UUID,
        quota_period_id: UUID,
        delivery_order_id: UUID,
        reserved_weight_kg: Decimal,
        as_of_date: date,
        actor_id: UUID,
        idempotency_record_id: UUID,
    ) -> QuotaReservationEntity:
        async with self._session_factory() as session:
            async with session.begin():
                res = await reserve_quota_in_tx(
                    session,
                    contract_id=contract_id,
                    quota_period_id=quota_period_id,
                    delivery_order_id=delivery_order_id,
                    reserved_weight_kg=reserved_weight_kg,
                    as_of_date=as_of_date,
                    actor_id=actor_id,
                )
                await complete_idempotency_slot(
                    session,
                    record_id=idempotency_record_id,
                    response_reference=res.id,
                )
                return _to_reservation_entity(res)
