"""Pure unit tests for Finance Domain rules (SM-09, SM-10, SM-11, SOD-04..06, BR-PAY-010)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from app.core.exceptions import AppError, ErrorCode
from app.modules.contracts.domain.entities import BusinessModelCode
from app.modules.finance.domain.entities import (
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
from app.modules.finance.domain.rules import (
    assert_can_approve_payment,
    assert_can_issue_invoice,
    assert_can_verify_invoice,
    assert_can_verify_payment_record,
    compute_line_amount,
    derive_settlement_status,
    parse_money_amount,
    validate_payment_submission,
)


def test_money_parsing_and_decimal_line_calculation() -> None:
    assert parse_money_amount("28215000.00") == Decimal("28215000.00")
    assert compute_line_amount(quantity_kg=Decimal("9900.000"), unit_price=Decimal("2850.00")) == (
        Decimal("28215000.00")
    )

    with pytest.raises(AppError) as bad_fmt:
        parse_money_amount("28215000")
    assert bad_fmt.value.code == ErrorCode.VAL_INVALID_DECIMAL_PRECISION

    with pytest.raises(AppError) as non_pos:
        parse_money_amount("0.00")
    assert non_pos.value.code == ErrorCode.PAY_AMOUNT_EXCEEDS_INVOICE


def test_derive_settlement_status_enforces_approved_not_equal_paid() -> None:
    uid1, uid2, inv_id, p1, p2 = uuid4(), uuid4(), uuid4(), uuid4(), uuid4()
    now = datetime.now(UTC)

    approved = PaymentApprovalEntity(
        id=uuid4(),
        requested_by=uid1,
        approver_id=uid2,
        decision=PaymentApprovalDecision.APPROVED,
        decision_reason="Disetujui untuk dibayar.",
        requested_at=now,
        decided_at=now,
    )
    assert (
        derive_settlement_status(
            invoice_total=Decimal("1000000.00"),
            approvals=[approved],
            payments=[],
        )
        == SettlementStatus.AWAITING_PAYMENT
    )

    unverified_pay = PaymentRecordEntity(
        id=uuid4(),
        payment_number="PAY-OUT-001",
        invoice_id=inv_id,
        payment_direction=PaymentDirection.OUTBOUND,
        payer_party_id=p1,
        payee_party_id=p2,
        amount=Decimal("1000000.00"),
        payment_date=date(2026, 11, 10),
        payment_method=PaymentMethod.BANK_TRANSFER_MANUAL,
        payment_reference="REF-001",
        proof_file_id=uuid4(),
        status=PaymentRecordStatus.PENDING_VERIFICATION,
        recorded_by=uid1,
        verified_by=None,
        verified_at=None,
        created_at=now,
    )
    assert (
        derive_settlement_status(
            invoice_total=Decimal("1000000.00"),
            approvals=[approved],
            payments=[unverified_pay],
        )
        == SettlementStatus.PENDING_VERIFICATION
    )

    reversed_pay = PaymentRecordEntity(
        id=unverified_pay.id,
        payment_number=unverified_pay.payment_number,
        invoice_id=inv_id,
        payment_direction=PaymentDirection.OUTBOUND,
        payer_party_id=p1,
        payee_party_id=p2,
        amount=Decimal("1000000.00"),
        payment_date=date(2026, 11, 10),
        payment_method=PaymentMethod.BANK_TRANSFER_MANUAL,
        payment_reference="REF-001",
        proof_file_id=uuid4(),
        status=PaymentRecordStatus.REVERSED,
        recorded_by=uid1,
        verified_by=uid2,
        verified_at=now,
        created_at=now,
    )
    assert (
        derive_settlement_status(
            invoice_total=Decimal("1000000.00"),
            approvals=[approved],
            payments=[reversed_pay],
        )
        == SettlementStatus.AWAITING_PAYMENT
    )


def test_invoice_verify_issue_and_sod_guards() -> None:
    maker, checker = uuid4(), uuid4()

    with pytest.raises(AppError) as sod_err:
        assert_can_verify_invoice(
            current_status=InvoiceStatus.PENDING_VERIFICATION,
            created_by=maker,
            actor_id=maker,
            non_approver_admin=False,
            decision="APPROVE",
            reason=None,
        )
    assert sod_err.value.code == ErrorCode.AUTH_CONFLICT_OF_DUTIES

    with pytest.raises(AppError) as sys_err:
        assert_can_verify_invoice(
            current_status=InvoiceStatus.PENDING_VERIFICATION,
            created_by=maker,
            actor_id=checker,
            non_approver_admin=True,
            decision="APPROVE",
            reason=None,
        )
    assert sys_err.value.code == ErrorCode.AUTH_OPERATION_FORBIDDEN

    with pytest.raises(AppError) as dispute_err:
        assert_can_issue_invoice(
            current_status=InvoiceStatus.VERIFIED,
            business_model_code=BusinessModelCode.PRINCIPAL,
            reconciliation_status="DISPUTE_HOLD",
        )
    assert dispute_err.value.code == ErrorCode.FIN_DISPUTE_HOLD_BLOCKED

    with pytest.raises(AppError) as unconfirmed_err:
        assert_can_issue_invoice(
            current_status=InvoiceStatus.VERIFIED,
            business_model_code=BusinessModelCode.UNCONFIRMED,
            reconciliation_status="MATCHED",
        )
    assert unconfirmed_err.value.code == ErrorCode.FIN_POLICY_UNCONFIRMED


def test_payment_approval_submission_and_verify_guards() -> None:
    maker, approver, verifier = uuid4(), uuid4(), uuid4()
    perumda_party, mill_party, coop_party = uuid4(), uuid4(), uuid4()

    with pytest.raises(AppError) as sod5:
        assert_can_approve_payment(
            invoice_status=InvoiceStatus.ISSUED,
            business_model_code=BusinessModelCode.PRINCIPAL,
            reconciliation_status="MATCHED",
            existing_approvals=[],
            requested_by=maker,
            actor_id=maker,
            non_approver_admin=False,
        )
    assert sod5.value.code == ErrorCode.AUTH_CONFLICT_OF_DUTIES

    with pytest.raises(AppError) as need_approval:
        validate_payment_submission(
            invoice_type=InvoiceType.ACCOUNTS_PAYABLE,
            invoice_status=InvoiceStatus.ISSUED,
            business_model_code=BusinessModelCode.PRINCIPAL,
            creditor_party_id=coop_party,
            debtor_party_id=perumda_party,
            invoice_total=Decimal("20000000.00"),
            settlement_status=SettlementStatus.UNPAID,
            has_approved_obligation=False,
            payment_direction=PaymentDirection.OUTBOUND,
            payer_party_id=perumda_party,
            payee_party_id=coop_party,
            submitted_amount=Decimal("20000000.00"),
        )
    assert need_approval.value.code == ErrorCode.PAY_APPROVAL_REQUIRED

    with pytest.raises(AppError) as partial_err:
        validate_payment_submission(
            invoice_type=InvoiceType.ACCOUNTS_RECEIVABLE,
            invoice_status=InvoiceStatus.ISSUED,
            business_model_code=BusinessModelCode.PRINCIPAL,
            creditor_party_id=perumda_party,
            debtor_party_id=mill_party,
            invoice_total=Decimal("20000000.00"),
            settlement_status=SettlementStatus.UNPAID,
            has_approved_obligation=False,
            payment_direction=PaymentDirection.INBOUND,
            payer_party_id=mill_party,
            payee_party_id=perumda_party,
            submitted_amount=Decimal("10000000.00"),
        )
    assert partial_err.value.code == ErrorCode.PAY_PARTIAL_NOT_SUPPORTED

    with pytest.raises(AppError) as overpay_err:
        validate_payment_submission(
            invoice_type=InvoiceType.ACCOUNTS_RECEIVABLE,
            invoice_status=InvoiceStatus.ISSUED,
            business_model_code=BusinessModelCode.PRINCIPAL,
            creditor_party_id=perumda_party,
            debtor_party_id=mill_party,
            invoice_total=Decimal("20000000.00"),
            settlement_status=SettlementStatus.UNPAID,
            has_approved_obligation=False,
            payment_direction=PaymentDirection.INBOUND,
            payer_party_id=mill_party,
            payee_party_id=perumda_party,
            submitted_amount=Decimal("25000000.00"),
        )
    assert overpay_err.value.code == ErrorCode.PAY_AMOUNT_EXCEEDS_INVOICE

    with pytest.raises(AppError) as bad_pairing:
        validate_payment_submission(
            invoice_type=InvoiceType.ACCOUNTS_RECEIVABLE,
            invoice_status=InvoiceStatus.ISSUED,
            business_model_code=BusinessModelCode.PRINCIPAL,
            creditor_party_id=perumda_party,
            debtor_party_id=mill_party,
            invoice_total=Decimal("20000000.00"),
            settlement_status=SettlementStatus.UNPAID,
            has_approved_obligation=False,
            payment_direction=PaymentDirection.OUTBOUND,
            payer_party_id=mill_party,
            payee_party_id=perumda_party,
            submitted_amount=Decimal("20000000.00"),
        )
    assert bad_pairing.value.code == ErrorCode.PAY_INVALID_PARTY_PAIRING

    with pytest.raises(AppError) as sod6:
        assert_can_verify_payment_record(
            current_status=PaymentRecordStatus.PENDING_VERIFICATION,
            decision=PaymentRecordStatus.VERIFIED,
            recorded_by=approver,
            actor_id=approver,
            non_approver_admin=False,
            has_proof_file=True,
            reason=None,
        )
    assert sod6.value.code == ErrorCode.AUTH_CONFLICT_OF_DUTIES

    with pytest.raises(AppError) as proof_err:
        assert_can_verify_payment_record(
            current_status=PaymentRecordStatus.PENDING_VERIFICATION,
            decision=PaymentRecordStatus.VERIFIED,
            recorded_by=approver,
            actor_id=verifier,
            non_approver_admin=False,
            has_proof_file=False,
            reason=None,
        )
    assert proof_err.value.code == ErrorCode.PAY_PROOF_REQUIRED
