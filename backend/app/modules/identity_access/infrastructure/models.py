"""SQLAlchemy 2 ORM models for Identity & Access (DBD §6.1-6.7) and RBAC catalog seeding."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.modules.identity_access.domain.rules import (
    CANONICAL_PERMISSIONS,
    ROLE_METADATA,
    ROLE_PERMISSIONS_MAP,
)


class RoleModel(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    role_permissions: Mapped[list[RolePermissionModel]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
    )


class PermissionModel(Base):
    __tablename__ = "permissions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    resource: Mapped[str] = mapped_column(String(80), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)


class RolePermissionModel(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )

    role: Mapped[RoleModel] = relationship(back_populates="role_permissions")
    permission: Mapped[PermissionModel] = relationship()


class UserAccountModel(Base):
    __tablename__ = "user_accounts"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str] = mapped_column(String(150), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    # FK to parties(id) is added in Milestone B2 when master_data tables are created.
    linked_party_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    failed_login_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    role_grants: Mapped[list[UserRoleGrantModel]] = relationship(
        foreign_keys="UserRoleGrantModel.user_id",
        back_populates="user",
    )
    access_scopes: Mapped[list[UserAccessScopeModel]] = relationship(
        foreign_keys="UserAccessScopeModel.user_id",
        back_populates="user",
    )

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'INACTIVE', 'LOCKED')", name="account_status"),
        CheckConstraint("failed_login_count >= 0", name="failed_login_non_negative"),
        Index("ix_user_accounts_username", "username"),
        Index("ix_user_accounts_status", "status"),
    )


class UserRoleGrantModel(Base):
    __tablename__ = "user_role_grants"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    role_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False
    )
    granted_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=True
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[UserAccountModel] = relationship(
        foreign_keys=[user_id], back_populates="role_grants"
    )
    role: Mapped[RoleModel] = relationship()

    __table_args__ = (
        Index("ix_user_role_grants_user_active", "user_id", "revoked_at"),
        Index(
            "uq_user_role_grants_active_pair",
            "user_id",
            "role_id",
            unique=True,
            postgresql_where=text("revoked_at IS NULL"),
        ),
    )


class UserAccessScopeModel(Base):
    __tablename__ = "user_access_scopes"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    scope_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # FKs to farmers/cooperatives/mills are added in B2 migration once master_data tables exist.
    farmer_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    cooperative_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    mill_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    granted_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[UserAccountModel] = relationship(
        foreign_keys=[user_id], back_populates="access_scopes"
    )

    __table_args__ = (
        CheckConstraint(
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
            name="scope_target_consistency",
        ),
        Index("ix_user_access_scopes_user_active", "user_id", "revoked_at"),
    )


class AuthSessionModel(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    session_token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    security_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    __table_args__ = (Index("ix_auth_sessions_user_status", "user_id", "revoked_at", "expires_at"),)


def deterministic_role_id(role_code: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"agroniaga:role:{role_code}")


def deterministic_permission_id(permission_code: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"agroniaga:permission:{permission_code}")


async def seed_rbac_catalog(session: AsyncSession) -> None:
    """Idempotently seed canonical 7 roles, 64 permissions, and role-permission mappings."""
    role_rows = [
        {
            "id": deterministic_role_id(role_code.value),
            "code": role_code.value,
            "name": name,
            "description": desc,
            "is_active": True,
        }
        for role_code, (name, desc) in ROLE_METADATA.items()
    ]
    await session.execute(insert(RoleModel).values(role_rows).on_conflict_do_nothing())

    perm_rows = [
        {
            "id": deterministic_permission_id(spec.code),
            "code": spec.code,
            "module": spec.module,
            "resource": spec.resource,
            "action": spec.action,
            "description": spec.description,
        }
        for spec in CANONICAL_PERMISSIONS
    ]
    await session.execute(insert(PermissionModel).values(perm_rows).on_conflict_do_nothing())

    mapping_rows = [
        {
            "role_id": deterministic_role_id(role_code.value),
            "permission_id": deterministic_permission_id(perm_code),
        }
        for role_code, perms in ROLE_PERMISSIONS_MAP.items()
        for perm_code in perms
    ]
    await session.execute(insert(RolePermissionModel).values(mapping_rows).on_conflict_do_nothing())
    await session.flush()
