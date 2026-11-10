"""Use cases for System Rule Versions, Redacted Audit Logs & CCTV Observability."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from app.modules.admin.application.ports import AdminRepositoryPort, SystemObservabilityPort
from app.modules.admin.domain.entities import (
    AuditEventEntity,
    SystemObservabilityEntity,
    SystemRuleVersionEntity,
)
from app.modules.admin.domain.rules import validate_audit_date_range, validate_rule_version_input
from app.modules.contracts.domain.entities import PolicyClassification
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal


class AdminGovernanceService:
    """Orchestrates governance rules (BR-SYS-002), redacted audit logs & CCTV telemetry."""

    def __init__(
        self,
        *,
        repo: AdminRepositoryPort,
        observability: SystemObservabilityPort,
    ) -> None:
        self._repo = repo
        self._observability = observability

    async def list_rule_versions(
        self, *, page: int, page_size: int
    ) -> tuple[list[SystemRuleVersionEntity], int]:
        return await self._repo.list_rule_versions(page=page, page_size=page_size)

    async def create_rule_version(
        self,
        *,
        principal: AuthenticatedPrincipal,
        rule_code: str,
        effective_from: datetime,
        effective_until: datetime | None,
        rule_config: dict[str, Any],
        policy_classification: PolicyClassification,
        reason: str | None,
    ) -> SystemRuleVersionEntity:
        cleaned_code, db_status, stored_cfg = validate_rule_version_input(
            principal=principal,
            rule_code=rule_code,
            effective_from=effective_from,
            effective_until=effective_until,
            rule_config=rule_config,
            policy_classification=policy_classification,
        )
        approved_by = principal.user_id if db_status == "APPROVED" else None
        return await self._repo.create_rule_version(
            rule_code=cleaned_code,
            effective_from=effective_from,
            effective_until=effective_until,
            rule_config=stored_cfg,
            db_approval_status=db_status,
            approved_by=approved_by,
            actor_id=principal.user_id,
            reason=reason.strip() if reason else None,
        )

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
        validate_audit_date_range(date_from, date_to)
        return await self._repo.list_audit_events(
            page=page,
            page_size=page_size,
            date_from=date_from,
            date_to=date_to,
            request_id=request_id.strip() if request_id else None,
            module=module.strip() if module else None,
        )

    async def get_system_observability(self) -> SystemObservabilityEntity:
        return await self._observability.collect_summary()
