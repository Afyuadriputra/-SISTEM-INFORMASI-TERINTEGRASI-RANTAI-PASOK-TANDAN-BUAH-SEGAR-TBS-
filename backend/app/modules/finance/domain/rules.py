"""Pure financial calculations and SM-09 / SM-10 / SM-11 / SOD-04..06 invariants."""

from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from uuid import UUID

from app.core.exceptions import AppError, ErrorCode
from app.modules.contracts.domain.entities import BusinessModelCode
from app.modules.finance.domain.entities import (
    InvoiceStatus,
    InvoiceType,
    PaymentApprovalDecision,
    PaymentApprovalEntity,
    PaymentDirection,
    PaymentRecordEntity,
    PaymentRecordStatus,
    SettlementStatus,
)

_MONEY_RE = re.compile(r"^-?\d{1,18}\.\d{2}$")


def parse_money_amount(raw_value: str, *, field_name: str = "amount") -> Decimal:
    cleaned = raw_value.strip()
    if not _MONEY_RE.match(cleaned):
        raise AppError(
            ErrorCode.VAL_INVALID_DECIMAL_PRECISION,
            details=[
                {
                    "field": field_name,
                    "reason": "Gunakan format nominal IDR 2 angka di belakang koma.",
                    "code": ErrorCode.VAL_INVALID_DECIMAL_PRECISION.value,
                }
            ],
        )
    try:
        val = Decimal(cleaned)
    except InvalidOperation as exc:
        raise AppError(ErrorCode.VAL_INVALID_DECIMAL_PRECISION) from exc
    if not val.is_finite() or val <= Decimal("0"):
        raise AppError(
            ErrorCode.PAY_AMOUNT_EXCEEDS_INVOICE,
            details=[
                {
                    "field": field_name,
                    "reason": "Nominal pembayaran harus lebih besar dari nol.",
                    "code": ErrorCode.PAY_AMOUNT_EXCEEDS_INVOICE.value,
                }
            ],
        )
    return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def compute_line_amount(*, quantity_kg: Decimal, unit_price: Decimal) -> Decimal:
    return (quantity_kg * unit_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def derive_settlement_status(
    *,
    invoice_total: Decimal,
    approvals: tuple[PaymentApprovalEntity, ...] | list[PaymentApprovalEntity],
    payments: tuple[PaymentRecordEntity, ...] | list[PaymentRecordEntity],
) -> SettlementStatus:
    """Compute PAID only from VERIFIED non-reversed payments matching total_amount (BR-PAY-010)."""
    verified_total = sum(
        (p.amount for p in payments if p.status == PaymentRecordStatus.VERIFIED),
        start=Decimal("0.00"),
    )
    if invoice_total > Decimal("0.00") and verified_total >= invoice_total:
        return SettlementStatus.PAID
    if any(p.status == PaymentRecordStatus.PENDING_VERIFICATION for p in payments):
        return SettlementStatus.PENDING_VERIFICATION
    if any(a.decision == PaymentApprovalDecision.APPROVED for a in approvals):
        return SettlementStatus.AWAITING_PAYMENT
    if any(a.decision == PaymentApprovalDecision.PENDING_APPROVAL for a in approvals):
        return SettlementStatus.PENDING_APPROVAL
    return SettlementStatus.UNPAID


def assert_can_verify_invoice(
    *,
    current_status: InvoiceStatus,
    created_by: UUID,
    actor_id: UUID,
    non_approver_admin: bool,
    decision: str,
    reason: str | None,
) -> None:
    if non_approver_admin:
        raise AppError(ErrorCode.AUTH_OPERATION_FORBIDDEN)
    if created_by == actor_id:
        raise AppError(ErrorCode.AUTH_CONFLICT_OF_DUTIES, details={"sod_rule": "SOD-04"})
    if current_status != InvoiceStatus.PENDING_VERIFICATION:
        raise AppError(
            ErrorCode.FIN_INVOICE_NOT_VERIFIED,
            details={"invoice_status": current_status.value},
        )
    if decision == "REJECT" and (not reason or len(reason.strip()) < 5):
        raise AppError(ErrorCode.VAL_REQUIRED_FIELD)


def assert_can_issue_invoice(
    *,
    current_status: InvoiceStatus,
    business_model_code: BusinessModelCode,
    reconciliation_status: str | None,
) -> None:
    if current_status != InvoiceStatus.VERIFIED:
        raise AppError(
            ErrorCode.FIN_INVOICE_NOT_VERIFIED,
            details={"invoice_status": current_status.value},
        )
    if reconciliation_status is not None and reconciliation_status not in ("MATCHED", "RESOLVED"):
        raise AppError(
            ErrorCode.FIN_DISPUTE_HOLD_BLOCKED,
            details={"reconciliation_status": reconciliation_status},
        )
    if business_model_code == BusinessModelCode.UNCONFIRMED:
        raise AppError(
            ErrorCode.FIN_POLICY_UNCONFIRMED,
            details={
                "business_model_code": BusinessModelCode.UNCONFIRMED.value,
                "pending_decision_id": "BSD-DEC-001",
            },
        )


def assert_can_approve_payment(
    *,
    invoice_status: InvoiceStatus,
    business_model_code: BusinessModelCode,
    reconciliation_status: str | None,
    existing_approvals: list[PaymentApprovalEntity],
    requested_by: UUID,
    actor_id: UUID,
    non_approver_admin: bool,
) -> None:
    if non_approver_admin:
        raise AppError(ErrorCode.AUTH_OPERATION_FORBIDDEN)
    if requested_by == actor_id:
        raise AppError(ErrorCode.AUTH_CONFLICT_OF_DUTIES, details={"sod_rule": "SOD-05"})
    if invoice_status != InvoiceStatus.ISSUED:
        raise AppError(
            ErrorCode.FIN_INVOICE_NOT_VERIFIED,
            details={"invoice_status": invoice_status.value},
        )
    if reconciliation_status is not None and reconciliation_status not in ("MATCHED", "RESOLVED"):
        raise AppError(
            ErrorCode.FIN_DISPUTE_HOLD_BLOCKED,
            details={"reconciliation_status": reconciliation_status},
        )
    if business_model_code == BusinessModelCode.UNCONFIRMED:
        raise AppError(
            ErrorCode.FIN_POLICY_UNCONFIRMED,
            details={
                "business_model_code": BusinessModelCode.UNCONFIRMED.value,
                "pending_decision_id": "BSD-DEC-001",
            },
        )
    if any(
        a.decision in (PaymentApprovalDecision.APPROVED, PaymentApprovalDecision.REJECTED)
        for a in existing_approvals
    ):
        raise AppError(ErrorCode.PAY_ALREADY_APPROVED)


def validate_payment_submission(
    *,
    invoice_type: InvoiceType,
    invoice_status: InvoiceStatus,
    business_model_code: BusinessModelCode,
    creditor_party_id: UUID,
    debtor_party_id: UUID,
    invoice_total: Decimal,
    settlement_status: SettlementStatus,
    has_approved_obligation: bool,
    payment_direction: PaymentDirection,
    payer_party_id: UUID,
    payee_party_id: UUID,
    submitted_amount: Decimal,
) -> None:
    if invoice_status != InvoiceStatus.ISSUED:
        raise AppError(
            ErrorCode.FIN_INVOICE_NOT_VERIFIED,
            details={"invoice_status": invoice_status.value},
        )
    if business_model_code == BusinessModelCode.UNCONFIRMED:
        raise AppError(
            ErrorCode.FIN_POLICY_UNCONFIRMED,
            details={
                "business_model_code": BusinessModelCode.UNCONFIRMED.value,
                "pending_decision_id": "BSD-DEC-001",
            },
        )
    if settlement_status == SettlementStatus.PAID:
        raise AppError(ErrorCode.PAY_DUPLICATE_PAYMENT)

    expected_dir = (
        PaymentDirection.INBOUND
        if invoice_type == InvoiceType.ACCOUNTS_RECEIVABLE
        else PaymentDirection.OUTBOUND
    )
    if (
        payment_direction != expected_dir
        or payer_party_id != debtor_party_id
        or payee_party_id != creditor_party_id
    ):
        raise AppError(
            ErrorCode.PAY_INVALID_PARTY_PAIRING,
            details=[
                {
                    "field": "payment_direction",
                    "reason": "Arah dana dan pasangan pembayar/penerima tidak cocok dengan faktur.",
                    "code": ErrorCode.PAY_INVALID_PARTY_PAIRING.value,
                }
            ],
        )

    if payment_direction == PaymentDirection.OUTBOUND and not has_approved_obligation:
        raise AppError(ErrorCode.PAY_APPROVAL_REQUIRED)

    if submitted_amount > invoice_total:
        raise AppError(
            ErrorCode.PAY_AMOUNT_EXCEEDS_INVOICE,
            details=[
                {
                    "field": "amount",
                    "reason": "Nominal pembayaran melebihi kewajiban total faktur.",
                    "code": ErrorCode.PAY_AMOUNT_EXCEEDS_INVOICE.value,
                }
            ],
        )
    if submitted_amount < invoice_total:
        raise AppError(
            ErrorCode.PAY_PARTIAL_NOT_SUPPORTED,
            details={
                "invoice_total_amount": f"{invoice_total:.2f}",
                "submitted_amount": f"{submitted_amount:.2f}",
            },
        )


def assert_can_verify_payment_record(
    *,
    current_status: PaymentRecordStatus,
    decision: PaymentRecordStatus,
    recorded_by: UUID,
    actor_id: UUID,
    non_approver_admin: bool,
    has_proof_file: bool,
    reason: str | None,
) -> None:
    if non_approver_admin:
        raise AppError(ErrorCode.AUTH_OPERATION_FORBIDDEN)
    if recorded_by == actor_id:
        raise AppError(ErrorCode.AUTH_CONFLICT_OF_DUTIES, details={"sod_rule": "SOD-06"})
    if decision not in (
        PaymentRecordStatus.VERIFIED,
        PaymentRecordStatus.REJECTED,
        PaymentRecordStatus.REVERSED,
    ):
        raise AppError(
            ErrorCode.PAY_INVALID_STATE_TRANSITION,
            details={"current_status": current_status.value},
        )
    if decision in (PaymentRecordStatus.VERIFIED, PaymentRecordStatus.REJECTED):
        if current_status != PaymentRecordStatus.PENDING_VERIFICATION:
            raise AppError(
                ErrorCode.PAY_INVALID_STATE_TRANSITION,
                details={"current_status": current_status.value},
            )
    if decision == PaymentRecordStatus.REVERSED:
        if current_status != PaymentRecordStatus.VERIFIED:
            raise AppError(
                ErrorCode.PAY_INVALID_STATE_TRANSITION,
                details={"current_status": current_status.value},
            )
        if not reason or len(reason.strip()) < 5:
            raise AppError(ErrorCode.VAL_REQUIRED_FIELD)
    if decision == PaymentRecordStatus.VERIFIED and not has_proof_file:
        raise AppError(ErrorCode.PAY_PROOF_REQUIRED)
