"""SQL-aggregated PostgreSQL repository for Overview, Supply, Reconciliation & Finance."""

from __future__ import annotations

from datetime import UTC, date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import case, exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.system_rules import (
    RULE_BUSINESS_MODEL_POLICY_ID,
    RULE_RECONCILIATION_TOLERANCE_ID,
    SystemRuleVersionModel,
)
from app.modules.contracts.domain.entities import PolicyClassification
from app.modules.finance.infrastructure.models import (
    InvoiceModel,
    PaymentApprovalModel,
    PaymentRecordModel,
)
from app.modules.identity_access.domain.entities import RoleCode
from app.modules.logistics.infrastructure.models import (
    DeliveryOrderLineModel,
    DeliveryOrderModel,
)
from app.modules.master_data.infrastructure.models import (
    CooperativeModel,
    FarmerModel,
    MillModel,
    PartyModel,
)
from app.modules.mill_weighing.infrastructure.models import MillWeighingTicketModel
from app.modules.reconciliation.infrastructure.models import ReconciliationCaseModel
from app.modules.reporting.domain.entities import (
    FinanceReportEntity,
    OverviewReportEntity,
    ReconciliationReportEntity,
    SupplyByMillEntity,
    SupplyReportEntity,
)
from app.modules.reporting.domain.rules import (
    FINANCE_SIMULATION_MARGIN_LABEL,
    compute_gross_contribution_simulation,
)
from app.modules.tbs_receiving.infrastructure.models import (
    ReceiptWeighingRevisionModel,
    TbsReceiptModel,
)


def _window_bounds(period_from: date, period_to: date) -> tuple[datetime, datetime]:
    return (
        datetime.combine(period_from, time.min, tzinfo=UTC),
        datetime.combine(period_to, time.max, tzinfo=UTC),
    )


def _policy_from_rule(rule: SystemRuleVersionModel | None) -> PolicyClassification:
    if rule is None:
        return PolicyClassification.PENDING_SOP
    if rule.approval_status == "APPROVED":
        return PolicyClassification.CONFIRMED
    if rule.approval_status == "PENDING_SOP":
        return PolicyClassification.PENDING_SOP
    return PolicyClassification.SIMULATION_ONLY


async def _latest_rule(session: AsyncSession, rule_code: str) -> SystemRuleVersionModel | None:
    return (
        (
            await session.execute(
                select(SystemRuleVersionModel)
                .where(
                    SystemRuleVersionModel.rule_code == rule_code,
                    SystemRuleVersionModel.approval_status.in_(
                        ["APPROVED", "SIMULATION_ONLY", "PENDING_SOP"]
                    ),
                )
                .order_by(SystemRuleVersionModel.version_number.desc())
                .limit(1)
            )
        )
        .scalars()
        .first()
    )


