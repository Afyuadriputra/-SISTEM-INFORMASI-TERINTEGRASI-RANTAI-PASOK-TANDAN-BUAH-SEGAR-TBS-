"""Use cases orchestrating Invoices SM-09, Payment Approvals SM-10 & Payments SM-11."""

from __future__ import annotations

from datetime import date
from typing import Literal
from uuid import UUID

from app.core.exceptions import AppError, ErrorCode
from app.core.idempotency_primitives import (
    IdempotencySlotPort,
    compute_request_hash,
    validate_idempotency_key,
)
from app.modules.finance.application.ports import FinanceRepositoryPort
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
from app.modules.finance.domain.rules import parse_money_amount
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.domain.rules import (
    allowed_cooperative_ids,
    allowed_farmer_ids,
    has_global_scope,
    is_non_approver_admin,
)

FINANCE_POLICY_NOTICE = (
    "Status disetujui (APPROVED) != terbayar (PAID). Bukti bayar manual wajib diverifikasi "
    "dan pembagian bertahap ditolak sampai SOP disahkan (BR-PAY-010, BSD-DEC-015..018)."
)


class FinanceService:
    """Manages AR/AP invoices, director payment approvals, & verified payment settlement."""

    def __init__(
        self,
        *,
        repo: FinanceRepositoryPort,
        idempotency: IdempotencySlotPort,
    ) -> None:
        self._repo = repo
        self._idempotency = idempotency

    async def list_invoices(
        self,
        *,
        invoice_type: InvoiceType | None,
        status_filter: InvoiceStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[InvoiceEntity], int]:
        return await self._repo.list_invoices(
            invoice_type=invoice_type,
            status_filter=status_filter,
            page=page,
            page_size=page_size,
        )

    async def get_invoice_detail(self, *, invoice_id: UUID) -> InvoiceEntity:
        inv = await self._repo.get_invoice_by_id(invoice_id)
        if inv is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        return inv

    async def create_invoice_draft(
        self,
        *,
        principal: AuthenticatedPrincipal,
        invoice_type: InvoiceType,
        creditor_party_id: UUID,
        debtor_party_id: UUID,
        reconciliation_case_id: UUID,
        invoice_date: date,
        due_date: date | None,
    ) -> InvoiceEntity:
        if creditor_party_id == debtor_party_id:
            raise AppError(ErrorCode.PAY_INVALID_PARTY_PAIRING)
        if due_date is not None and due_date < invoice_date:
            raise AppError(ErrorCode.VAL_INVALID_DATE_RANGE)
        return await self._repo.create_invoice_draft(
            invoice_type=invoice_type,
            creditor_party_id=creditor_party_id,
            debtor_party_id=debtor_party_id,
            reconciliation_case_id=reconciliation_case_id,
            invoice_date=invoice_date,
            due_date=due_date,
            actor_id=principal.user_id,
        )

    async def verify_invoice(
        self,
        *,
        principal: AuthenticatedPrincipal,
        invoice_id: UUID,
        decision: Literal["APPROVE", "REJECT"],
        reason: str | None,
    ) -> InvoiceEntity:
        return await self._repo.verify_invoice(
            invoice_id=invoice_id,
            decision=decision,
            reason=reason.strip() if reason else None,
            actor_id=principal.user_id,
            non_approver_admin=is_non_approver_admin(principal.roles),
        )

    async def issue_invoice(
        self,
        *,
        principal: AuthenticatedPrincipal,
        invoice_id: UUID,
    ) -> InvoiceEntity:
        return await self._repo.issue_invoice(
            invoice_id=invoice_id,
            actor_id=principal.user_id,
        )

    async def approve_payment(
        self,
        *,
        principal: AuthenticatedPrincipal,
        raw_idempotency_key: str | None,
        invoice_id: UUID,
        decision: Literal["APPROVED", "REJECTED"],
        reason: str,
    ) -> tuple[PaymentApprovalEntity, bool]:
        idempotency_key = validate_idempotency_key(raw_idempotency_key)
        reason_clean = reason.strip()
        if len(reason_clean) < 5:
            raise AppError(ErrorCode.VAL_REQUIRED_FIELD)

        req_hash = compute_request_hash(
            {"invoice_id": str(invoice_id), "decision": decision, "reason": reason_clean}
        )
        slot = await self._idempotency.reserve(
            actor_id=principal.user_id,
            operation_key="approveOrRejectInvoicePayment",
            idempotency_key=idempotency_key,
            request_hash=req_hash,
        )
        if slot.is_replay:
            if slot.response_reference is None:
                raise AppError(ErrorCode.SYS_DEPENDENCY_UNAVAILABLE)
            existing = await self._repo.get_approval_by_id(slot.response_reference)
            if existing is None:
                raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
            return existing, True

        try:
            approval = await self._repo.approve_payment(
                invoice_id=invoice_id,
                decision=PaymentApprovalDecision(decision),
                reason=reason_clean,
                actor_id=principal.user_id,
                non_approver_admin=is_non_approver_admin(principal.roles),
                idempotency_record_id=slot.record_id,
            )
        except Exception:
            await self._idempotency.release_on_error(record_id=slot.record_id)
            raise
        return approval, False

    async def list_payments(
        self,
        *,
        principal: AuthenticatedPrincipal,
        payment_direction: PaymentDirection | None,
        status_filter: PaymentRecordStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[PaymentRecordEntity], int]:
        f_ids: set[UUID] | None = None
        c_ids: set[UUID] | None = None
        effective_direction = payment_direction

        if not has_global_scope(principal):
            if RoleCode.FARMER in principal.roles:
                f_ids = allowed_farmer_ids(principal)
                if payment_direction == PaymentDirection.INBOUND:
                    return [], 0
                effective_direction = PaymentDirection.OUTBOUND
            elif RoleCode.COOPERATIVE_OPERATOR in principal.roles:
                c_ids = allowed_cooperative_ids(principal)
                if payment_direction == PaymentDirection.INBOUND:
                    return [], 0
                effective_direction = PaymentDirection.OUTBOUND
            else:
                raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)

        return await self._repo.list_payments(
            allowed_farmer_ids=f_ids,
            allowed_cooperative_ids=c_ids,
            payment_direction=effective_direction,
            status_filter=status_filter,
            page=page,
            page_size=page_size,
        )

    async def record_payment(
        self,
        *,
        principal: AuthenticatedPrincipal,
        raw_idempotency_key: str | None,
        invoice_id: UUID,
        payment_direction: PaymentDirection,
        payer_party_id: UUID,
        payee_party_id: UUID,
        amount_raw: str,
        payment_date: date,
        payment_method: PaymentMethod,
        payment_reference: str,
        proof_file_id: UUID,
    ) -> tuple[PaymentRecordEntity, bool]:
        idempotency_key = validate_idempotency_key(raw_idempotency_key)
        ref_clean = payment_reference.strip()
        if len(ref_clean) < 3:
            raise AppError(ErrorCode.PAY_PROOF_REQUIRED)
        amount = parse_money_amount(amount_raw, field_name="amount")

        req_hash = compute_request_hash(
            {
                "invoice_id": str(invoice_id),
                "payment_direction": payment_direction.value,
                "payer_party_id": str(payer_party_id),
                "payee_party_id": str(payee_party_id),
                "amount": f"{amount:.2f}",
                "payment_date": payment_date.isoformat(),
                "payment_method": payment_method.value,
                "payment_reference": ref_clean,
                "proof_file_id": str(proof_file_id),
            }
        )
        slot = await self._idempotency.reserve(
            actor_id=principal.user_id,
            operation_key="recordPaymentEvidence",
            idempotency_key=idempotency_key,
            request_hash=req_hash,
        )
        if slot.is_replay:
            if slot.response_reference is None:
                raise AppError(ErrorCode.SYS_DEPENDENCY_UNAVAILABLE)
            existing = await self._repo.get_payment_by_id(slot.response_reference)
            if existing is None:
                raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
            return existing, True

        try:
            rec = await self._repo.record_payment(
                invoice_id=invoice_id,
                payment_direction=payment_direction,
                payer_party_id=payer_party_id,
                payee_party_id=payee_party_id,
                amount=amount,
                payment_date=payment_date,
                payment_method=payment_method,
                payment_reference=ref_clean,
                proof_file_id=proof_file_id,
                actor_id=principal.user_id,
                idempotency_record_id=slot.record_id,
            )
        except Exception:
            await self._idempotency.release_on_error(record_id=slot.record_id)
            raise
        return rec, False

    async def verify_payment_record(
        self,
        *,
        principal: AuthenticatedPrincipal,
        payment_id: UUID,
        decision: Literal["VERIFIED", "REJECTED", "REVERSED"],
        reason: str | None,
    ) -> PaymentRecordEntity:
        return await self._repo.verify_payment_record(
            payment_id=payment_id,
            decision=PaymentRecordStatus(decision),
            reason=reason.strip() if reason else None,
            actor_id=principal.user_id,
            non_approver_admin=is_non_approver_admin(principal.roles),
        )
