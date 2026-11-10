"""SQLAlchemy 2 ORM models for invoices, invoice_lines, payment_approvals, & payment_records."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class InvoiceModel(Base):
    """AR/AP invoice header separating Mill Receivables vs Coop/Farmer Payables (DBD §14.2)."""

    __tablename__ = "invoices"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    invoice_number: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    invoice_type: Mapped[str] = mapped_column(String(30), nullable=False)
    creditor_party_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False
    )
    debtor_party_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False
    )
    business_model_code: Mapped[str] = mapped_column(String(20), nullable=False)
    business_model_rule_version_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("system_rule_versions.id"), nullable=False
    )
    reconciliation_case_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("reconciliation_cases.id"), nullable=True
    )
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    deduction_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(25), nullable=False)
    policy_classification: Mapped[str] = mapped_column(String(25), nullable=False)
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    verified_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    lines: Mapped[list[InvoiceLineModel]] = relationship(
        back_populates="invoice", order_by="InvoiceLineModel.created_at"
    )
    approvals: Mapped[list[PaymentApprovalModel]] = relationship(
        back_populates="invoice", order_by="PaymentApprovalModel.requested_at"
    )
    payments: Mapped[list[PaymentRecordModel]] = relationship(
        back_populates="invoice", order_by="PaymentRecordModel.created_at"
    )

    __table_args__ = (
        CheckConstraint(
            "invoice_type IN ('ACCOUNTS_RECEIVABLE', 'ACCOUNTS_PAYABLE')",
            name="invoice_type_valid",
        ),
        CheckConstraint(
            "creditor_party_id <> debtor_party_id",
            name="invoice_parties_distinct",
        ),
        CheckConstraint(
            "business_model_code IN ('PRINCIPAL', 'AGENT', 'UNCONFIRMED')",
            name="invoice_business_model_valid",
        ),
        CheckConstraint(
            "status IN ('DRAFT', 'PENDING_VERIFICATION', 'VERIFIED', 'ISSUED', 'REJECTED', 'VOID')",
            name="invoice_status_valid",
        ),
        CheckConstraint(
            "policy_classification IN ('CONFIRMED', 'SIMULATION_ONLY', 'PENDING_SOP', 'FUTURE')",
            name="invoice_policy_class_valid",
        ),
        CheckConstraint("gross_amount >= 0", name="invoice_gross_non_negative"),
        CheckConstraint("deduction_amount >= 0", name="invoice_deduction_non_negative"),
        CheckConstraint("total_amount >= 0", name="invoice_total_non_negative"),
        CheckConstraint("version >= 1", name="invoice_version_positive"),
        Index("ix_invoices_status_due_date", "status", "due_date"),
        Index("ix_invoices_type_status", "invoice_type", "status"),
        Index(
            "ux_invoices_active_case_type",
            "reconciliation_case_id",
            "invoice_type",
            unique=True,
            postgresql_where=text(
                "reconciliation_case_id IS NOT NULL AND status NOT IN ('REJECTED', 'VOID')"
            ),
        ),
    )


class InvoiceLineModel(Base):
    """Snapshot valuation lines anchored to reconciliation / delivery evidence (DBD §14.3)."""

    __tablename__ = "invoice_lines"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    invoice_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False
    )
    reference_type: Mapped[str] = mapped_column(String(30), nullable=False)
    reference_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    reconciliation_case_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("reconciliation_cases.id"), nullable=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False, default="kg")
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    line_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    invoice: Mapped[InvoiceModel] = relationship(back_populates="lines")

    __table_args__ = (
        CheckConstraint(
            "reference_type IN ('RECONCILIATION_CASE', 'DELIVERY_ORDER_LINE', 'FEE_ADJUSTMENT')",
            name="invoice_line_ref_type_valid",
        ),
        CheckConstraint("quantity >= 0", name="invoice_line_qty_non_negative"),
        CheckConstraint("unit_price >= 0", name="invoice_line_price_non_negative"),
        CheckConstraint("line_amount >= 0", name="invoice_line_amount_non_negative"),
        Index("ix_invoice_lines_invoice_id", "invoice_id"),
    )


class PaymentApprovalModel(Base):
    """Director authorization event for payable/receivable obligations SM-10 (DBD §14.4)."""

    __tablename__ = "payment_approvals"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    invoice_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False
    )
    requested_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    approver_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=True
    )
    decision: Mapped[str] = mapped_column(String(25), nullable=False)
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    idempotency_record_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("idempotency_records.id"), nullable=True
    )

    invoice: Mapped[InvoiceModel] = relationship(back_populates="approvals")

    __table_args__ = (
        CheckConstraint(
            "decision IN ('PENDING_APPROVAL', 'APPROVED', 'REJECTED')",
            name="payment_approval_decision_valid",
        ),
        CheckConstraint(
            "approver_id IS NULL OR approver_id <> requested_by",
            name="payment_approval_sod_05",
        ),
        Index("ix_payment_approvals_invoice", "invoice_id", "requested_at"),
    )


class PaymentRecordModel(Base):
    """Manual payment proof record SM-11 (never auto-executes bank transfers, DBD §14.5)."""

    __tablename__ = "payment_records"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    payment_number: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    invoice_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False
    )
    payment_direction: Mapped[str] = mapped_column(String(15), nullable=False)
    payer_party_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False
    )
    payee_party_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(30), nullable=False)
    payment_reference: Mapped[str] = mapped_column(String(100), nullable=False)
    proof_file_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("file_assets.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(25), nullable=False)
    recorded_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    verified_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    idempotency_record_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("idempotency_records.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    invoice: Mapped[InvoiceModel] = relationship(back_populates="payments")

    __table_args__ = (
        CheckConstraint(
            "payment_direction IN ('INBOUND', 'OUTBOUND')",
            name="payment_direction_valid",
        ),
        CheckConstraint(
            "payer_party_id <> payee_party_id",
            name="payment_parties_distinct",
        ),
        CheckConstraint("amount > 0", name="payment_amount_positive"),
        CheckConstraint(
            "payment_method IN ('BANK_TRANSFER_MANUAL', 'CASH_RECEIPT', 'OTHER_VERIFIED')",
            name="payment_method_valid",
        ),
        CheckConstraint(
            "status IN ('DRAFT', 'PENDING_VERIFICATION', 'VERIFIED', 'REJECTED', 'REVERSED')",
            name="payment_status_valid",
        ),
        CheckConstraint(
            "verified_by IS NULL OR verified_by <> recorded_by",
            name="payment_record_sod_06",
        ),
        Index("ix_payment_records_invoice_status", "invoice_id", "status"),
        Index(
            "ux_payment_records_active_ref",
            "payment_reference",
            unique=True,
            postgresql_where=text("status NOT IN ('REJECTED', 'REVERSED')"),
        ),
    )
