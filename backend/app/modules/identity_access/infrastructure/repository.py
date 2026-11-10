"""PostgreSQL async repository implementation for Identity & Access."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from app.core.audit import AuditRecordInput, append_audit_event
from app.core.exceptions import AppError, ErrorCode
from app.modules.identity_access.domain.entities import (
    AccessScopeEntity,
    AccountStatus,
    AdminUserRecord,
    AuthSessionRecord,
    RoleCode,
    ScopeType,
    UserAccountEntity,
)
from app.modules.identity_access.domain.rules import is_non_approver_admin
from app.modules.identity_access.infrastructure.models import (
    AuthSessionModel,
    RoleModel,
    RolePermissionModel,
    UserAccessScopeModel,
    UserAccountModel,
    UserRoleGrantModel,
)


def _user_eager_options() -> tuple[Any, ...]:
    return (
        selectinload(UserAccountModel.role_grants)
        .selectinload(UserRoleGrantModel.role)
        .selectinload(RoleModel.role_permissions)
        .selectinload(RolePermissionModel.permission),
        selectinload(UserAccountModel.access_scopes),
    )


def _to_user_entity(row: UserAccountModel) -> UserAccountEntity:
    active_roles: list[RoleCode] = []
    seen_roles: set[RoleCode] = set()
    perms: set[str] = set()

    for grant in sorted(row.role_grants, key=lambda g: g.granted_at):
        if grant.revoked_at is not None or not grant.role.is_active:
            continue
        role_enum = RoleCode(grant.role.code)
        if role_enum not in seen_roles:
            seen_roles.add(role_enum)
            active_roles.append(role_enum)
        for rp in grant.role.role_permissions:
            perms.add(rp.permission.code)

    active_scopes = tuple(
        AccessScopeEntity(
            id=sc.id,
            scope_type=ScopeType(sc.scope_type),
            farmer_id=sc.farmer_id,
            cooperative_id=sc.cooperative_id,
            mill_id=sc.mill_id,
        )
        for sc in sorted(row.access_scopes, key=lambda s: s.created_at)
        if sc.revoked_at is None
    )

    return UserAccountEntity(
        id=row.id,
        username=row.username,
        email=row.email,
        display_name=row.display_name,
        password_hash=row.password_hash,
        linked_party_id=row.linked_party_id,
        status=AccountStatus(row.status),
        failed_login_count=row.failed_login_count,
        last_login_at=row.last_login_at,
        roles=tuple(active_roles),
        access_scopes=active_scopes,
        permissions=frozenset(perms),
    )


def _to_admin_record(row: UserAccountModel) -> AdminUserRecord:
    entity = _to_user_entity(row)
    return AdminUserRecord(
        id=entity.id,
        username=entity.username,
        email=entity.email,
        status=entity.status,
        failed_login_count=entity.failed_login_count,
        last_login_at=entity.last_login_at,
        roles=entity.roles,
        access_scopes=entity.access_scopes,
        non_approver_enforced=is_non_approver_admin(entity.roles),
    )


class SqlAlchemyIdentityRepository:
    """Async PostgreSQL persistence adapter for accounts, sessions, RBAC, and scopes."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_user_by_username(self, username: str) -> UserAccountEntity | None:
        async with self._session_factory() as session:
            stmt = (
                select(UserAccountModel)
                .options(*_user_eager_options())
                .where(UserAccountModel.username == username)
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            return _to_user_entity(row) if row is not None else None

    async def get_user_by_id(self, user_id: UUID) -> UserAccountEntity | None:
        async with self._session_factory() as session:
            stmt = (
                select(UserAccountModel)
                .options(*_user_eager_options())
                .where(UserAccountModel.id == user_id)
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            return _to_user_entity(row) if row is not None else None

    async def record_failed_login(
        self,
        *,
        user_id: UUID | None,
        attempted_username: str,
        client_ip: str,
        failure_reason: str,
    ) -> None:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                if user_id is not None:
                    await session.execute(
                        update(UserAccountModel)
                        .where(UserAccountModel.id == user_id)
                        .values(
                            failed_login_count=UserAccountModel.failed_login_count + 1,
                            updated_at=now,
                        )
                    )
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=user_id,
                        event_type="AUTH_LOGIN_FAILED",
                        module="identity_access",
                        resource_type="user_accounts",
                        resource_id=str(user_id) if user_id is not None else attempted_username,
                        new_state={
                            "attempted_username": attempted_username,
                            "client_ip": client_ip,
                            "failure_reason": failure_reason,
                        },
                        reason=failure_reason,
                        occurred_at=now,
                    ),
                )

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
    ) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                if previous_token_hash:
                    await session.execute(
                        update(AuthSessionModel)
                        .where(
                            AuthSessionModel.session_token_hash == previous_token_hash,
                            AuthSessionModel.revoked_at.is_(None),
                        )
                        .values(revoked_at=created_at)
                    )
                await session.execute(
                    update(UserAccountModel)
                    .where(UserAccountModel.id == user_id)
                    .values(
                        failed_login_count=0,
                        last_login_at=created_at,
                        updated_at=created_at,
                    )
                )
                session.add(
                    AuthSessionModel(
                        id=session_id,
                        user_id=user_id,
                        session_token_hash=session_token_hash,
                        created_at=created_at,
                        expires_at=expires_at,
                        revoked_at=None,
                        last_seen_at=created_at,
                        security_metadata=security_metadata,
                    )
                )
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=user_id,
                        event_type="AUTH_LOGIN_SUCCESS",
                        module="identity_access",
                        resource_type="auth_sessions",
                        resource_id=str(session_id),
                        new_state={
                            "user_id": str(user_id),
                            "client_ip": security_metadata.get("client_ip"),
                        },
                        occurred_at=created_at,
                    ),
                )

    async def get_session_and_user(
        self, session_token_hash: str
    ) -> tuple[AuthSessionRecord, UserAccountEntity] | None:
        async with self._session_factory() as session:
            sess_row = (
                await session.execute(
                    select(AuthSessionModel).where(
                        AuthSessionModel.session_token_hash == session_token_hash
                    )
                )
            ).scalar_one_or_none()
            if sess_row is None:
                return None

            user_row = (
                await session.execute(
                    select(UserAccountModel)
                    .options(*_user_eager_options())
                    .where(UserAccountModel.id == sess_row.user_id)
                )
            ).scalar_one_or_none()
            if user_row is None:
                return None

            sess_entity = AuthSessionRecord(
                id=sess_row.id,
                user_id=sess_row.user_id,
                session_token_hash=sess_row.session_token_hash,
                created_at=sess_row.created_at,
                expires_at=sess_row.expires_at,
                revoked_at=sess_row.revoked_at,
                last_seen_at=sess_row.last_seen_at,
            )
            return sess_entity, _to_user_entity(user_row)

    async def touch_session(self, session_id: UUID, seen_at: datetime) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                await session.execute(
                    update(AuthSessionModel)
                    .where(AuthSessionModel.id == session_id)
                    .values(last_seen_at=seen_at)
                )

    async def revoke_session(
        self,
        *,
        session_id: UUID,
        actor_id: UUID | None,
        revoked_at: datetime,
        reason: str,
    ) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                await session.execute(
                    update(AuthSessionModel)
                    .where(AuthSessionModel.id == session_id, AuthSessionModel.revoked_at.is_(None))
                    .values(revoked_at=revoked_at)
                )
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="AUTH_LOGOUT",
                        module="identity_access",
                        resource_type="auth_sessions",
                        resource_id=str(session_id),
                        reason=reason,
                        occurred_at=revoked_at,
                    ),
                )

    async def list_users(
        self, *, page: int, page_size: int, query: str | None
    ) -> tuple[list[AdminUserRecord], int]:
        async with self._session_factory() as session:
            filters: list[Any] = []
            if query and query.strip():
                pattern = f"%{query.strip()}%"
                filters.append(
                    or_(
                        UserAccountModel.username.ilike(pattern),
                        UserAccountModel.email.ilike(pattern),
                        UserAccountModel.display_name.ilike(pattern),
                    )
                )

            count_stmt = select(func.count(UserAccountModel.id)).where(*filters)
            total = int((await session.execute(count_stmt)).scalar_one())

            offset = (page - 1) * page_size
            rows_stmt = (
                select(UserAccountModel)
                .options(*_user_eager_options())
                .where(*filters)
                .order_by(UserAccountModel.username.asc())
                .offset(offset)
                .limit(page_size)
            )
            rows = (await session.execute(rows_stmt)).scalars().all()
            return [_to_admin_record(r) for r in rows], total

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
    ) -> AdminUserRecord:
        now = datetime.now(UTC)
        new_user_id = uuid4()
        try:
            async with self._session_factory() as session:
                async with session.begin():
                    role_row = (
                        await session.execute(
                            select(RoleModel).where(RoleModel.code == role_code.value)
                        )
                    ).scalar_one_or_none()
                    if role_row is None:
                        raise AppError(
                            ErrorCode.SYS_INTERNAL_ERROR,
                            "Katalog role kanonis belum tersedia di database.",
                        )

                    user_row = UserAccountModel(
                        id=new_user_id,
                        username=username,
                        email=email,
                        display_name=display_name,
                        password_hash=password_hash,
                        linked_party_id=None,
                        status=AccountStatus.ACTIVE.value,
                        failed_login_count=0,
                        last_login_at=None,
                        created_at=now,
                        updated_at=now,
                    )
                    session.add(user_row)
                    await session.flush()

                    session.add(
                        UserRoleGrantModel(
                            id=uuid4(),
                            user_id=new_user_id,
                            role_id=role_row.id,
                            granted_by=granted_by,
                            granted_at=now,
                            revoked_at=None,
                        )
                    )
                    session.add(
                        UserAccessScopeModel(
                            id=uuid4(),
                            user_id=new_user_id,
                            scope_type=scope_type.value,
                            farmer_id=farmer_id,
                            cooperative_id=cooperative_id,
                            mill_id=mill_id,
                            granted_by=granted_by,
                            created_at=now,
                            revoked_at=None,
                        )
                    )
                    append_audit_event(
                        session,
                        AuditRecordInput(
                            actor_id=granted_by,
                            event_type="ADMIN_USER_CREATED",
                            module="identity_access",
                            resource_type="user_accounts",
                            resource_id=str(new_user_id),
                            new_state={
                                "username": username,
                                "role_code": role_code.value,
                                "scope_type": scope_type.value,
                                "status": AccountStatus.ACTIVE.value,
                            },
                            occurred_at=now,
                        ),
                    )
        except IntegrityError as exc:
            pgcode = getattr(exc.orig, "sqlstate", None)
            if pgcode == "23503":
                raise AppError(
                    ErrorCode.VAL_INVALID_FORMAT,
                    "Referensi target scope (farmer_id/cooperative_id/mill_id) tidak ditemukan.",
                ) from exc
            raise AppError(
                ErrorCode.MD_DUPLICATE_CODE,
                "Username sudah terdaftar dan tidak boleh duplikat.",
            ) from exc

        created = await self._load_admin_record(new_user_id)
        if created is None:
            raise AppError(ErrorCode.SYS_INTERNAL_ERROR)
        return created

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
    ) -> tuple[AdminUserRecord, list[str]]:
        revoked_hashes: list[str] = []
        try:
            async with self._session_factory() as session:
                async with session.begin():
                    user_row = (
                        await session.execute(
                            select(UserAccountModel)
                            .options(*_user_eager_options())
                            .where(UserAccountModel.id == target_user_id)
                        )
                    ).scalar_one_or_none()
                    if user_row is None:
                        raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)

                    prev_entity = _to_admin_record(user_row)
                    previous_state = {
                        "status": prev_entity.status.value,
                        "roles": [r.value for r in prev_entity.roles],
                        "scopes": [
                            {
                                "scope_type": s.scope_type.value,
                                "farmer_id": str(s.farmer_id) if s.farmer_id else None,
                                "cooperative_id": str(s.cooperative_id)
                                if s.cooperative_id
                                else None,
                                "mill_id": str(s.mill_id) if s.mill_id else None,
                            }
                            for s in prev_entity.access_scopes
                        ],
                    }

                    should_revoke_sessions = False
                    if status is not None and status.value != user_row.status:
                        user_row.status = status.value
                        should_revoke_sessions = True
                    if role_code is not None:
                        role_row = (
                            await session.execute(
                                select(RoleModel).where(RoleModel.code == role_code.value)
                            )
                        ).scalar_one_or_none()
                        if role_row is None:
                            raise AppError(ErrorCode.SYS_INTERNAL_ERROR)
                        await session.execute(
                            update(UserRoleGrantModel)
                            .where(
                                UserRoleGrantModel.user_id == target_user_id,
                                UserRoleGrantModel.revoked_at.is_(None),
                            )
                            .values(revoked_at=now)
                        )
                        session.add(
                            UserRoleGrantModel(
                                id=uuid4(),
                                user_id=target_user_id,
                                role_id=role_row.id,
                                granted_by=actor_id,
                                granted_at=now,
                                revoked_at=None,
                            )
                        )
                        should_revoke_sessions = True

                    if scope_type is not None:
                        await session.execute(
                            update(UserAccessScopeModel)
                            .where(
                                UserAccessScopeModel.user_id == target_user_id,
                                UserAccessScopeModel.revoked_at.is_(None),
                            )
                            .values(revoked_at=now)
                        )
                        session.add(
                            UserAccessScopeModel(
                                id=uuid4(),
                                user_id=target_user_id,
                                scope_type=scope_type.value,
                                farmer_id=farmer_id,
                                cooperative_id=cooperative_id,
                                mill_id=mill_id,
                                granted_by=actor_id,
                                created_at=now,
                                revoked_at=None,
                            )
                        )
                        should_revoke_sessions = True

                    user_row.updated_at = now
                    if should_revoke_sessions:
                        rev_rows = await session.execute(
                            update(AuthSessionModel)
                            .where(
                                AuthSessionModel.user_id == target_user_id,
                                AuthSessionModel.revoked_at.is_(None),
                            )
                            .values(revoked_at=now)
                            .returning(AuthSessionModel.session_token_hash)
                        )
                        revoked_hashes = [str(r[0]) for r in rev_rows.all()]

                    append_audit_event(
                        session,
                        AuditRecordInput(
                            actor_id=actor_id,
                            event_type="ADMIN_USER_ACCESS_UPDATED",
                            module="identity_access",
                            resource_type="user_accounts",
                            resource_id=str(target_user_id),
                            previous_state=previous_state,
                            new_state={
                                "status": user_row.status,
                                "role_code": role_code.value if role_code else None,
                                "scope_type": scope_type.value if scope_type else None,
                                "revoked_sessions": len(revoked_hashes),
                            },
                            reason=reason,
                            occurred_at=now,
                        ),
                    )
        except IntegrityError as exc:
            raise AppError(
                ErrorCode.VAL_INVALID_FORMAT,
                "Referensi target scope tidak ditemukan atau konflik integritas akses.",
            ) from exc

        updated = await self._load_admin_record(target_user_id)
        if updated is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        return updated, revoked_hashes

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
    ) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type=event_type,
                        module="identity_access",
                        resource_type=resource_type,
                        resource_id=resource_id,
                        previous_state=previous_state,
                        new_state=new_state,
                        reason=reason,
                    ),
                )

    async def _load_admin_record(self, user_id: UUID) -> AdminUserRecord | None:
        async with self._session_factory() as session:
            stmt = (
                select(UserAccountModel)
                .options(*_user_eager_options())
                .where(UserAccountModel.id == user_id)
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            return _to_admin_record(row) if row is not None else None
