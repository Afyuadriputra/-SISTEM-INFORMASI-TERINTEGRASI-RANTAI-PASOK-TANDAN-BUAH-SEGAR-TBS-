"""Repository port contract for Invoices AR/AP, Payment Approvals & Payment Evidence."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Protocol
from uuid import UUID

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
)


class FinanceRepositoryPort(Protocol):
    """Storage abstraction enforcing AR/AP separation, idempotency, & auditability."""

    async def list_invoices(
        self,
        *,
        invoice_type: InvoiceType | None,
        status_filter: InvoiceStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[InvoiceEntity], int]: ...

    async def get_invoice_by_id(self, invoice_id: UUID) -> InvoiceEntity | None: ...

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
    ) -> InvoiceEntity: ...

    async def verify_invoice(
        self,
        *,
        invoice_id: UUID,
        decision: str,
        reason: str | None,
        actor_id: UUID,
        non_approver_admin: bool,
    ) -> InvoiceEntity: ...

    async def issue_invoice(
        self,
        *,
        invoice_id: UUID,
        actor_id: UUID,
    ) -> InvoiceEntity: ...

    async def approve_payment(
        self,
        *,
        invoice_id: UUID,
        decision: PaymentApprovalDecision,
        reason: str,
        actor_id: UUID,
        non_approver_admin: bool,
        idempotency_record_id: UUID,
    ) -> PaymentApprovalEntity: ...

    async def get_approval_by_id(self, approval_id: UUID) -> PaymentApprovalEntity | None: ...

    async def list_payments(
        self,
        *,
        allowed_farmer_ids: set[UUID] | None,
        allowed_cooperative_ids: set[UUID] | None,
        payment_direction: PaymentDirection | None,
        status_filter: PaymentRecordStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[PaymentRecordEntity], int]: ...

    async def get_payment_by_id(self, payment_id: UUID) -> PaymentRecordEntity | None: ...

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
    ) -> PaymentRecordEntity: ...

    async def verify_payment_record(
        self,
        *,
        payment_id: UUID,
        decision: PaymentRecordStatus,
        reason: str | None,
        actor_id: UUID,
        non_approver_admin: bool,
    ) -> PaymentRecordEntity: ...
