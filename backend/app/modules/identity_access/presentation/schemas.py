"""Strict Pydantic schemas aligned 1:1 with OpenAPI Auth & AdminUser contracts."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from app.core.logging import format_utc_iso
from app.core.schemas import PaginationMeta, StrictContractModel, build_pagination_meta
from app.modules.identity_access.domain.entities import (
    AccountStatus,
    AdminUserRecord,
    AuthenticatedPrincipal,
    RoleCode,
    ScopeType,
)


class CsrfTokenData(StrictContractModel):
    csrf_token: str
    header_name: Literal["X-CSRF-Token"] = "X-CSRF-Token"


class CsrfEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: CsrfTokenData
    meta: dict[str, Any] | None = None
    request_id: str


class LoginRequest(StrictContractModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=128)


class AccessScopeGrantDto(StrictContractModel):
    id: UUID
    scope_type: ScopeType
    farmer_id: UUID | None
    cooperative_id: UUID | None
    mill_id: UUID | None


class AuthenticatedUserDto(StrictContractModel):
    id: UUID
    username: str
    email: str | None
    display_name: str
    linked_party_id: UUID | None
    status: AccountStatus
    roles: list[RoleCode]
    access_scopes: list[AccessScopeGrantDto]
    permissions: list[str]
    last_login_at: str | None
    non_approver_admin: bool


class AuthUserEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: AuthenticatedUserDto
    meta: dict[str, Any] | None = None
    request_id: str


class LogoutData(StrictContractModel):
    logged_out: Literal[True] = True
    redirect_to: Literal["/login"] = "/login"


class LogoutEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: LogoutData
    meta: dict[str, Any] | None = None
    request_id: str


class AdminUserSummaryDto(StrictContractModel):
    id: UUID
    username: str
    email: str | None
    status: AccountStatus
    failed_login_count: int = Field(ge=0)
    last_login_at: str | None
    roles: list[RoleCode]
    access_scopes: list[AccessScopeGrantDto]
    non_approver_enforced: bool


class AdminUserEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: AdminUserSummaryDto
    meta: dict[str, Any] | None = None
    request_id: str


class AdminUserListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[AdminUserSummaryDto]
    meta: PaginationMeta
    request_id: str


class CreateUserRequest(StrictContractModel):
    username: str = Field(min_length=3, max_length=100)
    email: str | None = None
    password: str = Field(min_length=10, max_length=128)
    role_code: RoleCode
    scope_type: ScopeType
    farmer_id: UUID | None = None
    cooperative_id: UUID | None = None
    mill_id: UUID | None = None


class UpdateUserAccessRequest(StrictContractModel):
    status: AccountStatus | None = None
    role_code: RoleCode | None = None
    scope_type: ScopeType | None = None
    farmer_id: UUID | None = None
    cooperative_id: UUID | None = None
    mill_id: UUID | None = None
    reason: str = Field(min_length=5, max_length=500)


def principal_to_dto(principal: AuthenticatedPrincipal) -> AuthenticatedUserDto:
    return AuthenticatedUserDto(
        id=principal.user_id,
        username=principal.username,
        email=principal.email,
        display_name=principal.display_name,
        linked_party_id=principal.linked_party_id,
        status=principal.status,
        roles=list(principal.roles),
        access_scopes=[
            AccessScopeGrantDto(
                id=s.id,
                scope_type=s.scope_type,
                farmer_id=s.farmer_id,
                cooperative_id=s.cooperative_id,
                mill_id=s.mill_id,
            )
            for s in principal.access_scopes
        ],
        permissions=sorted(principal.permissions),
        last_login_at=format_utc_iso(principal.last_login_at),
        non_approver_admin=principal.non_approver_admin,
    )


def admin_record_to_dto(record: AdminUserRecord) -> AdminUserSummaryDto:
    return AdminUserSummaryDto(
        id=record.id,
        username=record.username,
        email=record.email,
        status=record.status,
        failed_login_count=record.failed_login_count,
        last_login_at=format_utc_iso(record.last_login_at),
        roles=list(record.roles),
        access_scopes=[
            AccessScopeGrantDto(
                id=s.id,
                scope_type=s.scope_type,
                farmer_id=s.farmer_id,
                cooperative_id=s.cooperative_id,
                mill_id=s.mill_id,
            )
            for s in record.access_scopes
        ],
        non_approver_enforced=record.non_approver_enforced,
    )


__all__ = [
    "AdminUserEnvelope",
    "AdminUserListEnvelope",
    "AuthUserEnvelope",
    "CreateUserRequest",
    "CsrfEnvelope",
    "CsrfTokenData",
    "LoginRequest",
    "LogoutData",
    "LogoutEnvelope",
    "UpdateUserAccessRequest",
    "admin_record_to_dto",
    "build_pagination_meta",
    "principal_to_dto",
]
