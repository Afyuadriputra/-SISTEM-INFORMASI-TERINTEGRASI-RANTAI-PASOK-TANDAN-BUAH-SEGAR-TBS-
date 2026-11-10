"""B6 delivery_orders, delivery_order_lines (ux_active_receipt_allocation), status events, FK."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_b6_logistics_edo"
down_revision: str | None = "0006_b5_contracts_quota"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(sa.text("CREATE SEQUENCE delivery_order_seq START WITH 1 INCREMENT BY 1"))

    op.create_table(
        "delivery_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_order_number", sa.String(length=50), nullable=False),
        sa.Column("cooperative_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mill_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("total_origin_weight_kg", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("departed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("arrived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("qr_verification_token", sa.String(length=80), nullable=True),
        sa.Column("qr_reference_hash", sa.String(length=64), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "total_origin_weight_kg > 0", name="ck_delivery_orders_do_total_origin_positive"
        ),
        sa.CheckConstraint(
            "status IN "
            "('DRAFT', 'READY', 'IN_TRANSIT', 'ARRIVED', 'RECEIVED', 'COMPLETED', 'CANCELLED')",
            name="ck_delivery_orders_do_status_valid",
        ),
        sa.CheckConstraint("version >= 1", name="ck_delivery_orders_do_version_positive"),
        sa.ForeignKeyConstraint(
            ["contract_id"], ["trade_contracts.id"], name="fk_delivery_orders_contract_id"
        ),
        sa.ForeignKeyConstraint(
            ["cooperative_id"], ["cooperatives.id"], name="fk_delivery_orders_cooperative_id"
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["user_accounts.id"], name="fk_delivery_orders_created_by"
        ),
        sa.ForeignKeyConstraint(["driver_id"], ["drivers.id"], name="fk_delivery_orders_driver_id"),
        sa.ForeignKeyConstraint(["mill_id"], ["mills.id"], name="fk_delivery_orders_mill_id"),
        sa.ForeignKeyConstraint(
            ["vehicle_id"], ["vehicles.id"], name="fk_delivery_orders_vehicle_id"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_delivery_orders"),
        sa.UniqueConstraint(
            "delivery_order_number", name="uq_delivery_orders_delivery_order_number"
        ),
        sa.UniqueConstraint("qr_reference_hash", name="uq_delivery_orders_qr_reference_hash"),
        sa.UniqueConstraint(
            "qr_verification_token", name="uq_delivery_orders_qr_verification_token"
        ),
    )
    op.create_index(
        "ix_delivery_orders_coop_status",
        "delivery_orders",
        ["cooperative_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_delivery_orders_mill_status", "delivery_orders", ["mill_id", "status"], unique=False
    )

    op.create_table(
        "delivery_order_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("receipt_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("origin_weight_snapshot_kg", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("allocation_status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "origin_weight_snapshot_kg > 0", name="ck_delivery_order_lines_do_line_weight_positive"
        ),
        sa.CheckConstraint(
            "allocation_status IN ('ACTIVE', 'RELEASED')",
            name="ck_delivery_order_lines_do_line_allocation_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["delivery_order_id"],
            ["delivery_orders.id"],
            name="fk_delivery_order_lines_delivery_order_id",
        ),
        sa.ForeignKeyConstraint(
            ["receipt_id"], ["tbs_receipts.id"], name="fk_delivery_order_lines_receipt_id"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_delivery_order_lines"),
    )
    op.create_index(
        "ix_delivery_order_lines_do_id",
        "delivery_order_lines",
        ["delivery_order_id"],
        unique=False,
    )
    op.create_index(
        "ux_active_receipt_allocation",
        "delivery_order_lines",
        ["receipt_id"],
        unique=True,
        postgresql_where=sa.text("allocation_status = 'ACTIVE'"),
    )

    op.create_table(
        "delivery_status_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("previous_status", sa.String(length=20), nullable=True),
        sa.Column("new_status", sa.String(length=20), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(
            ["actor_id"], ["user_accounts.id"], name="fk_delivery_status_events_actor_id"
        ),
        sa.ForeignKeyConstraint(
            ["delivery_order_id"],
            ["delivery_orders.id"],
            name="fk_delivery_status_events_delivery_order_id",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_delivery_status_events"),
    )
    op.create_index(
        "ix_delivery_status_events_do_time",
        "delivery_status_events",
        ["delivery_order_id", "event_time"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_quota_reservations_delivery_order_id",
        "quota_reservations",
        "delivery_orders",
        ["delivery_order_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_quota_reservations_delivery_order_id", "quota_reservations", type_="foreignkey"
    )
    op.drop_index("ix_delivery_status_events_do_time", table_name="delivery_status_events")
    op.drop_table("delivery_status_events")
    op.drop_index("ux_active_receipt_allocation", table_name="delivery_order_lines")
    op.drop_index("ix_delivery_order_lines_do_id", table_name="delivery_order_lines")
    op.drop_table("delivery_order_lines")
    op.drop_index("ix_delivery_orders_mill_status", table_name="delivery_orders")
    op.drop_index("ix_delivery_orders_coop_status", table_name="delivery_orders")
    op.drop_table("delivery_orders")
    op.execute(sa.text("DROP SEQUENCE IF EXISTS delivery_order_seq"))
