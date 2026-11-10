"""B5 system_rule_versions (seed baseline), trade_contracts, quota periods, and reservations."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.core.system_rules import (
    RULE_BUSINESS_MODEL_POLICY_ID,
    RULE_FARMER_ALLOCATION_POLICY_ID,
    RULE_RECONCILIATION_TOLERANCE_ID,
)

revision: str = "0006_b5_contracts_quota"
down_revision: str | None = "0005_b4_tbs_receiving"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "system_rule_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rule_code", sa.String(length=80), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rule_config", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("approval_status", sa.String(length=30), nullable=False),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "version_number >= 1", name="ck_system_rule_versions_system_rule_version_positive"
        ),
        sa.CheckConstraint(
            "approval_status IN "
            "('DRAFT', 'SIMULATION_ONLY', 'PENDING_SOP', 'APPROVED', 'SUPERSEDED')",
            name="ck_system_rule_versions_system_rule_approval_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["approved_by"], ["user_accounts.id"], name="fk_system_rule_versions_approved_by"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_system_rule_versions"),
        sa.UniqueConstraint(
            "rule_code", "version_number", name="uq_system_rule_versions_code_version"
        ),
    )
    op.create_index(
        "ix_system_rule_versions_code_effective",
        "system_rule_versions",
        ["rule_code", "effective_from"],
        unique=False,
    )

    rules_tbl = sa.table(
        "system_rule_versions",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("rule_code", sa.String(80)),
        sa.column("version_number", sa.Integer()),
        sa.column("effective_from", sa.DateTime(timezone=True)),
        sa.column("effective_until", sa.DateTime(timezone=True)),
        sa.column("rule_config", postgresql.JSONB(astext_type=sa.Text())),
        sa.column("approval_status", sa.String(30)),
        sa.column("approved_by", postgresql.UUID(as_uuid=True)),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    seed_dt = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
    op.bulk_insert(
        rules_tbl,
        [
            {
                "id": RULE_RECONCILIATION_TOLERANCE_ID,
                "rule_code": "RECONCILIATION_TOLERANCE",
                "version_number": 1,
                "effective_from": seed_dt,
                "effective_until": None,
                "rule_config": {
                    "tolerance_percent": "1.5000",
                    "negative_difference_holds": True,
                    "policy_classification": "SIMULATION_ONLY",
                    "sop_ref": "BSD-DEC-007",
                },
                "approval_status": "SIMULATION_ONLY",
                "approved_by": None,
                "created_at": seed_dt,
            },
            {
                "id": RULE_BUSINESS_MODEL_POLICY_ID,
                "rule_code": "BUSINESS_MODEL_POLICY",
                "version_number": 1,
                "effective_from": seed_dt,
                "effective_until": None,
                "rule_config": {
                    "default_business_model_code": "UNCONFIRMED",
                    "default_perumda_role": "UNCONFIRMED",
                    "policy_classification": "PENDING_SOP",
                    "sop_ref": "BSD-DEC-001",
                },
                "approval_status": "PENDING_SOP",
                "approved_by": None,
                "created_at": seed_dt,
            },
            {
                "id": RULE_FARMER_ALLOCATION_POLICY_ID,
                "rule_code": "FARMER_ALLOCATION_POLICY",
                "version_number": 1,
                "effective_from": seed_dt,
                "effective_until": None,
                "rule_config": {
                    "allocation_basis": "UNCONFIRMED",
                    "default_simulation_basis": "PROPORTIONAL_ORIGIN_WEIGHT",
                    "policy_classification": "PENDING_SOP",
                    "sop_ref": "BSD-DEC-013",
                },
                "approval_status": "PENDING_SOP",
                "approved_by": None,
                "created_at": seed_dt,
            },
        ],
    )

    op.create_table(
        "trade_contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_number", sa.String(length=80), nullable=False),
        sa.Column("mill_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("price_rule_type", sa.String(length=30), nullable=False),
        sa.Column("agreed_price_per_kg", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("grading_policy_reference", sa.String(length=120), nullable=False),
        sa.Column("business_model_code", sa.String(length=20), nullable=False),
        sa.Column("perumda_role", sa.String(length=20), nullable=False),
        sa.Column("seller_party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("buyer_party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_party_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("represented_party_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("business_model_rule_version", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_terms", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=25), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "end_date >= start_date", name="ck_trade_contracts_trade_contract_date_range_valid"
        ),
        sa.CheckConstraint(
            "price_rule_type IN ('FIXED', 'REFERENCE_FORMULA', 'PERIOD_SCHEDULE')",
            name="ck_trade_contracts_trade_contract_price_rule_valid",
        ),
        sa.CheckConstraint(
            "agreed_price_per_kg IS NULL OR agreed_price_per_kg > 0",
            name="ck_trade_contracts_trade_contract_agreed_price_positive",
        ),
        sa.CheckConstraint(
            "business_model_code IN ('PRINCIPAL', 'AGENT', 'UNCONFIRMED')",
            name="ck_trade_contracts_trade_contract_business_model_valid",
        ),
        sa.CheckConstraint(
            "perumda_role IN ('BUYER', 'SELLER', 'AGENT', 'UNCONFIRMED')",
            name="ck_trade_contracts_trade_contract_perumda_role_valid",
        ),
        sa.CheckConstraint(
            "(business_model_code != 'AGENT' OR "
            "(agent_party_id IS NOT NULL AND represented_party_id IS NOT NULL "
            "AND perumda_role = 'AGENT'))",
            name="ck_trade_contracts_trade_contract_agent_parties_valid",
        ),
        sa.CheckConstraint(
            "(business_model_code != 'PRINCIPAL' OR "
            "(represented_party_id IS NULL AND perumda_role IN ('BUYER', 'SELLER')))",
            name="ck_trade_contracts_trade_contract_principal_parties_valid",
        ),
        sa.CheckConstraint(
            "seller_party_id <> buyer_party_id",
            name="ck_trade_contracts_trade_contract_distinct_parties",
        ),
        sa.CheckConstraint(
            "status IN "
            "('DRAFT', 'PENDING_APPROVAL', 'ACTIVE', 'SUSPENDED', 'COMPLETED', 'CANCELLED')",
            name="ck_trade_contracts_trade_contract_status_valid",
        ),
        sa.CheckConstraint(
            "version >= 1", name="ck_trade_contracts_trade_contract_version_positive"
        ),
        sa.ForeignKeyConstraint(
            ["agent_party_id"], ["parties.id"], name="fk_trade_contracts_agent_party_id"
        ),
        sa.ForeignKeyConstraint(
            ["approved_by"], ["user_accounts.id"], name="fk_trade_contracts_approved_by"
        ),
        sa.ForeignKeyConstraint(
            ["business_model_rule_version"],
            ["system_rule_versions.id"],
            name="fk_trade_contracts_business_model_rule_version",
        ),
        sa.ForeignKeyConstraint(
            ["buyer_party_id"], ["parties.id"], name="fk_trade_contracts_buyer_party_id"
        ),
        sa.ForeignKeyConstraint(["mill_id"], ["mills.id"], name="fk_trade_contracts_mill_id"),
        sa.ForeignKeyConstraint(
            ["created_by"], ["user_accounts.id"], name="fk_trade_contracts_created_by"
        ),
        sa.ForeignKeyConstraint(
            ["represented_party_id"],
            ["parties.id"],
            name="fk_trade_contracts_represented_party_id",
        ),
        sa.ForeignKeyConstraint(
            ["seller_party_id"], ["parties.id"], name="fk_trade_contracts_seller_party_id"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_trade_contracts"),
        sa.UniqueConstraint("contract_number", name="uq_trade_contracts_contract_number"),
    )
    op.create_index(
        "ix_trade_contracts_mill_status", "trade_contracts", ["mill_id", "status"], unique=False
    )

    op.create_table(
        "contract_quota_periods",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("quota_limit_kg", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "period_end >= period_start", name="ck_contract_quota_periods_quota_period_dates_valid"
        ),
        sa.CheckConstraint(
            "quota_limit_kg > 0", name="ck_contract_quota_periods_quota_period_limit_positive"
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'CLOSED')",
            name="ck_contract_quota_periods_quota_period_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["contract_id"], ["trade_contracts.id"], name="fk_contract_quota_periods_contract_id"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_contract_quota_periods"),
    )
    op.create_index(
        "ix_contract_quota_periods_contract_status",
        "contract_quota_periods",
        ["contract_id", "status"],
        unique=False,
    )

    op.create_table(
        "quota_reservations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quota_period_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reserved_weight_kg", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("consumed_weight_kg", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("reserved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "reserved_weight_kg > 0", name="ck_quota_reservations_quota_res_reserved_positive"
        ),
        sa.CheckConstraint(
            "consumed_weight_kg >= 0", name="ck_quota_reservations_quota_res_consumed_non_negative"
        ),
        sa.CheckConstraint(
            "status IN ('RESERVED', 'CONSUMED', 'RELEASED')",
            name="ck_quota_reservations_quota_res_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["quota_period_id"],
            ["contract_quota_periods.id"],
            name="fk_quota_reservations_quota_period_id",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_quota_reservations"),
    )
    op.create_index(
        "ix_quota_reservations_period_status",
        "quota_reservations",
        ["quota_period_id", "status"],
        unique=False,
    )
    op.create_index(
        "uq_quota_reservations_active_do",
        "quota_reservations",
        ["delivery_order_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('RESERVED', 'CONSUMED')"),
    )

    op.create_table(
        "contract_approval_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("previous_status", sa.String(length=25), nullable=False),
        sa.Column("new_status", sa.String(length=25), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["actor_id"], ["user_accounts.id"], name="fk_contract_approval_events_actor_id"
        ),
        sa.ForeignKeyConstraint(
            ["contract_id"], ["trade_contracts.id"], name="fk_contract_approval_events_contract_id"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_contract_approval_events"),
    )
    op.create_index(
        "ix_contract_approval_events_contract_id",
        "contract_approval_events",
        ["contract_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_contract_approval_events_contract_id", table_name="contract_approval_events")
    op.drop_table("contract_approval_events")
    op.drop_index("uq_quota_reservations_active_do", table_name="quota_reservations")
    op.drop_index("ix_quota_reservations_period_status", table_name="quota_reservations")
    op.drop_table("quota_reservations")
    op.drop_index("ix_contract_quota_periods_contract_status", table_name="contract_quota_periods")
    op.drop_table("contract_quota_periods")
    op.drop_index("ix_trade_contracts_mill_status", table_name="trade_contracts")
    op.drop_table("trade_contracts")
    op.drop_index("ix_system_rule_versions_code_effective", table_name="system_rule_versions")
    op.drop_table("system_rule_versions")
