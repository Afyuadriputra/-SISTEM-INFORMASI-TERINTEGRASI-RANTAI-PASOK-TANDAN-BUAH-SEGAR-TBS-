"""B7 file_assets, mill_weighing_tickets, mill_grading_items, and B3 document FKs."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_b7_mill_weighing_files"
down_revision: str | None = "0007_b6_logistics_edo"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "file_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("storage_provider", sa.String(length=30), nullable=False),
        sa.Column("storage_key", sa.String(length=255), nullable=False),
        sa.Column("original_filename", sa.String(length=150), nullable=False),
        sa.Column("mime_type", sa.String(length=80), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=False),
        sa.Column("classification", sa.String(length=40), nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "mime_type IN ('application/pdf', 'image/jpeg', 'image/png')",
            name="ck_file_assets_file_asset_mime_valid",
        ),
        sa.CheckConstraint(
            "size_bytes >= 1 AND size_bytes <= 10485760",
            name="ck_file_assets_file_asset_size_range",
        ),
        sa.CheckConstraint(
            "classification IN "
            "('PRICE_EVIDENCE', 'MILL_TICKET_PROOF', 'DISPUTE_EVIDENCE', 'PAYMENT_PROOF')",
            name="ck_file_assets_file_asset_classification_valid",
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by"], ["user_accounts.id"], name="fk_file_assets_uploaded_by"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_file_assets"),
        sa.UniqueConstraint("storage_key", name="uq_file_assets_storage_key"),
    )
    op.create_index(
        "ix_file_assets_uploaded_by", "file_assets", ["uploaded_by", "created_at"], unique=False
    )

    op.create_foreign_key(
        "fk_mill_price_quotes_source_document_id",
        "mill_price_quotes",
        "file_assets",
        ["source_document_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_disbun_reference_prices_source_document_id",
        "disbun_reference_prices",
        "file_assets",
        ["source_document_id"],
        ["id"],
    )

    op.create_table(
        "mill_weighing_tickets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mill_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ticket_number", sa.String(length=60), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("previous_ticket_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("gross_weight_kg", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("tare_weight_kg", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("net_weight_kg", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("weighed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("proof_file_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("correction_reason", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "revision_number >= 1", name="ck_mill_weighing_tickets_mill_ticket_revision_positive"
        ),
        sa.CheckConstraint(
            "gross_weight_kg > 0", name="ck_mill_weighing_tickets_mill_ticket_gross_positive"
        ),
        sa.CheckConstraint(
            "tare_weight_kg >= 0",
            name="ck_mill_weighing_tickets_mill_ticket_tare_non_negative",
        ),
        sa.CheckConstraint(
            "tare_weight_kg <= gross_weight_kg",
            name="ck_mill_weighing_tickets_mill_ticket_tare_lte_gross",
        ),
        sa.CheckConstraint(
            "net_weight_kg = gross_weight_kg - tare_weight_kg",
            name="ck_mill_weighing_tickets_mill_ticket_net_equals_gross_minus_tare",
        ),
        sa.CheckConstraint(
            "status IN ('DRAFT', 'SUBMITTED', 'VERIFIED')",
            name="ck_mill_weighing_tickets_mill_ticket_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["user_accounts.id"], name="fk_mill_weighing_tickets_created_by"
        ),
        sa.ForeignKeyConstraint(
            ["delivery_order_id"],
            ["delivery_orders.id"],
            name="fk_mill_weighing_tickets_delivery_order_id",
        ),
        sa.ForeignKeyConstraint(["mill_id"], ["mills.id"], name="fk_mill_weighing_tickets_mill_id"),
        sa.ForeignKeyConstraint(
            ["previous_ticket_id"],
            ["mill_weighing_tickets.id"],
            name="fk_mill_weighing_tickets_previous_ticket_id",
        ),
        sa.ForeignKeyConstraint(
            ["proof_file_id"], ["file_assets.id"], name="fk_mill_weighing_tickets_proof_file_id"
        ),
        sa.ForeignKeyConstraint(
            ["verified_by"], ["user_accounts.id"], name="fk_mill_weighing_tickets_verified_by"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_mill_weighing_tickets"),
        sa.UniqueConstraint(
            "delivery_order_id", "revision_number", name="uq_mill_tickets_do_revision"
        ),
    )
    op.create_index(
        "ix_mill_tickets_mill_status",
        "mill_weighing_tickets",
        ["mill_id", "status"],
        unique=False,
    )
    op.create_index(
        "ux_current_mill_ticket_per_do",
        "mill_weighing_tickets",
        ["delivery_order_id"],
        unique=True,
        postgresql_where=sa.text("is_current IS TRUE"),
    )
    op.create_index(
        "uq_mill_tickets_mill_number_current",
        "mill_weighing_tickets",
        ["mill_id", "ticket_number"],
        unique=True,
        postgresql_where=sa.text("is_current IS TRUE"),
    )

    op.create_table(
        "mill_grading_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mill_ticket_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("grading_category", sa.String(length=120), nullable=False),
        sa.Column("deduction_type", sa.String(length=25), nullable=False),
        sa.Column("deduction_value", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("calculation_basis", sa.String(length=60), nullable=False),
        sa.Column("is_simulation", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "deduction_type IN ('WEIGHT_PERCENT', 'WEIGHT_KG', 'VALUE_AMOUNT')",
            name="ck_mill_grading_items_mill_grading_deduction_type_valid",
        ),
        sa.CheckConstraint(
            "deduction_value >= 0",
            name="ck_mill_grading_items_mill_grading_deduction_value_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["mill_ticket_id"],
            ["mill_weighing_tickets.id"],
            name="fk_mill_grading_items_mill_ticket_id",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_mill_grading_items"),
    )


def downgrade() -> None:
    op.drop_table("mill_grading_items")
    op.drop_index("uq_mill_tickets_mill_number_current", table_name="mill_weighing_tickets")
    op.drop_index("ux_current_mill_ticket_per_do", table_name="mill_weighing_tickets")
    op.drop_index("ix_mill_tickets_mill_status", table_name="mill_weighing_tickets")
    op.drop_table("mill_weighing_tickets")
    op.drop_constraint(
        "fk_disbun_reference_prices_source_document_id",
        "disbun_reference_prices",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_mill_price_quotes_source_document_id",
        "mill_price_quotes",
        type_="foreignkey",
    )
    op.drop_index("ix_file_assets_uploaded_by", table_name="file_assets")
    op.drop_table("file_assets")
