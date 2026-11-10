"""Strict OpenAPI 3.1.0 request/response DTOs for /api/v1/invoices* & /api/v1/payments*."""

from __future__ import annotations

from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.logging import format_utc_iso
from app.core.schemas import PaginationMeta, SimpleSuccessMeta, StrictContractModel, format_decimal
from app.modules.contracts.domain.entities import BusinessModelCode, PolicyClassification
from app.modules.finance.domain.entities import (
    InvoiceEntity,
    InvoiceStatus,
    InvoiceType,
    PaymentApprovalDecision,
    PaymentApprovalEntity,
    PaymentDirection,
    PaymentMethod,
    PaymentRecordEntity,
    PaymentRecordStatus,
    SettlementStatus,
)


class InvoiceLineDto(StrictContractModel):
    id: str
    reference_type: Literal["RECONCILIATION_CASE", "DELIVERY_ORDER_LINE", "FEE_ADJUSTMENT"]
    reference_id: str
    description: str
    quantity: str
    unit: str
    unit_price: str
    line_amount: str


class PaymentApprovalDto(StrictContractModel):
    id: str
    requested_by: str
    approver_id: str | None
    decision: PaymentApprovalDecision
    decision_reason: str | None
    requested_at: str
    decided_at: str | None


class PaymentRecordDto(StrictContractModel):
    id: str
    payment_number: str
    invoice_id: str
    payment_direction: PaymentDirection
    payer_party_id: str
    payee_party_id: str
    amount: str
    payment_date: str
    payment_method: PaymentMethod
    payment_reference: str
    proof_file_id: str | None
    status: PaymentRecordStatus
    recorded_by: str
    verified_by: str | None
    verified_at: str | None
    created_at: str


class InvoiceDto(StrictContractModel):
    id: str
    invoice_number: str
    invoice_type: InvoiceType
    creditor_party_id: str
    debtor_party_id: str
    business_model_code: BusinessModelCode
    business_model_rule_version_id: str
    reconciliation_case_id: str | None
    invoice_date: str
    due_date: str | None
    gross_amount: str
    deduction_amount: str
    total_amount: str
    status: InvoiceStatus
    settlement_status: SettlementStatus
    policy_classification: PolicyClassification
    issued_at: str | None
    verified_by: str | None
    lines: list[InvoiceLineDto]
    approvals: list[PaymentApprovalDto]
    payments: list[PaymentRecordDto]
    created_at: str


class CreateInvoiceDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    invoice_type: InvoiceType
    creditor_party_id: UUID
    debtor_party_id: UUID
    reconciliation_case_id: UUID
    invoice_date: date
    due_date: date | None = None


class VerifyInvoiceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: Literal["APPROVE", "REJECT"]
    reason: str | None = Field(default=None, max_length=1000)


class ApprovePaymentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: Literal["APPROVED", "REJECTED"]
    reason: str = Field(min_length=5, max_length=500)


class RecordPaymentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    invoice_id: UUID
    payment_direction: PaymentDirection
    payer_party_id: UUID
    payee_party_id: UUID
    amount: str = Field(max_length=32)
    payment_date: date
    payment_method: PaymentMethod
    payment_reference: str = Field(min_length=3, max_length=100)
    proof_file_id: UUID


class VerifyPaymentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: Literal["VERIFIED", "REJECTED", "REVERSED"]
    reason: str | None = Field(default=None, max_length=1000)


class InvoiceListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[InvoiceDto]
    meta: PaginationMeta
    request_id: str


class InvoiceEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: InvoiceDto
    meta: SimpleSuccessMeta
    request_id: str


class PaymentListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[PaymentRecordDto]
    meta: PaginationMeta
    request_id: str


class PaymentApprovalEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: PaymentApprovalDto
    meta: SimpleSuccessMeta
    request_id: str


class PaymentRecordEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: PaymentRecordDto
    meta: SimpleSuccessMeta
    request_id: str


def approval_to_dto(entity: PaymentApprovalEntity) -> PaymentApprovalDto:
    return PaymentApprovalDto(
        id=str(entity.id),
        requested_by=str(entity.requested_by),
        approver_id=str(entity.approver_id) if entity.approver_id else None,
        decision=entity.decision,
        decision_reason=entity.decision_reason,
        requested_at=format_utc_iso(entity.requested_at) or "",
        decided_at=format_utc_iso(entity.decided_at) if entity.decided_at else None,
    )


def payment_to_dto(entity: PaymentRecordEntity) -> PaymentRecordDto:
    return PaymentRecordDto(
        id=str(entity.id),
        payment_number=entity.payment_number,
        invoice_id=str(entity.invoice_id),
        payment_direction=entity.payment_direction,
        payer_party_id=str(entity.payer_party_id),
        payee_party_id=str(entity.payee_party_id),
        amount=format_decimal(entity.amount, 2) or "0.00",
        payment_date=entity.payment_date.isoformat(),
        payment_method=entity.payment_method,
        payment_reference=entity.payment_reference,
        proof_file_id=str(entity.proof_file_id) if entity.proof_file_id else None,
        status=entity.status,
        recorded_by=str(entity.recorded_by),
        verified_by=str(entity.verified_by) if entity.verified_by else None,
        verified_at=format_utc_iso(entity.verified_at) if entity.verified_at else None,
        created_at=format_utc_iso(entity.created_at) or "",
    )


def invoice_to_dto(entity: InvoiceEntity) -> InvoiceDto:
    return InvoiceDto(
        id=str(entity.id),
        invoice_number=entity.invoice_number,
        invoice_type=entity.invoice_type,
        creditor_party_id=str(entity.creditor_party_id),
        debtor_party_id=str(entity.debtor_party_id),
        business_model_code=entity.business_model_code,
        business_model_rule_version_id=str(entity.business_model_rule_version_id),
        reconciliation_case_id=(
            str(entity.reconciliation_case_id) if entity.reconciliation_case_id else None
        ),
        invoice_date=entity.invoice_date.isoformat(),
        due_date=entity.due_date.isoformat() if entity.due_date else None,
        gross_amount=format_decimal(entity.gross_amount, 2) or "0.00",
        deduction_amount=format_decimal(entity.deduction_amount, 2) or "0.00",
        total_amount=format_decimal(entity.total_amount, 2) or "0.00",
        status=entity.status,
        settlement_status=entity.settlement_status,
        policy_classification=entity.policy_classification,
        issued_at=format_utc_iso(entity.issued_at) if entity.issued_at else None,
        verified_by=str(entity.verified_by) if entity.verified_by else None,
        lines=[
            InvoiceLineDto(
                id=str(line.id),
                reference_type=(
                    line.reference_type
                    if line.reference_type
                    in ("RECONCILIATION_CASE", "DELIVERY_ORDER_LINE", "FEE_ADJUSTMENT")
                    else "RECONCILIATION_CASE"
                ),
                reference_id=str(line.reference_id),
                description=line.description,
                quantity=format_decimal(line.quantity, 3) or "0.000",
                unit=line.unit,
                unit_price=format_decimal(line.unit_price, 2) or "0.00",
                line_amount=format_decimal(line.line_amount, 2) or "0.00",
            )
            for line in entity.lines
        ],
        approvals=[approval_to_dto(a) for a in entity.approvals],
        payments=[payment_to_dto(p) for p in entity.payments],
        created_at=format_utc_iso(entity.created_at) or "",
    )
