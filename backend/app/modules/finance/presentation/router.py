"""FastAPI endpoints for AR/AP Invoices SM-09, Approvals SM-10, & Payments SM-11."""

from __future__ import annotations

from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, status

from app.core.logging import request_id_ctx
from app.core.schemas import SimpleSuccessMeta, build_pagination_meta
from app.modules.finance.application.use_cases import FINANCE_POLICY_NOTICE, FinanceService
from app.modules.finance.domain.entities import (
    InvoiceStatus,
    InvoiceType,
    PaymentDirection,
    PaymentRecordStatus,
)
from app.modules.finance.presentation.schemas import (
    ApprovePaymentRequest,
    CreateInvoiceDraftRequest,
    InvoiceEnvelope,
    InvoiceListEnvelope,
    PaymentApprovalEnvelope,
    PaymentListEnvelope,
    PaymentRecordEnvelope,
    RecordPaymentRequest,
    VerifyInvoiceRequest,
    VerifyPaymentRequest,
    approval_to_dto,
    invoice_to_dto,
    payment_to_dto,
)
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.presentation.dependencies import require_access

invoices_router = APIRouter(prefix="/api/v1/invoices", tags=["Finance & Payments"])
payments_router = APIRouter(prefix="/api/v1/payments", tags=["Finance & Payments"])


def get_finance_service(request: Request) -> FinanceService:
    """Resolve FinanceService wired in composition root."""
    return cast(FinanceService, request.app.state.finance_service)


@invoices_router.get("", response_model=InvoiceListEnvelope)
async def list_invoices(
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("invoices.read",),
            )
        ),
    ],
    service: Annotated[FinanceService, Depends(get_finance_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    invoice_type: Annotated[InvoiceType | None, Query()] = None,
    invoice_status: Annotated[InvoiceStatus | None, Query(alias="status")] = None,
) -> InvoiceListEnvelope:
    rows, total = await service.list_invoices(
        invoice_type=invoice_type,
        status_filter=invoice_status,
        page=page,
        page_size=page_size,
    )
    return InvoiceListEnvelope(
        data=[invoice_to_dto(inv) for inv in rows],
        meta=build_pagination_meta(page, page_size, total, simulation_notice=FINANCE_POLICY_NOTICE),
        request_id=request_id_ctx.get(),
    )


@invoices_router.post(
    "",
    response_model=InvoiceEnvelope,
    status_code=status.HTTP_201_CREATED,
)
async def create_invoice_draft(
    body: CreateInvoiceDraftRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_FINANCE,),
                required_permissions=("invoices.create",),
            )
        ),
    ],
    service: Annotated[FinanceService, Depends(get_finance_service)],
) -> InvoiceEnvelope:
    inv = await service.create_invoice_draft(
        principal=principal,
        invoice_type=body.invoice_type,
        creditor_party_id=body.creditor_party_id,
        debtor_party_id=body.debtor_party_id,
        reconciliation_case_id=body.reconciliation_case_id,
        invoice_date=body.invoice_date,
        due_date=body.due_date,
    )
    return InvoiceEnvelope(
        data=invoice_to_dto(inv),
        meta=SimpleSuccessMeta(simulation_notice=FINANCE_POLICY_NOTICE),
        request_id=request_id_ctx.get(),
    )


@invoices_router.get("/{invoice_id}", response_model=InvoiceEnvelope)
async def get_invoice_detail(
    invoice_id: UUID,
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("invoices.read",),
            )
        ),
    ],
    service: Annotated[FinanceService, Depends(get_finance_service)],
) -> InvoiceEnvelope:
    inv = await service.get_invoice_detail(invoice_id=invoice_id)
    return InvoiceEnvelope(
        data=invoice_to_dto(inv),
        meta=SimpleSuccessMeta(simulation_notice=FINANCE_POLICY_NOTICE),
        request_id=request_id_ctx.get(),
    )


@invoices_router.post("/{invoice_id}/verify", response_model=InvoiceEnvelope)
async def verify_invoice(
    invoice_id: UUID,
    body: VerifyInvoiceRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_FINANCE, RoleCode.DIRECTOR),
                required_permissions=("invoices.verify",),
            )
        ),
    ],
    service: Annotated[FinanceService, Depends(get_finance_service)],
) -> InvoiceEnvelope:
    inv = await service.verify_invoice(
        principal=principal,
        invoice_id=invoice_id,
        decision=body.decision,
        reason=body.reason,
    )
    return InvoiceEnvelope(
        data=invoice_to_dto(inv),
        meta=SimpleSuccessMeta(simulation_notice=FINANCE_POLICY_NOTICE),
        request_id=request_id_ctx.get(),
    )


