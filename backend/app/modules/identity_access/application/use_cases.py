"""Use cases for authentication, session lifecycle, CSRF protection, and user access control."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from app.core.exceptions import AppError, ErrorCode
from app.core.logging import get_logger
from app.modules.identity_access.application.ports import (
    CsrfManagerPort,
    IdentityRepositoryPort,
    LoginRateLimiterPort,
    PasswordHasherPort,
    SessionCachePort,
)
from app.modules.identity_access.domain.entities import (
    AccountStatus,
    AdminUserRecord,
    AuthenticatedPrincipal,
    RoleCode,
    ScopeType,
    UserAccountEntity,
)
from app.modules.identity_access.domain.rules import (
    compute_effective_permissions,
    is_non_approver_admin,
    validate_new_password,
    validate_role_scope_assignment,
)

logger = get_logger("app.identity_access.application")


def hash_session_token(raw_token: str) -> str:
    """Return SHA-256 hex digest of raw session cookie token (never store raw token)."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _to_principal(session_id: UUID, user: UserAccountEntity) -> AuthenticatedPrincipal:
    effective_perms = compute_effective_permissions(user.roles, user.permissions)
    return AuthenticatedPrincipal(
        session_id=session_id,
        user_id=user.id,
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        linked_party_id=user.linked_party_id,
        status=user.status,
        roles=user.roles,
        access_scopes=user.access_scopes,
        permissions=effective_perms,
        last_login_at=user.last_login_at,
        non_approver_admin=is_non_approver_admin(user.roles),
    )


@dataclass(frozen=True, slots=True)
class LoginResult:
    """Output of successful login including raw cookie secret (only set on HttpOnly cookie)."""

    principal: AuthenticatedPrincipal
    raw_session_token: str
    ttl_seconds: int


