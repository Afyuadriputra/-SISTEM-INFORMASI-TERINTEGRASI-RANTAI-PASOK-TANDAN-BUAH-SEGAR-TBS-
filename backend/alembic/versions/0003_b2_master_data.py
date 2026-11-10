"""B2 master data tables and deferred B1 foreign-key bindings (DBD §7)."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_b2_master_data"
down_revision: str | None = "0002_b1_identity_access"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "parties",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_type", sa.String(length=30), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "party_type IN ('PERUMDA', 'FARMER', 'COOPERATIVE', 'MILL_COMPANY')",
            name="ck_parties_party_type_valid",
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')", name="ck_parties_party_status_valid"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_parties"),
    )

    op.create_table(
        "cooperatives",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cooperative_code", sa.String(length=40), nullable=False),
        sa.Column("cooperative_name", sa.String(length=180), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("contact_phone", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')", name="ck_cooperatives_cooperative_status_valid"
        ),
        sa.ForeignKeyConstraint(
            ["party_id"], ["parties.id"], name="fk_cooperatives_party_id_parties"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_cooperatives"),
        sa.UniqueConstraint("cooperative_code", name="uq_cooperatives_cooperative_code"),
        sa.UniqueConstraint("party_id", name="uq_cooperatives_party_id"),
    )

    op.create_table(
        "farmers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farmer_code", sa.String(length=40), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("contact_phone", sa.String(length=30), nullable=False),
        sa.Column("identity_reference", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')", name="ck_farmers_farmer_status_valid"
        ),
        sa.CheckConstraint("version >= 1", name="ck_farmers_farmer_version_positive"),
        sa.ForeignKeyConstraint(["party_id"], ["parties.id"], name="fk_farmers_party_id_parties"),
        sa.PrimaryKeyConstraint("id", name="pk_farmers"),
        sa.UniqueConstraint("farmer_code", name="uq_farmers_farmer_code"),
        sa.UniqueConstraint("party_id", name="uq_farmers_party_id"),
    )
    op.create_index("ix_farmers_farmer_code", "farmers", ["farmer_code"])

    op.create_table(
        "cooperative_memberships",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cooperative_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("membership_number", sa.String(length=60), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="ck_cooperative_memberships_membership_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["cooperative_id"],
            ["cooperatives.id"],
            name="fk_cooperative_memberships_cooperative_id_cooperatives",
        ),
        sa.ForeignKeyConstraint(
            ["farmer_id"], ["farmers.id"], name="fk_cooperative_memberships_farmer_id_farmers"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_cooperative_memberships"),
    )
    op.create_index(
        "ix_cooperative_memberships_coop_farmer",
        "cooperative_memberships",
        ["cooperative_id", "farmer_id"],
    )
    op.create_index(
        "uq_cooperative_memberships_active_farmer",
        "cooperative_memberships",
        ["farmer_id"],
        unique=True,
        postgresql_where=sa.text("status = 'ACTIVE' AND ended_at IS NULL"),
    )

    op.create_table(
        "farms",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farm_code", sa.String(length=40), nullable=False),
        sa.Column("farm_name", sa.String(length=150), nullable=False),
        sa.Column("area_hectares", sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column("planting_year", sa.Integer(), nullable=True),
        sa.Column("stdb_number", sa.String(length=100), nullable=True),
        sa.Column("village", sa.String(length=100), nullable=False),
        sa.Column("district", sa.String(length=100), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("verification_status", sa.String(length=20), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("area_hectares > 0", name="ck_farms_farm_area_positive"),
        sa.CheckConstraint(
            "planting_year IS NULL OR (planting_year BETWEEN 1970 AND 2035)",
            name="ck_farms_farm_planting_year_range",
        ),
        sa.CheckConstraint(
            "(latitude IS NULL AND longitude IS NULL) OR "
            "(latitude IS NOT NULL AND longitude IS NOT NULL)",
            name="ck_farms_farm_paired_coordinates",
        ),
        sa.CheckConstraint(
            "latitude IS NULL OR (latitude >= -90 AND latitude <= 90)",
            name="ck_farms_farm_lat_range",
        ),
        sa.CheckConstraint(
            "longitude IS NULL OR (longitude >= -180 AND longitude <= 180)",
            name="ck_farms_farm_lng_range",
        ),
        sa.CheckConstraint(
            "verification_status IN ('UNVERIFIED', 'VERIFIED')",
            name="ck_farms_farm_verification_valid",
        ),
        sa.CheckConstraint("version >= 1", name="ck_farms_farm_version_positive"),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"], name="fk_farms_farmer_id_farmers"),
        sa.PrimaryKeyConstraint("id", name="pk_farms"),
        sa.UniqueConstraint("farm_code", name="uq_farms_farm_code"),
    )
    op.create_index("ix_farms_farmer_id", "farms", ["farmer_id"])

    op.create_table(
        "mill_companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_code", sa.String(length=40), nullable=False),
        sa.Column("company_name", sa.String(length=180), nullable=False),
        sa.Column("contact_phone", sa.String(length=30), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')", name="ck_mill_companies_mill_company_status_valid"
        ),
        sa.ForeignKeyConstraint(
            ["party_id"], ["parties.id"], name="fk_mill_companies_party_id_parties"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_mill_companies"),
        sa.UniqueConstraint("company_code", name="uq_mill_companies_company_code"),
        sa.UniqueConstraint("party_id", name="uq_mill_companies_party_id"),
    )

    op.create_table(
        "mills",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mill_company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mill_code", sa.String(length=40), nullable=False),
        sa.Column("mill_name", sa.String(length=180), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("district", sa.String(length=100), nullable=False),
        sa.Column("regency", sa.String(length=100), nullable=False),
        sa.Column("province", sa.String(length=100), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("contact_phone", sa.String(length=30), nullable=True),
        sa.Column("partnership_status", sa.String(length=20), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("location_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "(latitude IS NULL AND longitude IS NULL) OR "
            "(latitude IS NOT NULL AND longitude IS NOT NULL)",
            name="ck_mills_mill_paired_coordinates",
        ),
        sa.CheckConstraint(
            "latitude IS NULL OR (latitude >= -90 AND latitude <= 90)",
            name="ck_mills_mill_lat_range",
        ),
        sa.CheckConstraint(
            "longitude IS NULL OR (longitude >= -180 AND longitude <= 180)",
            name="ck_mills_mill_lng_range",
        ),
        sa.CheckConstraint(
            "partnership_status IN ('ACTIVE', 'INACTIVE')",
            name="ck_mills_mill_partnership_status_valid",
        ),
        sa.CheckConstraint("version >= 1", name="ck_mills_mill_version_positive"),
        sa.ForeignKeyConstraint(
            ["mill_company_id"],
            ["mill_companies.id"],
            name="fk_mills_mill_company_id_mill_companies",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_mills"),
        sa.UniqueConstraint("mill_code", name="uq_mills_mill_code"),
    )
    op.create_index("ix_mills_code_regency", "mills", ["mill_code", "regency"])
    op.create_index("ix_mills_public_partnership", "mills", ["is_public", "partnership_status"])

    op.create_table(
        "perumda_offices",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("office_name", sa.String(length=180), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("public_contact", sa.String(length=100), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "(latitude IS NULL AND longitude IS NULL) OR "
            "(latitude IS NOT NULL AND longitude IS NOT NULL)",
            name="ck_perumda_offices_office_paired_coordinates",
        ),
        sa.ForeignKeyConstraint(
            ["party_id"], ["parties.id"], name="fk_perumda_offices_party_id_parties"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_perumda_offices"),
    )

    op.create_table(
        "vehicles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plate_number", sa.String(length=25), nullable=False),
        sa.Column("vehicle_type", sa.String(length=80), nullable=False),
        sa.Column("nominal_capacity_kg", sa.Numeric(precision=14, scale=3), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "nominal_capacity_kg IS NULL OR nominal_capacity_kg > 0",
            name="ck_vehicles_vehicle_capacity_positive",
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')", name="ck_vehicles_vehicle_status_valid"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_vehicles"),
        sa.UniqueConstraint("plate_number", name="uq_vehicles_plate_number"),
    )

    op.create_table(
        "drivers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("contact_phone", sa.String(length=30), nullable=False),
        sa.Column("driver_reference", sa.String(length=60), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')", name="ck_drivers_driver_status_valid"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_drivers"),
    )

    # Deferred B1 foreign keys now that master_data tables exist.
    op.create_foreign_key(
        "fk_user_accounts_linked_party_id_parties",
        "user_accounts",
        "parties",
        ["linked_party_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_user_access_scopes_farmer_id_farmers",
        "user_access_scopes",
        "farmers",
        ["farmer_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_user_access_scopes_cooperative_id_cooperatives",
        "user_access_scopes",
        "cooperatives",
        ["cooperative_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_user_access_scopes_mill_id_mills",
        "user_access_scopes",
        "mills",
        ["mill_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_user_access_scopes_mill_id_mills", "user_access_scopes", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_user_access_scopes_cooperative_id_cooperatives",
        "user_access_scopes",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_user_access_scopes_farmer_id_farmers", "user_access_scopes", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_user_accounts_linked_party_id_parties", "user_accounts", type_="foreignkey"
    )

    op.drop_table("drivers")
    op.drop_table("vehicles")
    op.drop_table("perumda_offices")
    op.drop_table("mills")
    op.drop_table("mill_companies")
    op.drop_table("farms")
    op.drop_table("cooperative_memberships")
    op.drop_table("farmers")
    op.drop_table("cooperatives")
    op.drop_table("parties")
