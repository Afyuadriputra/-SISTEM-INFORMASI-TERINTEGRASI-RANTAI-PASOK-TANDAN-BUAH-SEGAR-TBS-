"""B1 identity, access, session, and append-only audit tables."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.modules.identity_access.domain.rules import (
    CANONICAL_PERMISSIONS,
    ROLE_METADATA,
    ROLE_PERMISSIONS_MAP,
)
from app.modules.identity_access.infrastructure.models import (
    deterministic_permission_id,
    deterministic_role_id,
)

# revision identifiers, used by Alembic.
revision: str = "0002_b1_identity_access"
down_revision: str | None = "0001_b0_baseline"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id", name="pk_roles"),
        sa.UniqueConstraint("code", name="uq_roles_code"),
    )

    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("module", sa.String(length=50), nullable=False),
        sa.Column("resource", sa.String(length=80), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_permissions"),
        sa.UniqueConstraint("code", name="uq_permissions_code"),
    )

    op.create_table(
        "role_permissions",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
            ondelete="CASCADE",
            name="fk_role_permissions_permission_id_permissions",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"], ["roles.id"], ondelete="CASCADE", name="fk_role_permissions_role_id_roles"
        ),
        sa.PrimaryKeyConstraint("role_id", "permission_id", name="pk_role_permissions"),
    )

    op.create_table(
        "user_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=150), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("linked_party_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("failed_login_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE', 'LOCKED')", name="ck_user_accounts_account_status"
        ),
        sa.CheckConstraint(
            "failed_login_count >= 0", name="ck_user_accounts_failed_login_non_negative"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_user_accounts"),
        sa.UniqueConstraint("username", name="uq_user_accounts_username"),
    )
    op.create_index("ix_user_accounts_username", "user_accounts", ["username"])
    op.create_index("ix_user_accounts_status", "user_accounts", ["status"])

    op.create_table(
        "user_role_grants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("granted_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["granted_by"],
            ["user_accounts.id"],
            name="fk_user_role_grants_granted_by_user_accounts",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"], ["roles.id"], name="fk_user_role_grants_role_id_roles"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user_accounts.id"], name="fk_user_role_grants_user_id_user_accounts"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_user_role_grants"),
    )
    op.create_index(
        "ix_user_role_grants_user_active", "user_role_grants", ["user_id", "revoked_at"]
    )
    op.create_index(
        "uq_user_role_grants_active_pair",
        "user_role_grants",
        ["user_id", "role_id"],
        unique=True,
        postgresql_where=sa.text("revoked_at IS NULL"),
    )

    op.create_table(
        "user_access_scopes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scope_type", sa.String(length=30), nullable=False),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cooperative_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("mill_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("granted_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "("
            "(scope_type = 'FARMER' AND farmer_id IS NOT NULL "
            "AND cooperative_id IS NULL AND mill_id IS NULL) OR "
            "(scope_type = 'COOPERATIVE' AND cooperative_id IS NOT NULL "
            "AND farmer_id IS NULL AND mill_id IS NULL) OR "
            "(scope_type = 'MILL' AND mill_id IS NOT NULL "
            "AND farmer_id IS NULL AND cooperative_id IS NULL) OR "
            "(scope_type = 'PERUMDA_GLOBAL' AND farmer_id IS NULL "
            "AND cooperative_id IS NULL AND mill_id IS NULL)"
            ")",
            name="ck_user_access_scopes_scope_target_consistency",
        ),
        sa.ForeignKeyConstraint(
            ["granted_by"],
            ["user_accounts.id"],
            name="fk_user_access_scopes_granted_by_user_accounts",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user_accounts.id"], name="fk_user_access_scopes_user_id_user_accounts"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_user_access_scopes"),
    )
    op.create_index(
        "ix_user_access_scopes_user_active", "user_access_scopes", ["user_id", "revoked_at"]
    )

    op.create_table(
        "auth_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "security_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user_accounts.id"], name="fk_auth_sessions_user_id_user_accounts"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_auth_sessions"),
        sa.UniqueConstraint("session_token_hash", name="uq_auth_sessions_session_token_hash"),
    )
    op.create_index(
        "ix_auth_sessions_user_status", "auth_sessions", ["user_id", "revoked_at", "expires_at"]
    )

    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("module", sa.String(length=50), nullable=False),
        sa.Column("resource_type", sa.String(length=80), nullable=False),
        sa.Column("resource_id", sa.String(length=100), nullable=False),
        sa.Column("previous_state", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("new_state", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("request_id", sa.String(length=80), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_audit_events"),
    )
    op.create_index(
        "ix_audit_events_resource_lookup",
        "audit_events",
        ["resource_type", "resource_id", "occurred_at"],
    )
    op.create_index("ix_audit_events_module_occurred", "audit_events", ["module", "occurred_at"])
    op.create_index("ix_audit_events_request_id", "audit_events", ["request_id"])

    op.execute(
        """
        CREATE OR REPLACE FUNCTION prevent_audit_events_mutation()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'audit_events is append-only; UPDATE and DELETE are forbidden';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_audit_events_append_only
        BEFORE UPDATE OR DELETE ON audit_events
        FOR EACH ROW
        EXECUTE FUNCTION prevent_audit_events_mutation();
        """
    )

    # Deterministic canonical RBAC seed matching contracts/role-permissions.yaml.
    roles_table = sa.table(
        "roles",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("is_active", sa.Boolean),
    )
    permissions_table = sa.table(
        "permissions",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("code", sa.String),
        sa.column("module", sa.String),
        sa.column("resource", sa.String),
        sa.column("action", sa.String),
        sa.column("description", sa.Text),
    )
    role_perms_table = sa.table(
        "role_permissions",
        sa.column("role_id", postgresql.UUID(as_uuid=True)),
        sa.column("permission_id", postgresql.UUID(as_uuid=True)),
    )

    op.bulk_insert(
        roles_table,
        [
            {
                "id": deterministic_role_id(rc.value),
                "code": rc.value,
                "name": name,
                "description": desc,
                "is_active": True,
            }
            for rc, (name, desc) in ROLE_METADATA.items()
        ],
    )
    op.bulk_insert(
        permissions_table,
        [
            {
                "id": deterministic_permission_id(spec.code),
                "code": spec.code,
                "module": spec.module,
                "resource": spec.resource,
                "action": spec.action,
                "description": spec.description,
            }
            for spec in CANONICAL_PERMISSIONS
        ],
    )
    op.bulk_insert(
        role_perms_table,
        [
            {
                "role_id": deterministic_role_id(rc.value),
                "permission_id": deterministic_permission_id(perm_code),
            }
            for rc, perms in ROLE_PERMISSIONS_MAP.items()
            for perm_code in perms
        ],
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_audit_events_append_only ON audit_events;")
    op.execute("DROP FUNCTION IF EXISTS prevent_audit_events_mutation();")
    op.drop_table("audit_events")
    op.drop_table("auth_sessions")
    op.drop_table("user_access_scopes")
    op.drop_table("user_role_grants")
    op.drop_table("user_accounts")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_table("roles")
