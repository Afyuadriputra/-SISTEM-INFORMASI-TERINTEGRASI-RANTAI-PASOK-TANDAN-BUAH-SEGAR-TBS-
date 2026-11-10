"""B3 pricing, verification history, Disbun reference, and curated public tables."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.modules.pricing.domain.rules import CANONICAL_PRICE_CATEGORIES, CANONICAL_PRICE_SOURCES
from app.modules.pricing.infrastructure.models import (
    deterministic_category_id,
    deterministic_source_id,
)

revision: str = "0004_b3_pricing_public"
down_revision: str | None = "0003_b2_master_data"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "price_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_code", sa.String(length=50), nullable=False),
        sa.Column("source_name", sa.String(length=150), nullable=False),
        sa.Column("source_type", sa.String(length=30), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.CheckConstraint(
            "source_type IN ('DISBUN', 'MILL_OFFICIAL', 'MILL_DOCUMENT', 'VERIFIED_MANUAL')",
            name="ck_price_sources_price_source_type_valid",
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')", name="ck_price_sources_price_source_status_valid"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_price_sources"),
        sa.UniqueConstraint("source_code", name="uq_price_sources_source_code"),
    )

    op.create_table(
        "price_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("unit", sa.String(length=20), nullable=False),
        sa.Column("quality_basis", sa.Text(), nullable=False),
        sa.Column("age_group", sa.String(length=60), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id", name="pk_price_categories"),
        sa.UniqueConstraint("category_code", name="uq_price_categories_category_code"),
    )

    op.create_table(
        "mill_price_quotes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mill_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("price_category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("price_per_kg", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=25), nullable=False),
        sa.Column("submitted_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("verified_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_simulation", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("price_per_kg > 0", name="ck_mill_price_quotes_quote_price_positive"),
        sa.CheckConstraint(
            "effective_until IS NULL OR effective_until > effective_from",
            name="ck_mill_price_quotes_quote_period_valid",
        ),
        sa.CheckConstraint(
            "status IN ('DRAFT', 'PENDING_VERIFICATION', 'VERIFIED', "
            "'REJECTED', 'PUBLISHED', 'REVOKED')",
            name="ck_mill_price_quotes_quote_status_valid",
        ),
        sa.CheckConstraint("version >= 1", name="ck_mill_price_quotes_quote_version_positive"),
        sa.ForeignKeyConstraint(
            ["mill_id"], ["mills.id"], name="fk_mill_price_quotes_mill_id_mills"
        ),
        sa.ForeignKeyConstraint(
            ["price_category_id"],
            ["price_categories.id"],
            name="fk_mill_price_quotes_price_category_id_price_categories",
        ),
        sa.ForeignKeyConstraint(
            ["source_id"], ["price_sources.id"], name="fk_mill_price_quotes_source_id_price_sources"
        ),
        sa.ForeignKeyConstraint(
            ["submitted_by"],
            ["user_accounts.id"],
            name="fk_mill_price_quotes_submitted_by_user_accounts",
        ),
        sa.ForeignKeyConstraint(
            ["verified_by"],
            ["user_accounts.id"],
            name="fk_mill_price_quotes_verified_by_user_accounts",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_mill_price_quotes"),
    )
    op.create_index(
        "ix_mill_price_quotes_lookup",
        "mill_price_quotes",
        ["mill_id", "price_category_id", "effective_from"],
    )
    op.create_index(
        "ix_mill_price_quotes_status_from", "mill_price_quotes", ["status", "effective_from"]
    )

    op.create_table(
        "price_verification_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("price_quote_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("previous_status", sa.String(length=25), nullable=False),
        sa.Column("new_status", sa.String(length=25), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["user_accounts.id"],
            name="fk_price_verification_events_actor_id_user_accounts",
        ),
        sa.ForeignKeyConstraint(
            ["price_quote_id"],
            ["mill_price_quotes.id"],
            name="fk_price_verification_events_price_quote_id_mill_price_quotes",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_price_verification_events"),
    )
    op.create_index(
        "ix_price_verification_events_quote",
        "price_verification_events",
        ["price_quote_id", "created_at"],
    )

    op.create_table(
        "disbun_reference_prices",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("price_source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("price_category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("price_per_kg", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("verification_status", sa.String(length=25), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "price_per_kg > 0", name="ck_disbun_reference_prices_disbun_price_positive"
        ),
        sa.CheckConstraint(
            "effective_until IS NULL OR effective_until > effective_from",
            name="ck_disbun_reference_prices_disbun_period_valid",
        ),
        sa.CheckConstraint(
            "verification_status IN ('VERIFIED', 'PUBLISHED')",
            name="ck_disbun_reference_prices_disbun_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["price_category_id"],
            ["price_categories.id"],
            name="fk_disbun_reference_prices_price_category_id_price_categories",
        ),
        sa.ForeignKeyConstraint(
            ["price_source_id"],
            ["price_sources.id"],
            name="fk_disbun_reference_prices_price_source_id_price_sources",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_disbun_reference_prices"),
    )
    op.create_index(
        "ix_disbun_reference_prices_from", "disbun_reference_prices", ["effective_from"]
    )

    op.create_table(
        "public_pages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("publication_status", sa.String(length=25), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "publication_status IN ('DRAFT', 'PUBLISHED')",
            name="ck_public_pages_public_page_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"], ["user_accounts.id"], name="fk_public_pages_updated_by_user_accounts"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_public_pages"),
        sa.UniqueConstraint("slug", name="uq_public_pages_slug"),
    )

    op.create_table(
        "public_notices",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=25), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('DRAFT', 'PUBLISHED', 'ARCHIVED')",
            name="ck_public_notices_public_notice_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["user_accounts.id"],
            name="fk_public_notices_created_by_user_accounts",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_public_notices"),
    )
    op.create_index("ix_public_notices_active", "public_notices", ["status", "start_at", "end_at"])

    # Seed canonical sources & categories.
    sources_t = sa.table(
        "price_sources",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("source_code", sa.String),
        sa.column("source_name", sa.String),
        sa.column("source_type", sa.String),
        sa.column("source_url", sa.Text),
        sa.column("description", sa.Text),
        sa.column("status", sa.String),
    )
    cats_t = sa.table(
        "price_categories",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("category_code", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("unit", sa.String),
        sa.column("quality_basis", sa.Text),
        sa.column("age_group", sa.String),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(
        sources_t,
        [
            {
                "id": deterministic_source_id(s.code),
                "source_code": s.code,
                "source_name": s.name,
                "source_type": s.source_type,
                "source_url": None,
                "description": s.description,
                "status": "ACTIVE",
            }
            for s in CANONICAL_PRICE_SOURCES
        ],
    )
    op.bulk_insert(
        cats_t,
        [
            {
                "id": deterministic_category_id(c.code),
                "category_code": c.code,
                "name": c.name,
                "description": c.description,
                "unit": c.unit,
                "quality_basis": c.quality_basis,
                "age_group": c.age_group,
                "is_active": True,
            }
            for c in CANONICAL_PRICE_CATEGORIES
        ],
    )


def downgrade() -> None:
    op.drop_table("public_notices")
    op.drop_table("public_pages")
    op.drop_table("disbun_reference_prices")
    op.drop_table("price_verification_events")
    op.drop_table("mill_price_quotes")
    op.drop_table("price_categories")
    op.drop_table("price_sources")
