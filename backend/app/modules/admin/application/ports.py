"""Repository & telemetry ports for System Rules, Audit Viewer & Observability."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Protocol
from uuid import UUID

from app.modules.admin.domain.entities import (
    AuditEventEntity,
    SystemObservabilityEntity,
    SystemRuleVersionEntity,
)


class AdminRepositoryPort(Protocol):
    async def list_rule_versions(
        self, *, page: int, page_size: int
    ) -> tuple[list[SystemRuleVersionEntity], int]: ...

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
    ) -> SystemRuleVersionEntity: ...

    async def list_audit_events(
        self,
        *,
        page: int,
        page_size: int,
        date_from: date | None,
        date_to: date | None,
        request_id: str | None,
        module: str | None,
    ) -> tuple[list[AuditEventEntity], int]: ...


class SystemObservabilityPort(Protocol):
    async def collect_summary(self) -> SystemObservabilityEntity: ...
