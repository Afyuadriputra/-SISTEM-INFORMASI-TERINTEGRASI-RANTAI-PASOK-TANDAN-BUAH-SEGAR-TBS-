"""B4 idempotency_records, tbs_receipts, receipt_weighing_revisions, and receipt_grading_items."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_b4_tbs_receiving"
down_revision: str | None = "0004_b3_pricing_public"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "idempotency_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("operation_key", sa.String(length=80), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("processing_status", sa.String(length=20), nullable=False),
        sa.Column("response_reference", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("response_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "processing_status IN ('IN_PROGRESS', 'COMPLETED', 'FAILED')",
            name="ck_idempotency_records_idempotency_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"], ["user_accounts.id"], name="fk_idempotency_records_actor_id"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_idempotency_records"),
    )
    op.create_index(
        "uq_idempotency_records_actor_op_key",
        "idempotency_records",
        ["actor_id", "operation_key", "idempotency_key"],
        unique=True,
    )
    op.create_index(
        "ix_idempotency_records_expires_at", "idempotency_records", ["expires_at"], unique=False
    )

    op.execute(sa.text("CREATE SEQUENCE tbs_receipt_seq START WITH 1 INCREMENT BY 1"))

    op.create_table(
        "tbs_receipts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("receipt_number", sa.String(length=50), nullable=False),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farm_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cooperative_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("harvest_date", sa.Date(), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "status IN ('DRAFT', 'VALIDATED', 'ALLOCATED', 'SHIPPED', 'CLOSED', 'CANCELLED')",
            name="ck_tbs_receipts_tbs_receipt_status_valid",
        ),
        sa.CheckConstraint("version >= 1", name="ck_tbs_receipts_tbs_receipt_version_positive"),
        sa.ForeignKeyConstraint(
            ["cooperative_id"], ["cooperatives.id"], name="fk_tbs_receipts_cooperative_id"
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["user_accounts.id"], name="fk_tbs_receipts_created_by"
        ),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], name="fk_tbs_receipts_farm_id"),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"], name="fk_tbs_receipts_farmer_id"),
        sa.PrimaryKeyConstraint("id", name="pk_tbs_receipts"),
        sa.UniqueConstraint("receipt_number", name="uq_tbs_receipts_receipt_number"),
    )
    op.create_index(
        "ix_tbs_receipts_coop_received",
        "tbs_receipts",
        ["cooperative_id", "received_at"],
        unique=False,
    )
    op.create_index(
        "ix_tbs_receipts_farmer_received",
        "tbs_receipts",
        ["farmer_id", "received_at"],
        unique=False,
    )
    op.create_index(
        "ix_tbs_receipts_status_coop", "tbs_receipts", ["status", "cooperative_id"], unique=False
    )

    op.create_table(
        "receipt_weighing_revisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("receipt_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("gross_weight_kg", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("tare_weight_kg", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("net_weight_kg", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("weighed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("weighed_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("correction_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "revision_number >= 1",
            name="ck_receipt_weighing_revisions_weighing_revision_number_positive",
        ),
        sa.CheckConstraint(
            "gross_weight_kg > 0",
            name="ck_receipt_weighing_revisions_weighing_gross_positive",
        ),
        sa.CheckConstraint(
            "tare_weight_kg >= 0",
            name="ck_receipt_weighing_revisions_weighing_tare_non_negative",
        ),
        sa.CheckConstraint(
            "tare_weight_kg <= gross_weight_kg",
            name="ck_receipt_weighing_revisions_weighing_tare_lte_gross",
        ),
        sa.CheckConstraint(
            "net_weight_kg = gross_weight_kg - tare_weight_kg",
            name="ck_receipt_weighing_revisions_weighing_net_equals_gross_minus_tare",
        ),
        sa.ForeignKeyConstraint(
            ["receipt_id"], ["tbs_receipts.id"], name="fk_receipt_weighing_revisions_receipt_id"
        ),
        sa.ForeignKeyConstraint(
            ["weighed_by"], ["user_accounts.id"], name="fk_receipt_weighing_revisions_weighed_by"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_receipt_weighing_revisions"),
        sa.UniqueConstraint(
            "receipt_id",
            "revision_number",
            name="uq_receipt_weighing_revisions_receipt_rev",
        ),
    )
    op.create_index(
        "uq_receipt_weighing_revisions_current",
        "receipt_weighing_revisions",
        ["receipt_id"],
        unique=True,
        postgresql_where=sa.text("is_current IS TRUE"),
    )

    op.create_table(
        "receipt_grading_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("weighing_revision_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("grading_category", sa.String(length=120), nullable=False),
        sa.Column("measurement_value", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("deduction_type", sa.String(length=25), nullable=False),
        sa.Column("deduction_value", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("deduction_weight_kg", sa.Numeric(precision=14, scale=3), nullable=True),
        sa.Column("deduction_amount", sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column("calculation_basis", sa.String(length=60), nullable=False),
        sa.Column("is_simulation", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "measurement_value >= 0",
            name="ck_receipt_grading_items_grading_measurement_non_negative",
        ),
        sa.CheckConstraint(
            "deduction_type IN ('WEIGHT_PERCENT', 'WEIGHT_KG', 'VALUE_AMOUNT')",
            name="ck_receipt_grading_items_grading_deduction_type_valid",
        ),
        sa.CheckConstraint(
            "deduction_value >= 0",
            name="ck_receipt_grading_items_grading_deduction_value_non_negative",
        ),
        sa.CheckConstraint(
            "deduction_weight_kg IS NULL OR deduction_weight_kg >= 0",
            name="ck_receipt_grading_items_grading_deduction_weight_non_negative",
        ),
        sa.CheckConstraint(
            "deduction_amount IS NULL OR deduction_amount >= 0",
            name="ck_receipt_grading_items_grading_deduction_amount_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["weighing_revision_id"],
            ["receipt_weighing_revisions.id"],
            name="fk_receipt_grading_items_weighing_revision_id",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_receipt_grading_items"),
        sa.UniqueConstraint(
            "weighing_revision_id",
            "grading_category",
            name="uq_receipt_grading_items_revision_category",
        ),
    )


def downgrade() -> None:
    op.drop_table("receipt_grading_items")
    op.drop_index("uq_receipt_weighing_revisions_current", table_name="receipt_weighing_revisions")
    op.drop_table("receipt_weighing_revisions")
    op.drop_index("ix_tbs_receipts_status_coop", table_name="tbs_receipts")
    op.drop_index("ix_tbs_receipts_farmer_received", table_name="tbs_receipts")
    op.drop_index("ix_tbs_receipts_coop_received", table_name="tbs_receipts")
    op.drop_table("tbs_receipts")
    op.execute(sa.text("DROP SEQUENCE IF EXISTS tbs_receipt_seq"))
    op.drop_index("ix_idempotency_records_expires_at", table_name="idempotency_records")
    op.drop_index("uq_idempotency_records_actor_op_key", table_name="idempotency_records")
    op.drop_table("idempotency_records")