class SqlAlchemyReportingRepository:
    """SQL aggregation queries excluding CANCELLED rows (DBD §20.5)."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def fetch_overview(
        self,
        *,
        role_code: RoleCode,
        period_from: date,
        period_to: date,
        allowed_farmer_ids: set[UUID] | None,
        allowed_cooperative_ids: set[UUID] | None,
        allowed_mill_ids: set[UUID] | None,
    ) -> OverviewReportEntity:
        start_dt, end_dt = _window_bounds(period_from, period_to)
        now = datetime.now(UTC)

        async with self._session_factory() as session:
            # Determine scope predicates cleanly without fetching whole tables
            if allowed_farmer_ids is not None and not allowed_farmer_ids:
                return OverviewReportEntity(
                    role_code=role_code,
                    period_from=period_from,
                    period_to=period_to,
                    total_receipts_count=0,
                    total_received_weight_kg=Decimal("0.000"),
                    active_deliveries_count=0,
                    matched_reconciliations_count=0,
                    dispute_reconciliations_count=0,
                    farmer_paid_amount=Decimal("0.00"),
                    farmer_pending_amount=Decimal("0.00"),
                    is_simulation_data=True,
                    data_freshness_at=now,
                )

            if allowed_mill_ids is not None:
                if not allowed_mill_ids:
                    receipt_count, total_weight = 0, Decimal("0.000")
                else:
                    rec_agg = (
                        await session.execute(
                            select(
                                func.count(func.distinct(DeliveryOrderLineModel.receipt_id)),
                                func.coalesce(
                                    func.sum(DeliveryOrderLineModel.origin_weight_snapshot_kg),
                                    Decimal("0.000"),
                                ),
                            )
                            .select_from(DeliveryOrderLineModel)
                            .join(
                                DeliveryOrderModel,
                                DeliveryOrderModel.id == DeliveryOrderLineModel.delivery_order_id,
                            )
                            .where(
                                DeliveryOrderLineModel.allocation_status == "ACTIVE",
                                DeliveryOrderModel.mill_id.in_(allowed_mill_ids),
                                DeliveryOrderModel.status != "CANCELLED",
                                DeliveryOrderModel.created_at >= start_dt,
                                DeliveryOrderModel.created_at <= end_dt,
                            )
                        )
                    ).one()
                    receipt_count = int(rec_agg[0])
                    total_weight = Decimal(rec_agg[1]).quantize(Decimal("0.000"))
            else:
                rec_filters: list[Any] = [
                    TbsReceiptModel.status != "CANCELLED",
                    TbsReceiptModel.received_at >= start_dt,
                    TbsReceiptModel.received_at <= end_dt,
                ]
                if allowed_farmer_ids is not None:
                    rec_filters.append(TbsReceiptModel.farmer_id.in_(allowed_farmer_ids))
                elif allowed_cooperative_ids is not None:
                    if not allowed_cooperative_ids:
                        rec_filters.append(TbsReceiptModel.cooperative_id.is_(None))
                    else:
                        rec_filters.append(
                            TbsReceiptModel.cooperative_id.in_(allowed_cooperative_ids)
                        )
                rec_row = (
                    await session.execute(
                        select(
                            func.count(func.distinct(TbsReceiptModel.id)),
                            func.coalesce(
                                func.sum(ReceiptWeighingRevisionModel.net_weight_kg),
                                Decimal("0.000"),
                            ),
                        )
                        .select_from(TbsReceiptModel)
                        .outerjoin(
                            ReceiptWeighingRevisionModel,
                            (ReceiptWeighingRevisionModel.receipt_id == TbsReceiptModel.id)
                            & ReceiptWeighingRevisionModel.is_current.is_(True),
                        )
                        .where(*rec_filters)
                    )
                ).one()
                receipt_count = int(rec_row[0])
                total_weight = Decimal(rec_row[1]).quantize(Decimal("0.000"))

            do_filters: list[Any] = [
                DeliveryOrderModel.created_at >= start_dt,
                DeliveryOrderModel.created_at <= end_dt,
            ]
            if allowed_mill_ids is not None:
                do_filters.append(
                    DeliveryOrderModel.mill_id.in_(allowed_mill_ids)
                    if allowed_mill_ids
                    else DeliveryOrderModel.mill_id.is_(None)
                )
            elif allowed_cooperative_ids is not None:
                do_filters.append(
                    DeliveryOrderModel.cooperative_id.in_(allowed_cooperative_ids)
                    if allowed_cooperative_ids
                    else DeliveryOrderModel.cooperative_id.is_(None)
                )
            elif allowed_farmer_ids is not None:
                farmer_do_subq = (
                    select(DeliveryOrderLineModel.delivery_order_id)
                    .join(TbsReceiptModel, TbsReceiptModel.id == DeliveryOrderLineModel.receipt_id)
                    .where(
                        DeliveryOrderLineModel.allocation_status == "ACTIVE",
                        TbsReceiptModel.farmer_id.in_(allowed_farmer_ids),
                    )
                )
                do_filters.append(DeliveryOrderModel.id.in_(farmer_do_subq))

            active_deliveries_count = int(
                (
                    await session.execute(
                        select(func.count(DeliveryOrderModel.id)).where(
                            *do_filters,
                            DeliveryOrderModel.status.in_(
                                ["DRAFT", "READY", "IN_TRANSIT", "ARRIVED", "RECEIVED"]
                            ),
                        )
                    )
                ).scalar_one()
            )

            rec_summary = (
                await session.execute(
                    select(
                        func.count(
                            case(
                                (
                                    ReconciliationCaseModel.status.in_(["MATCHED", "RESOLVED"]),
                                    1,
                                )
                            )
                        ),
                        func.count(
                            case(
                                (
                                    ReconciliationCaseModel.status.in_(
                                        ["DISPUTE_HOLD", "UNDER_REVIEW"]
                                    ),
                                    1,
                                )
                            )
                        ),
                    )
                    .select_from(ReconciliationCaseModel)
                    .join(
                        DeliveryOrderModel,
                        DeliveryOrderModel.id == ReconciliationCaseModel.delivery_order_id,
                    )
                    .where(
                        *do_filters,
                        DeliveryOrderModel.status != "CANCELLED",
                        ReconciliationCaseModel.is_current.is_(True),
                        ReconciliationCaseModel.status != "CANCELLED",
                    )
                )
            ).one()
            matched_cnt, dispute_cnt = int(rec_summary[0]), int(rec_summary[1])

            farmer_paid: Decimal | None = None
            farmer_pending: Decimal | None = None
            if role_code in (
                RoleCode.FARMER,
                RoleCode.COOPERATIVE_OPERATOR,
                RoleCode.PERUMDA_FINANCE,
                RoleCode.DIRECTOR,
            ):
                payee_filter: list[Any] = [
                    PaymentRecordModel.payment_direction == "OUTBOUND",
                    PaymentRecordModel.payment_date >= period_from,
                    PaymentRecordModel.payment_date <= period_to,
                ]
                if allowed_farmer_ids is not None:
                    f_parties = list(
                        (
                            await session.execute(
                                select(FarmerModel.party_id).where(
                                    FarmerModel.id.in_(allowed_farmer_ids)
                                )
                            )
                        ).scalars()
                    )
                    payee_filter.append(
                        PaymentRecordModel.payee_party_id.in_(f_parties)
                        if f_parties
                        else PaymentRecordModel.id.is_(None)
                    )
                elif allowed_cooperative_ids is not None:
                    c_parties = list(
                        (
                            await session.execute(
                                select(CooperativeModel.party_id).where(
                                    CooperativeModel.id.in_(allowed_cooperative_ids)
                                )
                            )
                        ).scalars()
                    )
                    payee_filter.append(
                        PaymentRecordModel.payee_party_id.in_(c_parties)
                        if c_parties
                        else PaymentRecordModel.id.is_(None)
                    )
                pay_row = (
                    await session.execute(
                        select(
                            func.coalesce(
                                func.sum(
                                    case(
                                        (
                                            PaymentRecordModel.status == "VERIFIED",
                                            PaymentRecordModel.amount,
                                        ),
                                        else_=Decimal("0.00"),
                                    )
                                ),
                                Decimal("0.00"),
                            ),
                            func.coalesce(
                                func.sum(
                                    case(
                                        (
                                            PaymentRecordModel.status == "PENDING_VERIFICATION",
                                            PaymentRecordModel.amount,
                                        ),
                                        else_=Decimal("0.00"),
                                    )
                                ),
                                Decimal("0.00"),
                            ),
                        ).where(*payee_filter)
                    )
                ).one()
                farmer_paid = Decimal(pay_row[0]).quantize(Decimal("0.00"))
                farmer_pending = Decimal(pay_row[1]).quantize(Decimal("0.00"))

            tol_rule = await _latest_rule(session, "RECONCILIATION_TOLERANCE")
            biz_rule = await _latest_rule(session, "BUSINESS_MODEL_POLICY")
            is_sim = (tol_rule is None or tol_rule.approval_status != "APPROVED") or (
                biz_rule is None or biz_rule.approval_status != "APPROVED"
            )

            return OverviewReportEntity(
                role_code=role_code,
                period_from=period_from,
                period_to=period_to,
                total_receipts_count=receipt_count,
                total_received_weight_kg=total_weight,
                active_deliveries_count=active_deliveries_count,
                matched_reconciliations_count=matched_cnt,
                dispute_reconciliations_count=dispute_cnt,
                farmer_paid_amount=farmer_paid,
                farmer_pending_amount=farmer_pending,
                is_simulation_data=is_sim,
                data_freshness_at=now,
            )

    async def fetch_supply(
        self,
        *,
        period_from: date,
        period_to: date,
        allowed_cooperative_ids: set[UUID] | None,
        mill_id: UUID | None,
    ) -> SupplyReportEntity:
        start_dt, end_dt = _window_bounds(period_from, period_to)
        now = datetime.now(UTC)

        async with self._session_factory() as session:
            base_filters: list[Any] = [
                DeliveryOrderModel.created_at >= start_dt,
                DeliveryOrderModel.created_at <= end_dt,
            ]
            if allowed_cooperative_ids is not None:
                base_filters.append(
                    DeliveryOrderModel.cooperative_id.in_(allowed_cooperative_ids)
                    if allowed_cooperative_ids
                    else DeliveryOrderModel.id.is_(None)
                )
            if mill_id is not None:
                base_filters.append(DeliveryOrderModel.mill_id == mill_id)

            excluded_cancelled = int(
                (
                    await session.execute(
                        select(func.count(DeliveryOrderModel.id)).where(
                            *base_filters,
                            DeliveryOrderModel.status == "CANCELLED",
                        )
                    )
                ).scalar_one()
            )

            rows = (
                await session.execute(
                    select(
                        MillModel.id,
                        MillModel.mill_name,
                        func.count(DeliveryOrderModel.id),
                        func.coalesce(
                            func.sum(DeliveryOrderModel.total_origin_weight_kg),
                            Decimal("0.000"),
                        ),
                        func.coalesce(
                            func.sum(MillWeighingTicketModel.net_weight_kg),
                            Decimal("0.000"),
                        ),
                    )
                    .select_from(DeliveryOrderModel)
                    .join(MillModel, MillModel.id == DeliveryOrderModel.mill_id)
                    .outerjoin(
                        MillWeighingTicketModel,
                        (MillWeighingTicketModel.delivery_order_id == DeliveryOrderModel.id)
                        & MillWeighingTicketModel.is_current.is_(True)
                        & (MillWeighingTicketModel.status == "VERIFIED"),
                    )
                    .where(*base_filters, DeliveryOrderModel.status != "CANCELLED")
                    .group_by(MillModel.id, MillModel.mill_name)
                    .order_by(MillModel.mill_name.asc())
                )
            ).all()

            total_origin = Decimal("0.000")
            total_mill = Decimal("0.000")
            by_mill: list[SupplyByMillEntity] = []
            for m_id, m_name, cnt, orig_sum, mill_sum in rows:
                o_dec = Decimal(orig_sum).quantize(Decimal("0.000"))
                m_dec = Decimal(mill_sum).quantize(Decimal("0.000"))
                total_origin += o_dec
                total_mill += m_dec
                by_mill.append(
                    SupplyByMillEntity(
                        mill_id=m_id,
                        mill_name=m_name,
                        delivery_count=int(cnt),
                        total_mill_weight_kg=m_dec,
                    )
                )

            return SupplyReportEntity(
                period_from=period_from,
                period_to=period_to,
                total_origin_kg=total_origin.quantize(Decimal("0.000")),
                total_mill_received_kg=total_mill.quantize(Decimal("0.000")),
                excluded_cancelled_count=excluded_cancelled,
                by_mill=tuple(by_mill),
                data_freshness_at=now,
            )

    async def fetch_reconciliation(
        self,
        *,
        period_from: date,
        period_to: date,
        allowed_cooperative_ids: set[UUID] | None,
    ) -> ReconciliationReportEntity:
        start_dt, end_dt = _window_bounds(period_from, period_to)
        now = datetime.now(UTC)

        async with self._session_factory() as session:
            filters: list[Any] = [
                ReconciliationCaseModel.is_current.is_(True),
                ReconciliationCaseModel.status != "CANCELLED",
                DeliveryOrderModel.status != "CANCELLED",
                ReconciliationCaseModel.created_at >= start_dt,
                ReconciliationCaseModel.created_at <= end_dt,
            ]
            if allowed_cooperative_ids is not None:
                filters.append(
                    DeliveryOrderModel.cooperative_id.in_(allowed_cooperative_ids)
                    if allowed_cooperative_ids
                    else DeliveryOrderModel.id.is_(None)
                )

            agg = (
                await session.execute(
                    select(
                        func.count(case((ReconciliationCaseModel.status == "WAITING_TICKET", 1))),
                        func.count(case((ReconciliationCaseModel.status == "READY", 1))),
                        func.count(case((ReconciliationCaseModel.status == "MATCHED", 1))),
                        func.count(
                            case(
                                (
                                    ReconciliationCaseModel.status.in_(
                                        ["DISPUTE_HOLD", "UNDER_REVIEW"]
                                    ),
                                    1,
                                )
                            )
                        ),
                        func.count(case((ReconciliationCaseModel.status == "RESOLVED", 1))),
                        func.count(
                            case((ReconciliationCaseModel.is_negative_difference.is_(True), 1))
                        ),
                    )
                    .select_from(ReconciliationCaseModel)
                    .join(
                        DeliveryOrderModel,
                        DeliveryOrderModel.id == ReconciliationCaseModel.delivery_order_id,
                    )
                    .where(*filters)
                )
            ).one()

            tol_rule = await _latest_rule(session, "RECONCILIATION_TOLERANCE")
            rule_id = tol_rule.id if tol_rule is not None else RULE_RECONCILIATION_TOLERANCE_ID

            return ReconciliationReportEntity(
                period_from=period_from,
                period_to=period_to,
                waiting_ticket_count=int(agg[0]),
                ready_count=int(agg[1]),
                matched_count=int(agg[2]),
                dispute_hold_count=int(agg[3]),
                resolved_count=int(agg[4]),
                negative_difference_count=int(agg[5]),
                active_rule_version_id=rule_id,
                data_freshness_at=now,
            )

    async def fetch_finance(
        self,
        *,
        period_from: date,
        period_to: date,
    ) -> FinanceReportEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            ar_billed = Decimal(
                (
                    await session.execute(
                        select(
                            func.coalesce(func.sum(InvoiceModel.total_amount), Decimal("0.00"))
                        ).where(
                            InvoiceModel.invoice_type == "ACCOUNTS_RECEIVABLE",
                            InvoiceModel.status == "ISSUED",
                            InvoiceModel.invoice_date >= period_from,
                            InvoiceModel.invoice_date <= period_to,
                        )
                    )
                ).scalar_one()
            ).quantize(Decimal("0.00"))

            approved_subq = exists(
                select(PaymentApprovalModel.id).where(
                    PaymentApprovalModel.invoice_id == InvoiceModel.id,
                    PaymentApprovalModel.decision == "APPROVED",
                )
            )
            verified_pay_subq = exists(
                select(PaymentRecordModel.id).where(
                    PaymentRecordModel.invoice_id == InvoiceModel.id,
                    PaymentRecordModel.status == "VERIFIED",
                )
            )
            ap_approved_unpaid = Decimal(
                (
                    await session.execute(
                        select(
                            func.coalesce(func.sum(InvoiceModel.total_amount), Decimal("0.00"))
                        ).where(
                            InvoiceModel.invoice_type == "ACCOUNTS_PAYABLE",
                            InvoiceModel.status == "ISSUED",
                            InvoiceModel.invoice_date >= period_from,
                            InvoiceModel.invoice_date <= period_to,
                            approved_subq,
                            ~verified_pay_subq,
                        )
                    )
                ).scalar_one()
            ).quantize(Decimal("0.00"))

            pay_agg = (
                await session.execute(
                    select(
                        func.coalesce(
                            func.sum(
                                case(
                                    (
                                        (PaymentRecordModel.payment_direction == "INBOUND")
                                        & (PaymentRecordModel.status == "VERIFIED"),
                                        PaymentRecordModel.amount,
                                    ),
                                    else_=Decimal("0.00"),
                                )
                            ),
                            Decimal("0.00"),
                        ),
                        func.coalesce(
                            func.sum(
                                case(
                                    (
                                        (PaymentRecordModel.payment_direction == "OUTBOUND")
                                        & (PaymentRecordModel.status == "VERIFIED"),
                                        PaymentRecordModel.amount,
                                    ),
                                    else_=Decimal("0.00"),
                                )
                            ),
                            Decimal("0.00"),
                        ),
                        func.coalesce(
                            func.sum(
                                case(
                                    (
                                        (PaymentRecordModel.payment_direction == "OUTBOUND")
                                        & (PaymentRecordModel.status == "VERIFIED")
                                        & (PartyModel.party_type == "FARMER"),
                                        PaymentRecordModel.amount,
                                    ),
                                    else_=Decimal("0.00"),
                                )
                            ),
                            Decimal("0.00"),
                        ),
                    )
                    .select_from(PaymentRecordModel)
                    .join(PartyModel, PartyModel.id == PaymentRecordModel.payee_party_id)
                    .where(
                        PaymentRecordModel.payment_date >= period_from,
                        PaymentRecordModel.payment_date <= period_to,
                    )
                )
            ).one()

            ar_cash = Decimal(pay_agg[0]).quantize(Decimal("0.00"))
            ap_paid = Decimal(pay_agg[1]).quantize(Decimal("0.00"))
            farmer_disbursed = Decimal(pay_agg[2]).quantize(Decimal("0.00"))

            biz_rule = await _latest_rule(session, "BUSINESS_MODEL_POLICY")
            if biz_rule is None:
                biz_rule = await session.get(SystemRuleVersionModel, RULE_BUSINESS_MODEL_POLICY_ID)

            return FinanceReportEntity(
                period_from=period_from,
                period_to=period_to,
                ar_billed_total=ar_billed,
                ar_cash_collected_total=ar_cash,
                ap_approved_unpaid_total=ap_approved_unpaid,
                ap_verified_paid_total=ap_paid,
                farmer_disbursed_verified_total=farmer_disbursed,
                gross_contribution_simulation=compute_gross_contribution_simulation(
                    ar_billed_total=ar_billed,
                    ap_approved_unpaid_total=ap_approved_unpaid,
                    ap_verified_paid_total=ap_paid,
                ),
                margin_label=FINANCE_SIMULATION_MARGIN_LABEL,
                is_net_profit=False,
                policy_classification=_policy_from_rule(biz_rule),
                data_freshness_at=now,
            )
