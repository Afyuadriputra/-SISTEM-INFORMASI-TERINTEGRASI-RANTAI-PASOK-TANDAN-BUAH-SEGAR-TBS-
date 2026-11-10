"""B10 composite indexes optimizing reporting date-window & audit queries (DBD §20.2)."""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0011_b10_reporting_indexes"
down_revision: str | None = "0010_b9_finance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_delivery_orders_status_created", "delivery_orders", ["status", "created_at"]
    )
    op.create_index(
        "ix_reconciliation_cases_status_calculated",
        "reconciliation_cases",
        ["status", "calculated_at"],
    )
    op.create_index("ix_audit_events_occurred_at", "audit_events", ["occurred_at"])
    op.create_index(
        "ix_invoices_date_type_status",
        "invoices",
        ["invoice_date", "invoice_type", "status"],
    )
    op.create_index(
        "ix_payment_records_date_dir_status",
        "payment_records",
        ["payment_date", "payment_direction", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_payment_records_date_dir_status", table_name="payment_records")
    op.drop_index("ix_invoices_date_type_status", table_name="invoices")
    op.drop_index("ix_audit_events_occurred_at", table_name="audit_events")
    op.drop_index("ix_reconciliation_cases_status_calculated", table_name="reconciliation_cases")
    op.drop_index("ix_delivery_orders_status_created", table_name="delivery_orders")