@invoices_router.post("/{invoice_id}/issue", response_model=InvoiceEnvelope)
async def issue_invoice(
    invoice_id: UUID,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_FINANCE,),
                required_permissions=("invoices.issue",),
            )
        ),
    ],
    service: Annotated[FinanceService, Depends(get_finance_service)],
) -> InvoiceEnvelope:
    inv = await service.issue_invoice(principal=principal, invoice_id=invoice_id)
    return InvoiceEnvelope(
        data=invoice_to_dto(inv),
        meta=SimpleSuccessMeta(simulation_notice=FINANCE_POLICY_NOTICE),
        request_id=request_id_ctx.get(),
    )


@payments_router.get("", response_model=PaymentListEnvelope)
async def list_payments(
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.FARMER,
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("payments.read",),
            )
        ),
    ],
    service: Annotated[FinanceService, Depends(get_finance_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    payment_direction: Annotated[PaymentDirection | None, Query()] = None,
    payment_status: Annotated[PaymentRecordStatus | None, Query(alias="status")] = None,
) -> PaymentListEnvelope:
    rows, total = await service.list_payments(
        principal=principal,
        payment_direction=payment_direction,
        status_filter=payment_status,
        page=page,
        page_size=page_size,
    )
    return PaymentListEnvelope(
        data=[payment_to_dto(p) for p in rows],
        meta=build_pagination_meta(page, page_size, total, simulation_notice=FINANCE_POLICY_NOTICE),
        request_id=request_id_ctx.get(),
    )


@payments_router.post(
    "",
    response_model=PaymentRecordEnvelope,
    status_code=status.HTTP_201_CREATED,
)
async def record_payment_evidence(
    body: RecordPaymentRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_FINANCE,),
                required_permissions=("payments.record",),
            )
        ),
    ],
    service: Annotated[FinanceService, Depends(get_finance_service)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> PaymentRecordEnvelope:
    rec, replayed = await service.record_payment(
        principal=principal,
        raw_idempotency_key=idempotency_key,
        invoice_id=body.invoice_id,
        payment_direction=body.payment_direction,
        payer_party_id=body.payer_party_id,
        payee_party_id=body.payee_party_id,
        amount_raw=body.amount,
        payment_date=body.payment_date,
        payment_method=body.payment_method,
        payment_reference=body.payment_reference,
        proof_file_id=body.proof_file_id,
    )
    return PaymentRecordEnvelope(
        data=payment_to_dto(rec),
        meta=SimpleSuccessMeta(
            idempotency_replayed=True if replayed else False,
            simulation_notice=FINANCE_POLICY_NOTICE,
        ),
        request_id=request_id_ctx.get(),
    )


@payments_router.post("/{id}/approve", response_model=PaymentApprovalEnvelope)
async def approve_or_reject_invoice_payment(
    id: UUID,
    body: ApprovePaymentRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.DIRECTOR,),
                required_permissions=("payments.approve",),
            )
        ),
    ],
    service: Annotated[FinanceService, Depends(get_finance_service)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> PaymentApprovalEnvelope:
    approval, replayed = await service.approve_payment(
        principal=principal,
        raw_idempotency_key=idempotency_key,
        invoice_id=id,
        decision=body.decision,
        reason=body.reason,
    )
    return PaymentApprovalEnvelope(
        data=approval_to_dto(approval),
        meta=SimpleSuccessMeta(
            idempotency_replayed=True if replayed else False,
            simulation_notice=FINANCE_POLICY_NOTICE,
        ),
        request_id=request_id_ctx.get(),
    )


@payments_router.post("/{payment_id}/verify", response_model=PaymentRecordEnvelope)
async def verify_payment_record(
    payment_id: UUID,
    body: VerifyPaymentRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_FINANCE,),
                required_permissions=("payments.verify",),
            )
        ),
    ],
    service: Annotated[FinanceService, Depends(get_finance_service)],
) -> PaymentRecordEnvelope:
    rec = await service.verify_payment_record(
        principal=principal,
        payment_id=payment_id,
        decision=body.decision,
        reason=body.reason,
    )
    return PaymentRecordEnvelope(
        data=payment_to_dto(rec),
        meta=SimpleSuccessMeta(simulation_notice=FINANCE_POLICY_NOTICE),
        request_id=request_id_ctx.get(),
    )
