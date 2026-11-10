"""Pure domain entities for System Rules, Audit Logs & System Health."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID

from app.modules.contracts.domain.entities import PolicyClassification


class RuleDtoApprovalStatus(StrEnum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    RETIRED = "RETIRED"


@dataclass(frozen=True, slots=True)
class SystemRuleVersionEntity:
    id: UUID
    rule_code: str
    version_number: int
    effective_from: datetime
    effective_until: datetime | None
    rule_config: dict[str, Any]
    approval_status: RuleDtoApprovalStatus
    policy_classification: PolicyClassification
    approved_by: UUID | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class AuditEventEntity:
    id: UUID
    actor_id: UUID | None
    event_type: str
    module: str
    resource_type: str
    resource_id: UUID
    previous_state: dict[str, Any] | None
    new_state: dict[str, Any] | None
    reason: str | None
    request_id: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class ObservabilityErrorItemEntity:
    request_id: str
    trace_id: str
    route: str
    status_code: int
    error_code: str
    module: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class SystemObservabilityEntity:
    health_status: str
    service_name: str
    checked_at: datetime
    postgresql_status: str
    redis_status: str
    redis_cache_hit_ratio_percent: Decimal
    total_requests_24h: int
    server_errors_5xx_24h: int
    recent_error_correlations: tuple[ObservabilityErrorItemEntity, ...]
