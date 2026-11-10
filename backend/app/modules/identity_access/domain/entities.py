"""Pure domain entities and value objects for identity, roles, scopes, and sessions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class RoleCode(StrEnum):
    """Canonical internal roles aligned 1:1 with contracts/role-permissions.yaml."""

    FARMER = "FARMER"
    COOPERATIVE_OPERATOR = "COOPERATIVE_OPERATOR"
    PERUMDA_OPERATIONS = "PERUMDA_OPERATIONS"
    PERUMDA_FINANCE = "PERUMDA_FINANCE"
    MILL_OPERATOR = "MILL_OPERATOR"
    DIRECTOR = "DIRECTOR"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"


class ScopeType(StrEnum):
    """Canonical resource isolation scopes aligned with DBD §6.6."""

    FARMER = "FARMER"
    COOPERATIVE = "COOPERATIVE"
    MILL = "MILL"
    PERUMDA_GLOBAL = "PERUMDA_GLOBAL"


class AccountStatus(StrEnum):
    """Lifecycle states of internal user accounts."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LOCKED = "LOCKED"


@dataclass(frozen=True, slots=True)
class AccessScopeEntity:
    """Active resource isolation grant assigned to an internal user."""

    id: UUID
    scope_type: ScopeType
    farmer_id: UUID | None
    cooperative_id: UUID | None
    mill_id: UUID | None


@dataclass(frozen=True, slots=True)
class UserAccountEntity:
    """Loaded user account aggregate including roles and active scope grants."""

    id: UUID
    username: str
    email: str | None
    display_name: str
    password_hash: str
    linked_party_id: UUID | None
    status: AccountStatus
    failed_login_count: int
    last_login_at: datetime | None
    roles: tuple[RoleCode, ...]
    access_scopes: tuple[AccessScopeEntity, ...]
    permissions: frozenset[str]


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    """Resolved authenticated actor identity, effective permissions, and scopes."""

    session_id: UUID
    user_id: UUID
    username: str
    email: str | None
    display_name: str
    linked_party_id: UUID | None
    status: AccountStatus
    roles: tuple[RoleCode, ...]
    access_scopes: tuple[AccessScopeEntity, ...]
    permissions: frozenset[str]
    last_login_at: datetime | None
    non_approver_admin: bool


@dataclass(frozen=True, slots=True)
class AuthSessionRecord:
    """Server-side persisted authentication session metadata."""

    id: UUID
    user_id: UUID
    session_token_hash: str
    created_at: datetime
    expires_at: datetime
    revoked_at: datetime | None
    last_seen_at: datetime


@dataclass(frozen=True, slots=True)
class AdminUserRecord:
    """Administrative projection of user account without password hashes."""

    id: UUID
    username: str
    email: str | None
    status: AccountStatus
    failed_login_count: int
    last_login_at: datetime | None
    roles: tuple[RoleCode, ...]
    access_scopes: tuple[AccessScopeEntity, ...]
    non_approver_enforced: bool
