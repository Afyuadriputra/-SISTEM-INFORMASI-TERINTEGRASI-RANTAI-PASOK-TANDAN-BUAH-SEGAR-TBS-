"""PostgreSQL repository implementation for AR/AP Invoices, Approvals & Payments."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from app.core.audit import AuditRecordInput, append_audit_event
from app.core.exceptions import AppError, ErrorCode
from app.core.idempotency import complete_idempotency_slot
from app.core.system_rules import SystemRuleVersionModel
from app.modules.contracts.domain.entities import BusinessModelCode, PolicyClassification
from app.modules.contracts.infrastructure.models import TradeContractModel
from app.modules.files.infrastructure.models import FileAssetModel
from app.modules.finance.domain.entities import (
    InvoiceEntity,
    InvoiceLineEntity,
    InvoiceStatus,
    InvoiceType,
    PaymentApprovalDecision,
    PaymentApprovalEntity,
    PaymentDirection,
    PaymentMethod,
    PaymentRecordEntity,
    PaymentRecordStatus,
)
from app.modules.finance.domain.rules import (
    assert_can_approve_payment,
    assert_can_issue_invoice,
    assert_can_verify_invoice,
    assert_can_verify_payment_record,
    compute_line_amount,
    derive_settlement_status,
    validate_payment_submission,
)
from app.modules.finance.infrastructure.models import (
    InvoiceLineModel,
    InvoiceModel,
    PaymentApprovalModel,
    PaymentRecordModel,
)
from app.modules.logistics.infrastructure.models import (
    DeliveryOrderLineModel,
    DeliveryOrderModel,
)
from app.modules.master_data.domain.entities import PartyType
from app.modules.master_data.infrastructure.models import (
    CooperativeModel,
    FarmerModel,
    MillCompanyModel,
    MillModel,
    PartyModel,
)
from app.modules.pricing.infrastructure.models import MillPriceQuoteModel
from app.modules.reconciliation.infrastructure.models import ReconciliationCaseModel
from app.modules.tbs_receiving.infrastructure.models import TbsReceiptModel


def _map_approval(row: PaymentApprovalModel) -> PaymentApprovalEntity:
    return PaymentApprovalEntity(
        id=row.id,
        requested_by=row.requested_by,
        approver_id=row.approver_id,
        decision=PaymentApprovalDecision(row.decision),
        decision_reason=row.decision_reason,
        requested_at=row.requested_at,
        decided_at=row.decided_at,
    )


def _map_payment(row: PaymentRecordModel) -> PaymentRecordEntity:
    return PaymentRecordEntity(
        id=row.id,
        payment_number=row.payment_number,
        invoice_id=row.invoice_id,
        payment_direction=PaymentDirection(row.payment_direction),
        payer_party_id=row.payer_party_id,
        payee_party_id=row.payee_party_id,
        amount=row.amount,
        payment_date=row.payment_date,
        payment_method=PaymentMethod(row.payment_method),
        payment_reference=row.payment_reference,
        proof_file_id=row.proof_file_id,
        status=PaymentRecordStatus(row.status),
        recorded_by=row.recorded_by,
        verified_by=row.verified_by,
        verified_at=row.verified_at,
        created_at=row.created_at,
    )


def _map_invoice(row: InvoiceModel) -> InvoiceEntity:
    lines = tuple(
        InvoiceLineEntity(
            id=line.id,
            reference_type=line.reference_type,
            reference_id=line.reference_id,
            description=line.description,
            quantity=line.quantity,
            unit=line.unit,
            unit_price=line.unit_price,
            line_amount=line.line_amount,
        )
        for line in row.lines
    )
    approvals = tuple(_map_approval(a) for a in row.approvals)
    payments = tuple(_map_payment(p) for p in row.payments)
    return InvoiceEntity(
        id=row.id,
        invoice_number=row.invoice_number,
        invoice_type=InvoiceType(row.invoice_type),
        creditor_party_id=row.creditor_party_id,
        debtor_party_id=row.debtor_party_id,
        business_model_code=BusinessModelCode(row.business_model_code),
        business_model_rule_version_id=row.business_model_rule_version_id,
        reconciliation_case_id=row.reconciliation_case_id,
        invoice_date=row.invoice_date,
        due_date=row.due_date,
        gross_amount=row.gross_amount,
        deduction_amount=row.deduction_amount,
        total_amount=row.total_amount,
        status=InvoiceStatus(row.status),
        settlement_status=derive_settlement_status(
            invoice_total=row.total_amount,
            approvals=approvals,
            payments=payments,
        ),
        policy_classification=PolicyClassification(row.policy_classification),
        issued_at=row.issued_at,
        verified_by=row.verified_by,
        lines=lines,
        approvals=approvals,
        payments=payments,
        created_at=row.created_at,
    )


def _require_invoice(row: InvoiceModel | None) -> InvoiceEntity:
    if row is None:
        raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
    return _map_invoice(row)


async def _fetch_invoice(session: AsyncSession, invoice_id: UUID) -> InvoiceModel | None:
    stmt = (
        select(InvoiceModel)
        .options(
            selectinload(InvoiceModel.lines),
            selectinload(InvoiceModel.approvals),
            selectinload(InvoiceModel.payments),
        )
        .where(InvoiceModel.id == invoice_id)
    )
    return (await session.execute(stmt)).scalar_one_or_none()


async def _resolve_invoice_unit_price(
    session: AsyncSession,
    *,
    contract: TradeContractModel,
    mill_id: UUID,
    snapshot_at: datetime,
) -> Decimal:
    """Resolve price snapshot (FIXED contract or active PUBLISHED mill quote)."""
    if contract.price_rule_type == "FIXED" and contract.agreed_price_per_kg is not None:
        return contract.agreed_price_per_kg

    quote_price = (
        await session.execute(
            select(MillPriceQuoteModel.price_per_kg)
            .where(
                MillPriceQuoteModel.mill_id == mill_id,
                MillPriceQuoteModel.status == "PUBLISHED",
                MillPriceQuoteModel.effective_from <= snapshot_at,
                (
                    MillPriceQuoteModel.effective_until.is_(None)
                    | (MillPriceQuoteModel.effective_until >= snapshot_at)
                ),
            )
            .order_by(
                MillPriceQuoteModel.effective_from.desc(),
                MillPriceQuoteModel.published_at.desc(),
            )
            .limit(1)
        )
    ).scalar_one_or_none()
    if quote_price is not None:
        return quote_price

    if contract.agreed_price_per_kg is not None:
        return contract.agreed_price_per_kg

    raise AppError(
        ErrorCode.FIN_POLICY_UNCONFIRMED,
        details={"reason": "Harga kontrak atau kutipan PKS terbit belum tersedia."},
    )


async def _validate_ar_ap_parties(
    session: AsyncSession,
    *,
    invoice_type: InvoiceType,
    creditor_party_id: UUID,
    debtor_party_id: UUID,
    do: DeliveryOrderModel,
) -> None:
    creditor = await session.get(PartyModel, creditor_party_id)
    debtor = await session.get(PartyModel, debtor_party_id)
    if creditor is None or debtor is None:
        raise AppError(ErrorCode.PAY_INVALID_PARTY_PAIRING)

    if invoice_type == InvoiceType.ACCOUNTS_RECEIVABLE:
        mill = await session.get(MillModel, do.mill_id)
        if mill is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        mill_company = await session.get(MillCompanyModel, mill.mill_company_id)
        if (
            mill_company is None
            or creditor.party_type != PartyType.PERUMDA.value
            or debtor_party_id != mill_company.party_id
        ):
            raise AppError(ErrorCode.PAY_INVALID_PARTY_PAIRING)
        return

    coop = await session.get(CooperativeModel, do.cooperative_id)
    farmer_party_rows = (
        await session.execute(
            select(FarmerModel.party_id)
            .join(TbsReceiptModel, TbsReceiptModel.farmer_id == FarmerModel.id)
            .join(DeliveryOrderLineModel, DeliveryOrderLineModel.receipt_id == TbsReceiptModel.id)
            .where(
                DeliveryOrderLineModel.delivery_order_id == do.id,
                DeliveryOrderLineModel.allocation_status == "ACTIVE",
            )
        )
    ).scalars()
    allowed_ap_creditors = set(farmer_party_rows)
    if coop is not None:
        allowed_ap_creditors.add(coop.party_id)

    if (
        debtor.party_type != PartyType.PERUMDA.value
        or creditor_party_id not in allowed_ap_creditors
    ):
        raise AppError(ErrorCode.PAY_INVALID_PARTY_PAIRING)


def _derive_policy_classification(
    *, business_model_code: BusinessModelCode, rule_row: SystemRuleVersionModel | None
) -> PolicyClassification:
    if business_model_code == BusinessModelCode.UNCONFIRMED:
        return PolicyClassification.PENDING_SOP
    if rule_row is not None and rule_row.approval_status == "APPROVED":
        return PolicyClassification.CONFIRMED
    if rule_row is not None and rule_row.approval_status == "PENDING_SOP":
        return PolicyClassification.PENDING_SOP
    return PolicyClassification.SIMULATION_ONLY


class SqlAlchemyFinanceRepository:
    """PostgreSQL adapter implementing AR/AP Invoice, Payment Approval, & Payment Record ports."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def list_invoices(
        self,
        *,
        invoice_type: InvoiceType | None,
        status_filter: InvoiceStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[InvoiceEntity], int]:
        filters: list[Any] = []
        if invoice_type is not None:
            filters.append(InvoiceModel.invoice_type == invoice_type.value)
        if status_filter is not None:
            filters.append(InvoiceModel.status == status_filter.value)

        async with self._session_factory() as session:
            total = int(
                (
                    await session.execute(
                        select(func.count()).select_from(InvoiceModel).where(*filters)
                    )
                ).scalar_one()
            )
            stmt = (
                select(InvoiceModel)
                .options(
                    selectinload(InvoiceModel.lines),
                    selectinload(InvoiceModel.approvals),
                    selectinload(InvoiceModel.payments),
                )
                .where(*filters)
                .order_by(InvoiceModel.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return [_map_invoice(r) for r in rows], total

    async def get_invoice_by_id(self, invoice_id: UUID) -> InvoiceEntity | None:
        async with self._session_factory() as session:
            row = await _fetch_invoice(session, invoice_id)
            return _map_invoice(row) if row is not None else None

    async def create_invoice_draft(
        self,
        *,
        invoice_type: InvoiceType,
        creditor_party_id: UUID,
        debtor_party_id: UUID,
        reconciliation_case_id: UUID,
        invoice_date: date,
        due_date: date | None,
        actor_id: UUID,
    ) -> InvoiceEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                case = (
                    await session.execute(
                        select(ReconciliationCaseModel)
                        .where(ReconciliationCaseModel.id == reconciliation_case_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if case is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                if not case.is_current or case.status not in ("MATCHED", "RESOLVED"):
                    raise AppError(
                        ErrorCode.FIN_DISPUTE_HOLD_BLOCKED,
                        details={"reconciliation_status": case.status},
                    )

                do = await session.get(DeliveryOrderModel, case.delivery_order_id)
                if do is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                contract = await session.get(TradeContractModel, do.contract_id)
                if contract is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)

                await _validate_ar_ap_parties(
                    session,
                    invoice_type=invoice_type,
                    creditor_party_id=creditor_party_id,
                    debtor_party_id=debtor_party_id,
                    do=do,
                )

                snapshot_time = do.issued_at or case.calculated_at or now
                unit_price = await _resolve_invoice_unit_price(
                    session, contract=contract, mill_id=do.mill_id, snapshot_at=snapshot_time
                )
                qty_kg = case.agreed_settlement_weight_kg or case.mill_weight_kg
                line_amount = compute_line_amount(quantity_kg=qty_kg, unit_price=unit_price)

                rule_row = await session.get(
                    SystemRuleVersionModel, contract.business_model_rule_version
                )
                bmc = BusinessModelCode(contract.business_model_code)
                policy_cls = _derive_policy_classification(
                    business_model_code=bmc, rule_row=rule_row
                )

                seq = int(
                    (await session.execute(text("SELECT nextval('invoice_seq')"))).scalar_one()
                )
                kind_code = "AR" if invoice_type == InvoiceType.ACCOUNTS_RECEIVABLE else "AP"
                inv_number = f"INV-{kind_code}-{invoice_date:%Y%m}-{seq:05d}"

                inv = InvoiceModel(
                    id=uuid4(),
                    invoice_number=inv_number,
                    invoice_type=invoice_type.value,
                    creditor_party_id=creditor_party_id,
                    debtor_party_id=debtor_party_id,
                    business_model_code=bmc.value,
                    business_model_rule_version_id=contract.business_model_rule_version,
                    reconciliation_case_id=case.id,
                    invoice_date=invoice_date,
                    due_date=due_date,
                    gross_amount=line_amount,
                    deduction_amount=Decimal("0.00"),
                    total_amount=line_amount,
                    status=InvoiceStatus.PENDING_VERIFICATION.value,
                    policy_classification=policy_cls.value,
                    issued_at=None,
                    created_by=actor_id,
                    verified_by=None,
                    verified_at=None,
                    verification_reason=None,
                    version=1,
                    created_at=now,
                    updated_at=now,
                )
                session.add(inv)
                try:
                    await session.flush()
                except IntegrityError as exc:
                    raise AppError(
                        ErrorCode.PAY_DUPLICATE_PAYMENT,
                        details={"invoice_type": invoice_type.value},
                    ) from exc

                desc_prefix = (
                    "Tagihan Penjualan TBS"
                    if invoice_type == InvoiceType.ACCOUNTS_RECEIVABLE
                    else "Kewajiban Pembelian TBS"
                )
                session.add(
                    InvoiceLineModel(
                        id=uuid4(),
                        invoice_id=inv.id,
                        reference_type="RECONCILIATION_CASE",
                        reference_id=case.id,
                        reconciliation_case_id=case.id,
                        description=(
                            f"{desc_prefix} e-DO {do.delivery_order_number} ({qty_kg:.3f} kg)"
                        ),
                        quantity=qty_kg,
                        unit="kg",
                        unit_price=unit_price,
                        line_amount=line_amount,
                        created_at=now,
                    )
                )
                await session.flush()

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="INVOICE_DRAFT_CREATED",
                        module="finance",
                        resource_type="invoices",
                        resource_id=str(inv.id),
                        new_state={
                            "invoice_number": inv.invoice_number,
                            "invoice_type": inv.invoice_type,
                            "total_amount": f"{line_amount:.2f}",
                            "unit_price": f"{unit_price:.2f}",
                            "status": inv.status,
                        },
                    ),
                )
                inv_id = inv.id

        async with self._session_factory() as read_session:
            return _require_invoice(await _fetch_invoice(read_session, inv_id))

    async def verify_invoice(
        self,
        *,
        invoice_id: UUID,
        decision: str,
        reason: str | None,
        actor_id: UUID,
        non_approver_admin: bool,
    ) -> InvoiceEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                inv = (
                    await session.execute(
                        select(InvoiceModel).where(InvoiceModel.id == invoice_id).with_for_update()
                    )
                ).scalar_one_or_none()
                if inv is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)

                prev_status = inv.status
                assert_can_verify_invoice(
                    current_status=InvoiceStatus(prev_status),
                    created_by=inv.created_by,
                    actor_id=actor_id,
                    non_approver_admin=non_approver_admin,
                    decision=decision,
                    reason=reason,
                )

                inv.status = (
                    InvoiceStatus.VERIFIED.value
                    if decision == "APPROVE"
                    else InvoiceStatus.REJECTED.value
                )
                inv.verified_by = actor_id
                inv.verified_at = now
                inv.verification_reason = reason
                inv.version += 1
                inv.updated_at = now

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="INVOICE_VERIFIED"
                        if decision == "APPROVE"
                        else "INVOICE_REJECTED",
                        module="finance",
                        resource_type="invoices",
                        resource_id=str(inv.id),
                        previous_state={"status": prev_status},
                        new_state={"status": inv.status},
                        reason=reason,
                    ),
                )

        async with self._session_factory() as read_session:
            return _require_invoice(await _fetch_invoice(read_session, invoice_id))

    async def issue_invoice(
        self,
        *,
        invoice_id: UUID,
        actor_id: UUID,
    ) -> InvoiceEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                inv = (
                    await session.execute(
                        select(InvoiceModel).where(InvoiceModel.id == invoice_id).with_for_update()
                    )
                ).scalar_one_or_none()
                if inv is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)

                rec_status: str | None = None
                if inv.reconciliation_case_id is not None:
                    case = await session.get(ReconciliationCaseModel, inv.reconciliation_case_id)
                    if case is None:
                        raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                    rec_status = case.status

                assert_can_issue_invoice(
                    current_status=InvoiceStatus(inv.status),
                    business_model_code=BusinessModelCode(inv.business_model_code),
                    reconciliation_status=rec_status,
                )

                prev_status = inv.status
                inv.status = InvoiceStatus.ISSUED.value
                inv.issued_at = now
                inv.version += 1
                inv.updated_at = now

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="INVOICE_ISSUED",
                        module="finance",
                        resource_type="invoices",
                        resource_id=str(inv.id),
                        previous_state={"status": prev_status},
                        new_state={
                            "status": inv.status,
                            "business_model_code": inv.business_model_code,
                            "total_amount": f"{inv.total_amount:.2f}",
                        },
                    ),
                )

        async with self._session_factory() as read_session:
            return _require_invoice(await _fetch_invoice(read_session, invoice_id))

    async def get_approval_by_id(self, approval_id: UUID) -> PaymentApprovalEntity | None:
        async with self._session_factory() as session:
            row = await session.get(PaymentApprovalModel, approval_id)
            return _map_approval(row) if row is not None else None

    async def approve_payment(
        self,
        *,
        invoice_id: UUID,
        decision: PaymentApprovalDecision,
        reason: str,
        actor_id: UUID,
        non_approver_admin: bool,
        idempotency_record_id: UUID,
    ) -> PaymentApprovalEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                inv = (
                    await session.execute(
                        select(InvoiceModel)
                        .options(selectinload(InvoiceModel.approvals))
                        .where(InvoiceModel.id == invoice_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if inv is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)

                rec_status: str | None = None
                if inv.reconciliation_case_id is not None:
                    case = await session.get(ReconciliationCaseModel, inv.reconciliation_case_id)
                    rec_status = case.status if case is not None else None

                existing_entities = [_map_approval(a) for a in inv.approvals]
                assert_can_approve_payment(
                    invoice_status=InvoiceStatus(inv.status),
                    business_model_code=BusinessModelCode(inv.business_model_code),
                    reconciliation_status=rec_status,
                    existing_approvals=existing_entities,
                    requested_by=inv.created_by,
                    actor_id=actor_id,
                    non_approver_admin=non_approver_admin,
                )

                approval = PaymentApprovalModel(
                    id=uuid4(),
                    invoice_id=inv.id,
                    requested_by=inv.created_by,
                    approver_id=actor_id,
                    decision=decision.value,
                    decision_reason=reason,
                    requested_at=inv.created_at,
                    decided_at=now,
                    idempotency_record_id=idempotency_record_id,
                )
                session.add(approval)
                await session.flush()

                await complete_idempotency_slot(
                    session,
                    record_id=idempotency_record_id,
                    response_reference=approval.id,
                    response_payload={
                        "approval_id": str(approval.id),
                        "decision": approval.decision,
                    },
                )

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="PAYMENT_OBLIGATION_DECIDED",
                        module="finance",
                        resource_type="payment_approvals",
                        resource_id=str(approval.id),
                        new_state={
                            "invoice_id": str(inv.id),
                            "decision": approval.decision,
                            "note": "APPROVED != PAID",
                        },
                        reason=reason,
                    ),
                )
                return _map_approval(approval)

    async def list_payments(
        self,
        *,
        allowed_farmer_ids: set[UUID] | None,
        allowed_cooperative_ids: set[UUID] | None,
        payment_direction: PaymentDirection | None,
        status_filter: PaymentRecordStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[PaymentRecordEntity], int]:
        filters: list[Any] = []
        if payment_direction is not None:
            filters.append(PaymentRecordModel.payment_direction == payment_direction.value)
        if status_filter is not None:
            filters.append(PaymentRecordModel.status == status_filter.value)

        async with self._session_factory() as session:
            if allowed_farmer_ids is not None:
                if not allowed_farmer_ids:
                    return [], 0
                farmer_parties = list(
                    (
                        await session.execute(
                            select(FarmerModel.party_id).where(
                                FarmerModel.id.in_(allowed_farmer_ids)
                            )
                        )
                    ).scalars()
                )
                if not farmer_parties:
                    return [], 0
                filters.append(
                    PaymentRecordModel.payment_direction == PaymentDirection.OUTBOUND.value
                )
                filters.append(PaymentRecordModel.payee_party_id.in_(farmer_parties))
            elif allowed_cooperative_ids is not None:
                if not allowed_cooperative_ids:
                    return [], 0
                coop_parties = list(
                    (
                        await session.execute(
                            select(CooperativeModel.party_id).where(
                                CooperativeModel.id.in_(allowed_cooperative_ids)
                            )
                        )
                    ).scalars()
                )
                if not coop_parties:
                    return [], 0
                filters.append(
                    PaymentRecordModel.payment_direction == PaymentDirection.OUTBOUND.value
                )
                filters.append(PaymentRecordModel.payee_party_id.in_(coop_parties))

            total = int(
                (
                    await session.execute(
                        select(func.count()).select_from(PaymentRecordModel).where(*filters)
                    )
                ).scalar_one()
            )
            rows = (
                (
                    await session.execute(
                        select(PaymentRecordModel)
                        .where(*filters)
                        .order_by(PaymentRecordModel.created_at.desc())
                        .offset((page - 1) * page_size)
                        .limit(page_size)
                    )
                )
                .scalars()
                .all()
            )
            return [_map_payment(r) for r in rows], total

    async def get_payment_by_id(self, payment_id: UUID) -> PaymentRecordEntity | None:
        async with self._session_factory() as session:
            row = await session.get(PaymentRecordModel, payment_id)
            return _map_payment(row) if row is not None else None

    async def record_payment(
        self,
        *,
        invoice_id: UUID,
        payment_direction: PaymentDirection,
        payer_party_id: UUID,
        payee_party_id: UUID,
        amount: Decimal,
        payment_date: date,
        payment_method: PaymentMethod,
        payment_reference: str,
        proof_file_id: UUID,
        actor_id: UUID,
        idempotency_record_id: UUID,
    ) -> PaymentRecordEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                inv = (
                    await session.execute(
                        select(InvoiceModel)
                        .options(
                            selectinload(InvoiceModel.approvals),
                            selectinload(InvoiceModel.payments),
                        )
                        .where(InvoiceModel.id == invoice_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if inv is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)

                proof = await session.get(FileAssetModel, proof_file_id)
                if proof is None:
                    raise AppError(ErrorCode.PAY_PROOF_REQUIRED)

                approvals = [_map_approval(a) for a in inv.approvals]
                payments = [_map_payment(p) for p in inv.payments]
                settlement_status = derive_settlement_status(
                    invoice_total=inv.total_amount,
                    approvals=approvals,
                    payments=payments,
                )
                has_approved = any(
                    a.decision == PaymentApprovalDecision.APPROVED for a in approvals
                )

                validate_payment_submission(
                    invoice_type=InvoiceType(inv.invoice_type),
                    invoice_status=InvoiceStatus(inv.status),
                    business_model_code=BusinessModelCode(inv.business_model_code),
                    creditor_party_id=inv.creditor_party_id,
                    debtor_party_id=inv.debtor_party_id,
                    invoice_total=inv.total_amount,
                    settlement_status=settlement_status,
                    has_approved_obligation=has_approved,
                    payment_direction=payment_direction,
                    payer_party_id=payer_party_id,
                    payee_party_id=payee_party_id,
                    submitted_amount=amount,
                )

                if any(
                    p.status
                    in (PaymentRecordStatus.PENDING_VERIFICATION, PaymentRecordStatus.VERIFIED)
                    for p in payments
                ):
                    raise AppError(ErrorCode.PAY_DUPLICATE_PAYMENT)

                seq = int(
                    (await session.execute(text("SELECT nextval('payment_seq')"))).scalar_one()
                )
                dir_code = "IN" if payment_direction == PaymentDirection.INBOUND else "OUT"
                payment_number = f"PAY-{dir_code}-{payment_date:%Y%m}-{seq:05d}"

                rec = PaymentRecordModel(
                    id=uuid4(),
                    payment_number=payment_number,
                    invoice_id=inv.id,
                    payment_direction=payment_direction.value,
                    payer_party_id=payer_party_id,
                    payee_party_id=payee_party_id,
                    amount=amount,
                    payment_date=payment_date,
                    payment_method=payment_method.value,
                    payment_reference=payment_reference,
                    proof_file_id=proof_file_id,
                    status=PaymentRecordStatus.PENDING_VERIFICATION.value,
                    recorded_by=actor_id,
                    verified_by=None,
                    verified_at=None,
                    decision_reason=None,
                    idempotency_record_id=idempotency_record_id,
                    created_at=now,
                )
                session.add(rec)
                try:
                    await session.flush()
                except IntegrityError as exc:
                    raise AppError(ErrorCode.PAY_DUPLICATE_PAYMENT) from exc

                await complete_idempotency_slot(
                    session,
                    record_id=idempotency_record_id,
                    response_reference=rec.id,
                    response_payload={
                        "payment_id": str(rec.id),
                        "payment_number": rec.payment_number,
                        "status": rec.status,
                    },
                )

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="PAYMENT_EVIDENCE_RECORDED",
                        module="finance",
                        resource_type="payment_records",
                        resource_id=str(rec.id),
                        new_state={
                            "payment_number": rec.payment_number,
                            "invoice_id": str(inv.id),
                            "amount": f"{amount:.2f}",
                            "status": rec.status,
                        },
                    ),
                )
                return _map_payment(rec)

    async def verify_payment_record(
        self,
        *,
        payment_id: UUID,
        decision: PaymentRecordStatus,
        reason: str | None,
        actor_id: UUID,
        non_approver_admin: bool,
    ) -> PaymentRecordEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                rec = (
                    await session.execute(
                        select(PaymentRecordModel)
                        .where(PaymentRecordModel.id == payment_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if rec is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)

                prev_status = rec.status
                assert_can_verify_payment_record(
                    current_status=PaymentRecordStatus(prev_status),
                    decision=decision,
                    recorded_by=rec.recorded_by,
                    actor_id=actor_id,
                    non_approver_admin=non_approver_admin,
                    has_proof_file=(rec.proof_file_id is not None),
                    reason=reason,
                )

                rec.status = decision.value
                rec.verified_by = actor_id
                rec.verified_at = now
                rec.decision_reason = reason
                await session.flush()

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type=f"PAYMENT_RECORD_{decision.value}",
                        module="finance",
                        resource_type="payment_records",
                        resource_id=str(rec.id),
                        previous_state={"status": prev_status},
                        new_state={"status": rec.status},
                        reason=reason,
                    ),
                )
                return _map_payment(rec)
