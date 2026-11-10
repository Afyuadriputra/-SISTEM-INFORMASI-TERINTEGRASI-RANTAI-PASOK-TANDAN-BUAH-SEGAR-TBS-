"""Strict OpenAPI 3.1.0 DTOs for /api/v1/admin/{rule-versions,audit-events,system-health}."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.core.logging import format_utc_iso
from app.core.schemas import (
    HealthDependencies,
    HealthStatus,
    PaginationMeta,
    StrictContractModel,
    format_decimal,
)
from app.modules.admin.domain.entities import (
    AuditEventEntity,
    RuleDtoApprovalStatus,
    SystemObservabilityEntity,
    SystemRuleVersionEntity,
)
from app.modules.contracts.domain.entities import PolicyClassification


class SystemRuleVersionDto(StrictContractModel):
    id: str
    rule_code: str
    version_number: int = Field(ge=1)
    effective_from: str
    effective_until: str | None
    rule_config: dict[str, Any]
    approval_status: RuleDtoApprovalStatus
    policy_classification: PolicyClassification
    approved_by: str | None
    created_at: str


class CreateSystemRuleVersionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_code: str = Field(min_length=1, max_length=80)
    effective_from: datetime
    effective_until: datetime | None = None
    rule_config: dict[str, Any]
    policy_classification: PolicyClassification
    reason: str | None = Field(default=None, max_length=500)


class AuditEventDto(StrictContractModel):
    id: str
    actor_id: str | None
    event_type: str
    module: str
    resource_type: str
    resource_id: str
    previous_state: dict[str, Any] | None
    new_state: dict[str, Any] | None
    reason: str | None
    request_id: str
    occurred_at: str


class ErrorCorrelationDto(StrictContractModel):
    request_id: str
    trace_id: str
    route: str
    status_code: int
    error_code: str
    module: str
    occurred_at: str


class SystemObservabilitySummaryDto(StrictContractModel):
    health: HealthStatus
    redis_cache_hit_ratio_percent: str
    total_requests_24h: int = Field(ge=0)
    server_errors_5xx_24h: int = Field(ge=0)
    recent_error_correlations: list[ErrorCorrelationDto]


class SystemRuleListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[SystemRuleVersionDto]
    meta: PaginationMeta
    request_id: str


class SystemRuleEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: SystemRuleVersionDto
    meta: dict[str, Any] | None = None
    request_id: str


class AuditEventListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[AuditEventDto]
    meta: PaginationMeta
    request_id: str


class SystemObservabilityEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: SystemObservabilitySummaryDto
    meta: dict[str, Any] | None = None
    request_id: str


def rule_to_dto(entity: SystemRuleVersionEntity) -> SystemRuleVersionDto:
    return SystemRuleVersionDto(
        id=str(entity.id),
        rule_code=entity.rule_code,
        version_number=entity.version_number,
        effective_from=format_utc_iso(entity.effective_from) or "",
        effective_until=format_utc_iso(entity.effective_until),
        rule_config=entity.rule_config,
        approval_status=entity.approval_status,
        policy_classification=entity.policy_classification,
        approved_by=str(entity.approved_by) if entity.approved_by else None,
        created_at=format_utc_iso(entity.created_at) or "",
    )


def audit_to_dto(entity: AuditEventEntity) -> AuditEventDto:
    return AuditEventDto(
        id=str(entity.id),
        actor_id=str(entity.actor_id) if entity.actor_id else None,
        event_type=entity.event_type,
        module=entity.module,
        resource_type=entity.resource_type,
        resource_id=str(entity.resource_id),
        previous_state=entity.previous_state,
        new_state=entity.new_state,
        reason=entity.reason,
        request_id=entity.request_id,
        occurred_at=format_utc_iso(entity.occurred_at) or "",
    )


def observability_to_dto(entity: SystemObservabilityEntity) -> SystemObservabilitySummaryDto:
    return SystemObservabilitySummaryDto(
        health=HealthStatus(
            status="ok" if entity.health_status == "ok" else "degraded",
            service=entity.service_name,
            checked_at=format_utc_iso(entity.checked_at) or "",
            dependencies=HealthDependencies(
                postgresql="up" if entity.postgresql_status == "up" else "down",
                redis="up" if entity.redis_status == "up" else "down",
            ),
        ),
        redis_cache_hit_ratio_percent=(
            format_decimal(entity.redis_cache_hit_ratio_percent, 4) or "0.0000"
        ),
        total_requests_24h=entity.total_requests_24h,
        server_errors_5xx_24h=entity.server_errors_5xx_24h,
        recent_error_correlations=[
            ErrorCorrelationDto(
                request_id=item.request_id,
                trace_id=item.trace_id,
                route=item.route,
                status_code=item.status_code,
                error_code=item.error_code,
                module=item.module,
                occurred_at=format_utc_iso(item.occurred_at) or "",
            )
            for item in entity.recent_error_correlations
        ],
    )
