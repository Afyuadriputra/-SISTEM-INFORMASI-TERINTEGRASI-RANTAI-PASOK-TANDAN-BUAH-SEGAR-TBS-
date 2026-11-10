"""PostgreSQL repository implementation for SystemRuleVersions & Redacted Audit Events."""

from __future__ import annotations

import re
from datetime import UTC, date, datetime, time
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.audit import AuditEventModel, AuditRecordInput, append_audit_event
from app.core.logging import redact_mapping, sanitize_text
from app.core.system_rules import SystemRuleVersionModel, deterministic_rule_id
from app.modules.admin.domain.entities import (
    AuditEventEntity,
    SystemRuleVersionEntity,
)
from app.modules.admin.domain.rules import map_db_rule_status

_LONG_DIGITS_RE = re.compile(r"\b\d{10,20}\b")


def _sanitize_audit_reason(raw: str | None) -> str | None:
    if raw is None:
        return None
    cleaned = sanitize_text(raw)
    return _LONG_DIGITS_RE.sub("[REDACTED_NUMBER]", cleaned)


def _normalize_audit_resource_uuid(raw: str) -> UUID:
    try:
        return UUID(raw)
    except ValueError:
        return uuid5(NAMESPACE_URL, f"agroniaga:audit_resource:{raw}")


def _normalize_request_id(raw: str) -> str:
    if raw.startswith("req_") and len(raw) >= 6:
        return raw[:80]
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", raw)[:72]
    return f"req_{cleaned or 'unknown'}"


def _map_rule_entity(row: SystemRuleVersionModel) -> SystemRuleVersionEntity:
    dto_status, policy_cls = map_db_rule_status(
        db_approval_status=row.approval_status,
        rule_config=row.rule_config or {},
    )
    return SystemRuleVersionEntity(
        id=row.id,
        rule_code=row.rule_code,
        version_number=row.version_number,
        effective_from=row.effective_from,
        effective_until=row.effective_until,
        rule_config=dict(row.rule_config or {}),
        approval_status=dto_status,
        policy_classification=policy_cls,
        approved_by=row.approved_by,
        created_at=row.created_at,
    )


def _map_audit_entity(row: AuditEventModel) -> AuditEventEntity:
    return AuditEventEntity(
        id=row.id,
        actor_id=row.actor_id,
        event_type=row.event_type,
        module=row.module,
        resource_type=row.resource_type,
        resource_id=_normalize_audit_resource_uuid(row.resource_id),
        previous_state=redact_mapping(row.previous_state)
        if row.previous_state is not None
        else None,
        new_state=redact_mapping(row.new_state) if row.new_state is not None else None,
        reason=_sanitize_audit_reason(row.reason),
        request_id=_normalize_request_id(row.request_id),
        occurred_at=row.occurred_at,
    )


class SqlAlchemyAdminRepository:
    """PostgreSQL adapter implementing system rules versioning & redacted audit viewer."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def list_rule_versions(
        self, *, page: int, page_size: int
    ) -> tuple[list[SystemRuleVersionEntity], int]:
        async with self._session_factory() as session:
            total = int(
                (
                    await session.execute(select(func.count()).select_from(SystemRuleVersionModel))
                ).scalar_one()
            )
            rows = (
                (
                    await session.execute(
                        select(SystemRuleVersionModel)
                        .order_by(
                            SystemRuleVersionModel.rule_code.asc(),
                            SystemRuleVersionModel.version_number.desc(),
                        )
                        .offset((page - 1) * page_size)
                        .limit(page_size)
                    )
                )
                .scalars()
                .all()
            )
            return [_map_rule_entity(r) for r in rows], total

    async def create_rule_version(
        self,
        *,
        rule_code: str,
        effective_from: datetime,
        effective_until: datetime | None,
        rule_config: dict[str, Any],
        db_approval_status: str,
        approved_by: UUID | None,
        actor_id: UUID,
        reason: str | None,
    ) -> SystemRuleVersionEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                existing_versions = (
                    (
                        await session.execute(
                            select(SystemRuleVersionModel)
                            .where(SystemRuleVersionModel.rule_code == rule_code)
                            .order_by(SystemRuleVersionModel.version_number.desc())
                            .with_for_update()
                        )
                    )
                    .scalars()
                    .all()
                )
                next_ver = (existing_versions[0].version_number + 1) if existing_versions else 1
                new_id = deterministic_rule_id(rule_code, next_ver)
                model = SystemRuleVersionModel(
                    id=new_id,
                    rule_code=rule_code,
                    version_number=next_ver,
                    effective_from=effective_from,
                    effective_until=effective_until,
                    rule_config=rule_config,
                    approval_status=db_approval_status,
                    approved_by=approved_by,
                    created_at=now,
                )
                session.add(model)
                await session.flush()

                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="SYSTEM_RULE_VERSION_CREATED",
                        module="admin",
                        resource_type="system_rule_versions",
                        resource_id=str(model.id),
                        new_state={
                            "rule_code": model.rule_code,
                            "version_number": model.version_number,
                            "approval_status": model.approval_status,
                            "policy_classification": rule_config.get("policy_classification"),
                        },
                        reason=reason,
                    ),
                )
                return _map_rule_entity(model)

    async def list_audit_events(
        self,
        *,
        page: int,
        page_size: int,
        date_from: date | None,
        date_to: date | None,
        request_id: str | None,
        module: str | None,
    ) -> tuple[list[AuditEventEntity], int]:
        filters: list[Any] = []
        if date_from is not None:
            filters.append(
                AuditEventModel.occurred_at >= datetime.combine(date_from, time.min, tzinfo=UTC)
            )
        if date_to is not None:
            filters.append(
                AuditEventModel.occurred_at <= datetime.combine(date_to, time.max, tzinfo=UTC)
            )
        if request_id is not None:
            filters.append(AuditEventModel.request_id == request_id)
        if module is not None:
            filters.append(AuditEventModel.module == module)

        async with self._session_factory() as session:
            total = int(
                (
                    await session.execute(
                        select(func.count()).select_from(AuditEventModel).where(*filters)
                    )
                ).scalar_one()
            )
            rows = (
                (
                    await session.execute(
                        select(AuditEventModel)
                        .where(*filters)
                        .order_by(AuditEventModel.occurred_at.desc())
                        .offset((page - 1) * page_size)
                        .limit(page_size)
                    )
                )
                .scalars()
                .all()
            )
            return [_map_audit_entity(r) for r in rows], total
