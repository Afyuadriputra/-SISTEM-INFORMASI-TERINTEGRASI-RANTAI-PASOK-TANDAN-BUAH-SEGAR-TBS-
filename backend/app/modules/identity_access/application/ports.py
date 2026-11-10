"""Repository and security adapter ports for Identity & Access (ADR-002)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from app.modules.identity_access.domain.entities import (
    AccountStatus,
    AdminUserRecord,
    AuthSessionRecord,
    RoleCode,
    ScopeType,
    UserAccountEntity,
)


class IdentityRepositoryPort(Protocol):
    """Persistence contract backed by PostgreSQL for accounts, roles, scopes, and sessions."""

    async def get_user_by_username(self, username: str) -> UserAccountEntity | None: ...

    async def get_user_by_id(self, user_id: UUID) -> UserAccountEntity | None: ...

    async def record_failed_login(
        self,
        *,
        user_id: UUID | None,
        attempted_username: str,
        client_ip: str,
        failure_reason: str,
    ) -> None: ...

    async def create_login_session(
        self,
        *,
        user_id: UUID,
        session_id: UUID,
        session_token_hash: str,
        created_at: datetime,
        expires_at: datetime,
        security_metadata: dict[str, Any],
        previous_token_hash: str | None,
    ) -> None: ...

    async def get_session_and_user(
        self, session_token_hash: str
    ) -> tuple[AuthSessionRecord, UserAccountEntity] | None: ...

    async def touch_session(self, session_id: UUID, seen_at: datetime) -> None: ...

    async def revoke_session(
        self,
        *,
        session_id: UUID,
        actor_id: UUID | None,
        revoked_at: datetime,
        reason: str,
    ) -> None: ...

    async def list_users(
        self, *, page: int, page_size: int, query: str | None
    ) -> tuple[list[AdminUserRecord], int]: ...

    async def create_user(
        self,
        *,
        username: str,
        email: str | None,
        display_name: str,
        password_hash: str,
        role_code: RoleCode,
        scope_type: ScopeType,
        farmer_id: UUID | None,
        cooperative_id: UUID | None,
        mill_id: UUID | None,
        granted_by: UUID,
    ) -> AdminUserRecord: ...

    async def update_user_access(
        self,
        *,
        target_user_id: UUID,
        status: AccountStatus | None,
        role_code: RoleCode | None,
        scope_type: ScopeType | None,
        farmer_id: UUID | None,
        cooperative_id: UUID | None,
        mill_id: UUID | None,
        reason: str,
        actor_id: UUID,
        now: datetime,
    ) -> tuple[AdminUserRecord, list[str]]: ...

    async def record_security_event(
        self,
        *,
        actor_id: UUID | None,
        event_type: str,
        resource_type: str,
        resource_id: str,
        previous_state: dict[str, Any] | None = None,
        new_state: dict[str, Any] | None = None,
        reason: str | None = None,
    ) -> None: ...


class SessionCachePort(Protocol):
    """Fail-closed session cache contract backed by Redis."""

    async def ping_required(self, operation_name: str) -> None: ...

    async def store_session(
        self,
        *,
        token_hash: str,
        user_id: UUID,
        session_id: UUID,
        ttl_seconds: int,
    ) -> None: ...

    async def is_session_present(self, token_hash: str) -> bool: ...

    async def delete_session(self, token_hash: str) -> None: ...

    async def delete_sessions(self, token_hashes: list[str]) -> None: ...


class LoginRateLimiterPort(Protocol):
    """Fail-closed login anti-bruteforce rate limiter backed by Redis."""

    async def check_allowed(self, *, client_ip: str, username: str) -> None: ...

    async def record_failure(self, *, client_ip: str, username: str) -> None: ...

    async def clear_failures(self, *, client_ip: str, username: str) -> None: ...


class PasswordHasherPort(Protocol):
    """Argon2id password hashing contract running off the event loop."""

    async def hash_password(self, raw_password: str) -> str: ...

    async def verify_password(self, raw_password: str, encoded_hash: str) -> bool: ...

    async def verify_dummy(self, raw_password: str) -> None: ...


class CsrfManagerPort(Protocol):
    """Server-bound HMAC CSRF token issuer & verifier."""

    def issue_for_session(self, session_id: UUID) -> str: ...

    def issue_pre_auth(self) -> str: ...

    def verify_for_session(self, token: str | None, session_id: UUID) -> bool: ...
