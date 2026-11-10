"""B8 reconciliation_cases, dispute_reviews, and farmer_settlement_allocations."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009_b8_reconciliation"
down_revision: str | None = "0008_b7_mill_weighing_files"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reconciliation_cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mill_ticket_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("origin_weight_kg", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("mill_weight_kg", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("difference_weight_kg", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("difference_percent", sa.Numeric(precision=9, scale=4), nullable=False),
        sa.Column("tolerance_percent", sa.Numeric(precision=9, scale=4), nullable=False),
        sa.Column("rule_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tolerance_policy_classification", sa.String(length=25), nullable=False),
        sa.Column("is_negative_difference", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=25), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("agreed_settlement_weight_kg", sa.Numeric(precision=14, scale=3), nullable=True),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "revision_number >= 1", name="ck_reconciliation_cases_rec_revision_positive"
        ),
        sa.CheckConstraint(
            "origin_weight_kg >= 0", name="ck_reconciliation_cases_rec_origin_non_negative"
        ),
        sa.CheckConstraint(
            "mill_weight_kg >= 0", name="ck_reconciliation_cases_rec_mill_non_negative"
        ),
        sa.CheckConstraint(
            "tolerance_policy_classification IN "
            "('CONFIRMED', 'SIMULATION_ONLY', 'PENDING_SOP', 'FUTURE')",
            name="ck_reconciliation_cases_rec_policy_class_valid",
        ),
        sa.CheckConstraint(
            "status IN ('WAITING_TICKET', 'READY', 'MATCHED', 'DISPUTE_HOLD', "
            "'UNDER_REVIEW', 'RESOLVED', 'CANCELLED')",
            name="ck_reconciliation_cases_rec_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["user_accounts.id"], name="fk_reconciliation_cases_created_by"
        ),
        sa.ForeignKeyConstraint(
            ["delivery_order_id"],
            ["delivery_orders.id"],
            name="fk_reconciliation_cases_delivery_order_id",
        ),
        sa.ForeignKeyConstraint(
            ["mill_ticket_id"],
            ["mill_weighing_tickets.id"],
            name="fk_reconciliation_cases_mill_ticket_id",
        ),
        sa.ForeignKeyConstraint(
            ["rule_version_id"],
            ["system_rule_versions.id"],
            name="fk_reconciliation_cases_rule_version_id",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_reconciliation_cases"),
        sa.UniqueConstraint(
            "delivery_order_id", "revision_number", name="uq_reconciliation_do_revision"
        ),
    )
    op.create_index(
        "ix_reconciliation_cases_status", "reconciliation_cases", ["status"], unique=False
    )
    op.create_index(
        "ux_current_reconciliation_per_do",
        "reconciliation_cases",
        ["delivery_order_id"],
        unique=True,
        postgresql_where=sa.text("is_current IS TRUE"),
    )

    op.create_table(
        "dispute_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reconciliation_case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("previous_status", sa.String(length=25), nullable=False),
        sa.Column("decision", sa.String(length=40), nullable=False),
        sa.Column(
            "proposed_settlement_weight_kg", sa.Numeric(precision=14, scale=3), nullable=True
        ),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("evidence_file_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "decision IN ('KEEP_ORIGIN_WEIGHT', 'ACCEPT_MILL_WEIGHT', "
            "'AGREED_SETTLEMENT_WEIGHT', 'REQUIRE_TICKET_REVISION', "
            "'HOLD_FOR_AUDIT', 'CANCEL_CASE')",
            name="ck_dispute_reviews_dispute_decision_valid",
        ),
        sa.ForeignKeyConstraint(
            ["approved_by"], ["user_accounts.id"], name="fk_dispute_reviews_approved_by"
        ),
        sa.ForeignKeyConstraint(
            ["evidence_file_id"], ["file_assets.id"], name="fk_dispute_reviews_evidence_file_id"
        ),
        sa.ForeignKeyConstraint(
            ["reconciliation_case_id"],
            ["reconciliation_cases.id"],
            name="fk_dispute_reviews_reconciliation_case_id",
        ),
        sa.ForeignKeyConstraint(
            ["reviewer_id"], ["user_accounts.id"], name="fk_dispute_reviews_reviewer_id"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_dispute_reviews"),
    )
    op.create_index(
        "ix_dispute_reviews_case",
        "dispute_reviews",
        ["reconciliation_case_id", "reviewed_at"],
        unique=False,
    )

    op.create_table(
        "farmer_settlement_allocations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reconciliation_case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("receipt_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("allocation_basis_weight_kg", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("agreed_weight_kg", sa.Numeric(precision=14, scale=3), nullable=True),
        sa.Column("allocation_policy_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("gross_amount", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column("deduction_amount", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column("net_amount", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column("status", sa.String(length=25), nullable=False),
        sa.Column("policy_classification", sa.String(length=25), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "allocation_basis_weight_kg >= 0",
            name="ck_farmer_settlement_allocations_alloc_basis_non_negative",
        ),
        sa.CheckConstraint(
            "agreed_weight_kg IS NULL OR agreed_weight_kg >= 0",
            name="ck_farmer_settlement_allocations_alloc_agreed_non_negative",
        ),
        sa.CheckConstraint(
            "gross_amount >= 0",
            name="ck_farmer_settlement_allocations_alloc_gross_non_negative",
        ),
        sa.CheckConstraint(
            "deduction_amount >= 0",
            name="ck_farmer_settlement_allocations_alloc_deduction_non_negative",
        ),
        sa.CheckConstraint(
            "net_amount >= 0",
            name="ck_farmer_settlement_allocations_alloc_net_non_negative",
        ),
        sa.CheckConstraint(
            "status IN ('SIMULATED', 'PENDING_SOP_LOCKED', 'APPROVED', 'SETTLED')",
            name="ck_farmer_settlement_allocations_alloc_status_valid",
        ),
        sa.CheckConstraint(
            "policy_classification IN ('CONFIRMED', 'SIMULATION_ONLY', 'PENDING_SOP', 'FUTURE')",
            name="ck_farmer_settlement_allocations_alloc_policy_class_valid",
        ),
        sa.ForeignKeyConstraint(
            ["allocation_policy_version_id"],
            ["system_rule_versions.id"],
            name="fk_farmer_settlement_allocations_allocation_policy_version_id",
        ),
        sa.ForeignKeyConstraint(
            ["farmer_id"], ["farmers.id"], name="fk_farmer_settlement_allocations_farmer_id"
        ),
        sa.ForeignKeyConstraint(
            ["receipt_id"], ["tbs_receipts.id"], name="fk_farmer_settlement_allocations_receipt_id"
        ),
        sa.ForeignKeyConstraint(
            ["reconciliation_case_id"],
            ["reconciliation_cases.id"],
            name="fk_farmer_settlement_allocations_reconciliation_case_id",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_farmer_settlement_allocations"),
    )
    op.create_index(
        "ix_farmer_allocations_case_farmer",
        "farmer_settlement_allocations",
        ["reconciliation_case_id", "farmer_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_farmer_allocations_case_farmer", table_name="farmer_settlement_allocations")
    op.drop_table("farmer_settlement_allocations")
    op.drop_index("ix_dispute_reviews_case", table_name="dispute_reviews")
    op.drop_table("dispute_reviews")
    op.drop_index("ux_current_reconciliation_per_do", table_name="reconciliation_cases")
    op.drop_index("ix_reconciliation_cases_status", table_name="reconciliation_cases")
    op.drop_table("reconciliation_cases")
