"""B9 invoices, invoice_lines, payment_approvals, and payment_records."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0010_b9_finance"
down_revision: str | None = "0009_b8_reconciliation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(sa.text("CREATE SEQUENCE invoice_seq START WITH 1 INCREMENT BY 1"))
    op.execute(sa.text("CREATE SEQUENCE payment_seq START WITH 1 INCREMENT BY 1"))

    op.create_table(
        "invoices",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invoice_number", sa.String(length=60), nullable=False),
        sa.Column("invoice_type", sa.String(length=30), nullable=False),
        sa.Column("creditor_party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("debtor_party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_model_code", sa.String(length=20), nullable=False),
        sa.Column("business_model_rule_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reconciliation_case_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("invoice_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("gross_amount", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column("deduction_amount", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column("status", sa.String(length=25), nullable=False),
        sa.Column("policy_classification", sa.String(length=25), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("verified_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verification_reason", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "invoice_type IN ('ACCOUNTS_RECEIVABLE', 'ACCOUNTS_PAYABLE')",
            name="ck_invoices_invoice_type_valid",
        ),
        sa.CheckConstraint(
            "creditor_party_id <> debtor_party_id",
            name="ck_invoices_invoice_parties_distinct",
        ),
        sa.CheckConstraint(
            "business_model_code IN ('PRINCIPAL', 'AGENT', 'UNCONFIRMED')",
            name="ck_invoices_invoice_business_model_valid",
        ),
        sa.CheckConstraint(
            "status IN ('DRAFT', 'PENDING_VERIFICATION', 'VERIFIED', 'ISSUED', 'REJECTED', 'VOID')",
            name="ck_invoices_invoice_status_valid",
        ),
        sa.CheckConstraint(
            "policy_classification IN ('CONFIRMED', 'SIMULATION_ONLY', 'PENDING_SOP', 'FUTURE')",
            name="ck_invoices_invoice_policy_class_valid",
        ),
        sa.CheckConstraint("gross_amount >= 0", name="ck_invoices_invoice_gross_non_negative"),
        sa.CheckConstraint(
            "deduction_amount >= 0", name="ck_invoices_invoice_deduction_non_negative"
        ),
        sa.CheckConstraint("total_amount >= 0", name="ck_invoices_invoice_total_non_negative"),
        sa.CheckConstraint("version >= 1", name="ck_invoices_invoice_version_positive"),
        sa.ForeignKeyConstraint(["business_model_rule_version_id"], ["system_rule_versions.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["user_accounts.id"]),
        sa.ForeignKeyConstraint(["creditor_party_id"], ["parties.id"]),
        sa.ForeignKeyConstraint(["debtor_party_id"], ["parties.id"]),
        sa.ForeignKeyConstraint(["reconciliation_case_id"], ["reconciliation_cases.id"]),
        sa.ForeignKeyConstraint(["verified_by"], ["user_accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_number", name="uq_invoices_invoice_number"),
    )
    op.create_index("ix_invoices_status_due_date", "invoices", ["status", "due_date"])
    op.create_index("ix_invoices_type_status", "invoices", ["invoice_type", "status"])
    op.create_index(
        "ux_invoices_active_case_type",
        "invoices",
        ["reconciliation_case_id", "invoice_type"],
        unique=True,
        postgresql_where=sa.text(
            "reconciliation_case_id IS NOT NULL AND status NOT IN ('REJECTED', 'VOID')"
        ),
    )

    op.create_table(
        "invoice_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reference_type", sa.String(length=30), nullable=False),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reconciliation_case_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("unit", sa.String(length=20), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("line_amount", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "reference_type IN ('RECONCILIATION_CASE', 'DELIVERY_ORDER_LINE', 'FEE_ADJUSTMENT')",
            name="ck_invoice_lines_invoice_line_ref_type_valid",
        ),
        sa.CheckConstraint("quantity >= 0", name="ck_invoice_lines_invoice_line_qty_non_negative"),
        sa.CheckConstraint(
            "unit_price >= 0", name="ck_invoice_lines_invoice_line_price_non_negative"
        ),
        sa.CheckConstraint(
            "line_amount >= 0", name="ck_invoice_lines_invoice_line_amount_non_negative"
        ),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"]),
        sa.ForeignKeyConstraint(["reconciliation_case_id"], ["reconciliation_cases.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_invoice_lines_invoice_id", "invoice_lines", ["invoice_id"])

    op.create_table(
        "payment_approvals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("approver_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("decision", sa.String(length=25), nullable=False),
        sa.Column("decision_reason", sa.Text(), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("idempotency_record_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint(
            "decision IN ('PENDING_APPROVAL', 'APPROVED', 'REJECTED')",
            name="ck_payment_approvals_payment_approval_decision_valid",
        ),
        sa.CheckConstraint(
            "approver_id IS NULL OR approver_id <> requested_by",
            name="ck_payment_approvals_payment_approval_sod_05",
        ),
        sa.ForeignKeyConstraint(["approver_id"], ["user_accounts.id"]),
        sa.ForeignKeyConstraint(["idempotency_record_id"], ["idempotency_records.id"]),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"]),
        sa.ForeignKeyConstraint(["requested_by"], ["user_accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_payment_approvals_invoice", "payment_approvals", ["invoice_id", "requested_at"]
    )

    op.create_table(
        "payment_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_number", sa.String(length=60), nullable=False),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_direction", sa.String(length=15), nullable=False),
        sa.Column("payer_party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payee_party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("payment_method", sa.String(length=30), nullable=False),
        sa.Column("payment_reference", sa.String(length=100), nullable=False),
        sa.Column("proof_file_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=25), nullable=False),
        sa.Column("recorded_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("verified_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decision_reason", sa.Text(), nullable=True),
        sa.Column("idempotency_record_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "payment_direction IN ('INBOUND', 'OUTBOUND')",
            name="ck_payment_records_payment_direction_valid",
        ),
        sa.CheckConstraint(
            "payer_party_id <> payee_party_id",
            name="ck_payment_records_payment_parties_distinct",
        ),
        sa.CheckConstraint("amount > 0", name="ck_payment_records_payment_amount_positive"),
        sa.CheckConstraint(
            "payment_method IN ('BANK_TRANSFER_MANUAL', 'CASH_RECEIPT', 'OTHER_VERIFIED')",
            name="ck_payment_records_payment_method_valid",
        ),
        sa.CheckConstraint(
            "status IN ('DRAFT', 'PENDING_VERIFICATION', 'VERIFIED', 'REJECTED', 'REVERSED')",
            name="ck_payment_records_payment_status_valid",
        ),
        sa.CheckConstraint(
            "verified_by IS NULL OR verified_by <> recorded_by",
            name="ck_payment_records_payment_record_sod_06",
        ),
        sa.ForeignKeyConstraint(["idempotency_record_id"], ["idempotency_records.id"]),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"]),
        sa.ForeignKeyConstraint(["payee_party_id"], ["parties.id"]),
        sa.ForeignKeyConstraint(["payer_party_id"], ["parties.id"]),
        sa.ForeignKeyConstraint(["proof_file_id"], ["file_assets.id"]),
        sa.ForeignKeyConstraint(["recorded_by"], ["user_accounts.id"]),
        sa.ForeignKeyConstraint(["verified_by"], ["user_accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payment_number", name="uq_payment_records_payment_number"),
    )
    op.create_index(
        "ix_payment_records_invoice_status", "payment_records", ["invoice_id", "status"]
    )
    op.create_index(
        "ux_payment_records_active_ref",
        "payment_records",
        ["payment_reference"],
        unique=True,
        postgresql_where=sa.text("status NOT IN ('REJECTED', 'REVERSED')"),
    )


def downgrade() -> None:
    op.drop_index("ux_payment_records_active_ref", table_name="payment_records")
    op.drop_index("ix_payment_records_invoice_status", table_name="payment_records")
    op.drop_table("payment_records")

    op.drop_index("ix_payment_approvals_invoice", table_name="payment_approvals")
    op.drop_table("payment_approvals")

    op.drop_index("ix_invoice_lines_invoice_id", table_name="invoice_lines")
    op.drop_table("invoice_lines")

    op.drop_index("ux_invoices_active_case_type", table_name="invoices")
    op.drop_index("ix_invoices_type_status", table_name="invoices")
    op.drop_index("ix_invoices_status_due_date", table_name="invoices")
    op.drop_table("invoices")

    op.execute(sa.text("DROP SEQUENCE IF EXISTS payment_seq"))
    op.execute(sa.text("DROP SEQUENCE IF EXISTS invoice_seq"))