class IdentityAccessService:
    """Orchestrates authentication, session security, and RBAC administration."""

    def __init__(
        self,
        *,
        repo: IdentityRepositoryPort,
        session_cache: SessionCachePort,
        rate_limiter: LoginRateLimiterPort,
        hasher: PasswordHasherPort,
        csrf: CsrfManagerPort,
        session_ttl_seconds: int,
    ) -> None:
        self._repo = repo
        self._session_cache = session_cache
        self._rate_limiter = rate_limiter
        self._hasher = hasher
        self._csrf = csrf
        self._session_ttl_seconds = session_ttl_seconds

    async def issue_csrf(self, raw_session_token: str | None) -> str:
        """Issue session-bound CSRF token if authenticated, else pre-auth bootstrap token."""
        if raw_session_token:
            try:
                principal = await self.resolve_session(raw_session_token)
                return self._csrf.issue_for_session(principal.session_id)
            except AppError as exc:
                if exc.code == ErrorCode.SYS_DEPENDENCY_UNAVAILABLE:
                    raise
        return self._csrf.issue_pre_auth()

    async def login(
        self,
        *,
        username: str,
        password: str,
        client_ip: str,
        user_agent: str | None,
        previous_raw_token: str | None,
    ) -> LoginResult:
        """Authenticate credentials, rotate session ID, enforce rate limits & Redis."""
        normalized_username = username.strip()
        await self._rate_limiter.check_allowed(client_ip=client_ip, username=normalized_username)
        await self._session_cache.ping_required("login_session_store")

        user = await self._repo.get_user_by_username(normalized_username)
        if user is None:
            await self._hasher.verify_dummy(password)
            await self._handle_failed_login(
                user=None,
                attempted_username=normalized_username,
                client_ip=client_ip,
                reason="unknown_username",
            )
            raise AppError(ErrorCode.AUTH_INVALID_CREDENTIALS)

        password_ok = await self._hasher.verify_password(password, user.password_hash)
        if not password_ok:
            await self._handle_failed_login(
                user=user,
                attempted_username=normalized_username,
                client_ip=client_ip,
                reason="invalid_password",
            )
            raise AppError(ErrorCode.AUTH_INVALID_CREDENTIALS)

        if user.status != AccountStatus.ACTIVE:
            await self._handle_failed_login(
                user=user,
                attempted_username=normalized_username,
                client_ip=client_ip,
                reason=f"account_status_{user.status.value.lower()}",
            )
            raise AppError(ErrorCode.AUTH_INVALID_CREDENTIALS)

        now = datetime.now(UTC)
        expires_at = now + timedelta(seconds=self._session_ttl_seconds)
        new_session_id = uuid4()
        new_raw_token = secrets.token_urlsafe(32)
        new_token_hash = hash_session_token(new_raw_token)
        prev_hash = hash_session_token(previous_raw_token) if previous_raw_token else None

        await self._repo.create_login_session(
            user_id=user.id,
            session_id=new_session_id,
            session_token_hash=new_token_hash,
            created_at=now,
            expires_at=expires_at,
            security_metadata={
                "client_ip": client_ip,
                "user_agent": (user_agent or "")[:200],
            },
            previous_token_hash=prev_hash,
        )
        await self._session_cache.store_session(
            token_hash=new_token_hash,
            user_id=user.id,
            session_id=new_session_id,
            ttl_seconds=self._session_ttl_seconds,
        )
        if prev_hash:
            await self._session_cache.delete_session(prev_hash)
        await self._rate_limiter.clear_failures(client_ip=client_ip, username=normalized_username)

        logger.info(
            "auth_login_succeeded",
            extra={
                "structured": {
                    "event": "auth_login_succeeded",
                    "user_id": str(user.id),
                    "roles": [r.value for r in user.roles],
                }
            },
        )
        refreshed = UserAccountEntity(
            id=user.id,
            username=user.username,
            email=user.email,
            display_name=user.display_name,
            password_hash="",
            linked_party_id=user.linked_party_id,
            status=user.status,
            failed_login_count=0,
            last_login_at=now,
            roles=user.roles,
            access_scopes=user.access_scopes,
            permissions=user.permissions,
        )
        return LoginResult(
            principal=_to_principal(new_session_id, refreshed),
            raw_session_token=new_raw_token,
            ttl_seconds=self._session_ttl_seconds,
        )

    async def _handle_failed_login(
        self,
        *,
        user: UserAccountEntity | None,
        attempted_username: str,
        client_ip: str,
        reason: str,
    ) -> None:
        await self._repo.record_failed_login(
            user_id=user.id if user is not None else None,
            attempted_username=attempted_username,
            client_ip=client_ip,
            failure_reason=reason,
        )
        await self._rate_limiter.record_failure(client_ip=client_ip, username=attempted_username)
        logger.warning(
            "auth_login_failed",
            extra={
                "structured": {
                    "event": "auth_login_failed",
                    "attempted_username": attempted_username,
                    "reason": reason,
                    "client_ip": client_ip,
                }
            },
        )

    async def resolve_session(self, raw_token: str | None) -> AuthenticatedPrincipal:
        """Resolve and validate active session from Redis + PostgreSQL fail-closed."""
        if not raw_token:
            raise AppError(ErrorCode.AUTH_REQUIRED)

        await self._session_cache.ping_required("session_verify")
        token_hash = hash_session_token(raw_token)
        redis_active = await self._session_cache.is_session_present(token_hash)

        record = await self._repo.get_session_and_user(token_hash)
        if record is None:
            raise AppError(ErrorCode.AUTH_REQUIRED)

        sess, user = record
        now = datetime.now(UTC)
        if (
            sess.revoked_at is not None
            or sess.expires_at <= now
            or not redis_active
            or user.status != AccountStatus.ACTIVE
        ):
            await self._session_cache.delete_session(token_hash)
            raise AppError(ErrorCode.AUTH_SESSION_EXPIRED)

        if (now - sess.last_seen_at) > timedelta(seconds=60):
            await self._repo.touch_session(sess.id, now)

        return _to_principal(sess.id, user)

    def verify_csrf(self, *, csrf_header: str | None, session_id: UUID) -> None:
        """Validate session-bound X-CSRF-Token or raise AUTH_CSRF_INVALID (403)."""
        if not self._csrf.verify_for_session(csrf_header, session_id):
            raise AppError(ErrorCode.AUTH_CSRF_INVALID)

    async def logout(self, *, principal: AuthenticatedPrincipal, raw_token: str) -> None:
        """Revoke active server-side session across PostgreSQL & Redis cleanly."""
        now = datetime.now(UTC)
        token_hash = hash_session_token(raw_token)
        await self._repo.revoke_session(
            session_id=principal.session_id,
            actor_id=principal.user_id,
            revoked_at=now,
            reason="user_logout",
        )
        await self._session_cache.delete_session(token_hash)
        logger.info(
            "auth_logout_completed",
            extra={"structured": {"event": "auth_logout", "user_id": str(principal.user_id)}},
        )

    async def list_users(
        self,
        *,
        page: int,
        page_size: int,
        query: str | None,
    ) -> tuple[list[AdminUserRecord], int]:
        """List internal accounts for SYSTEM_ADMIN without exposing credentials."""
        return await self._repo.list_users(page=page, page_size=page_size, query=query)

    async def create_user(
        self,
        *,
        actor: AuthenticatedPrincipal,
        username: str,
        email: str | None,
        raw_password: str,
        role_code: RoleCode,
        scope_type: ScopeType,
        farmer_id: UUID | None,
        cooperative_id: UUID | None,
        mill_id: UUID | None,
    ) -> AdminUserRecord:
        """Create internal user with explicit role, scope validation, & Argon2id hash."""
        clean_username = username.strip()
        if len(clean_username) < 3:
            raise AppError(ErrorCode.VAL_INVALID_FORMAT, "Username minimal 3 karakter.")
        validate_new_password(raw_password, clean_username)
        validate_role_scope_assignment(role_code, scope_type, farmer_id, cooperative_id, mill_id)

        existing = await self._repo.get_user_by_username(clean_username)
        if existing is not None:
            raise AppError(
                ErrorCode.MD_DUPLICATE_CODE,
                "Username sudah terdaftar dan tidak boleh duplikat.",
            )

        pw_hash = await self._hasher.hash_password(raw_password)
        clean_email = email.strip().lower() if email and email.strip() else None
        return await self._repo.create_user(
            username=clean_username,
            email=clean_email,
            display_name=clean_username,
            password_hash=pw_hash,
            role_code=role_code,
            scope_type=scope_type,
            farmer_id=farmer_id,
            cooperative_id=cooperative_id,
            mill_id=mill_id,
            granted_by=actor.user_id,
        )

    async def update_user_access(
        self,
        *,
        actor: AuthenticatedPrincipal,
        target_user_id: UUID,
        status: AccountStatus | None,
        role_code: RoleCode | None,
        scope_type: ScopeType | None,
        farmer_id: UUID | None,
        cooperative_id: UUID | None,
        mill_id: UUID | None,
        reason: str,
    ) -> AdminUserRecord:
        """Update user status/role/scope and immediately revoke active sessions."""
        target = await self._repo.get_user_by_id(target_user_id)
        if target is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)

        effective_role = role_code if role_code is not None else target.roles[0]
        if scope_type is not None:
            eff_scope = scope_type
            eff_farmer = farmer_id
            eff_coop = cooperative_id
            eff_mill = mill_id
        elif target.access_scopes:
            cur_scope = target.access_scopes[0]
            eff_scope = cur_scope.scope_type
            eff_farmer = cur_scope.farmer_id if farmer_id is None else farmer_id
            eff_coop = cur_scope.cooperative_id if cooperative_id is None else cooperative_id
            eff_mill = cur_scope.mill_id if mill_id is None else mill_id
        else:
            raise AppError(ErrorCode.VAL_REQUIRED_FIELD, "Scope pengguna wajib ditetapkan.")

        validate_role_scope_assignment(effective_role, eff_scope, eff_farmer, eff_coop, eff_mill)

        now = datetime.now(UTC)
        updated, revoked_hashes = await self._repo.update_user_access(
            target_user_id=target_user_id,
            status=status,
            role_code=effective_role if role_code is not None else None,
            scope_type=eff_scope if (scope_type is not None or role_code is not None) else None,
            farmer_id=eff_farmer,
            cooperative_id=eff_coop,
            mill_id=eff_mill,
            reason=reason.strip(),
            actor_id=actor.user_id,
            now=now,
        )
        if revoked_hashes:
            await self._session_cache.delete_sessions(revoked_hashes)

        logger.info(
            "admin_user_access_updated",
            extra={
                "structured": {
                    "event": "user_access_updated",
                    "target_user_id": str(target_user_id),
                    "revoked_sessions_count": len(revoked_hashes),
                }
            },
        )
        return updated
