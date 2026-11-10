"""Domain entities and enums for Invoices SM-09, Payment Approvals SM-10, and Records SM-11."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from app.modules.contracts.domain.entities import BusinessModelCode, PolicyClassification


class InvoiceType(StrEnum):
    ACCOUNTS_RECEIVABLE = "ACCOUNTS_RECEIVABLE"
    ACCOUNTS_PAYABLE = "ACCOUNTS_PAYABLE"


class InvoiceStatus(StrEnum):
    DRAFT = "DRAFT"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    VERIFIED = "VERIFIED"
    ISSUED = "ISSUED"
    REJECTED = "REJECTED"
    VOID = "VOID"


class SettlementStatus(StrEnum):
    UNPAID = "UNPAID"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED_UNPAID = "APPROVED_UNPAID"
    AWAITING_PAYMENT = "AWAITING_PAYMENT"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    PAID = "PAID"


class PaymentDirection(StrEnum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class PaymentMethod(StrEnum):
    BANK_TRANSFER_MANUAL = "BANK_TRANSFER_MANUAL"
    CASH_RECEIPT = "CASH_RECEIPT"
    OTHER_VERIFIED = "OTHER_VERIFIED"


class PaymentApprovalDecision(StrEnum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class PaymentRecordStatus(StrEnum):
    DRAFT = "DRAFT"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    REVERSED = "REVERSED"


@dataclass(frozen=True, slots=True)
class InvoiceLineEntity:
    id: UUID
    reference_type: str
    reference_id: UUID
    description: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    line_amount: Decimal


@dataclass(frozen=True, slots=True)
class PaymentApprovalEntity:
    id: UUID
    requested_by: UUID
    approver_id: UUID | None
    decision: PaymentApprovalDecision
    decision_reason: str | None
    requested_at: datetime
    decided_at: datetime | None


@dataclass(frozen=True, slots=True)
class PaymentRecordEntity:
    id: UUID
    payment_number: str
    invoice_id: UUID
    payment_direction: PaymentDirection
    payer_party_id: UUID
    payee_party_id: UUID
    amount: Decimal
    payment_date: date
    payment_method: PaymentMethod
    payment_reference: str
    proof_file_id: UUID | None
    status: PaymentRecordStatus
    recorded_by: UUID
    verified_by: UUID | None
    verified_at: datetime | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class InvoiceEntity:
    id: UUID
    invoice_number: str
    invoice_type: InvoiceType
    creditor_party_id: UUID
    debtor_party_id: UUID
    business_model_code: BusinessModelCode
    business_model_rule_version_id: UUID
    reconciliation_case_id: UUID | None
    invoice_date: date
    due_date: date | None
    gross_amount: Decimal
    deduction_amount: Decimal
    total_amount: Decimal
    status: InvoiceStatus
    settlement_status: SettlementStatus
    policy_classification: PolicyClassification
    issued_at: datetime | None
    verified_by: UUID | None
    lines: tuple[InvoiceLineEntity, ...]
    approvals: tuple[PaymentApprovalEntity, ...]
    payments: tuple[PaymentRecordEntity, ...]
    created_at: datetime
