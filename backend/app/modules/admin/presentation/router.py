"""FastAPI endpoints for System Rule Versions, Redacted Audit Viewer & CCTV Health."""

from __future__ import annotations

from datetime import date
from typing import Annotated, cast

from fastapi import APIRouter, Depends, Query, Request, status

from app.core.logging import request_id_ctx
from app.core.schemas import build_pagination_meta
from app.modules.admin.application.use_cases import AdminGovernanceService
from app.modules.admin.presentation.schemas import (
    AuditEventListEnvelope,
    CreateSystemRuleVersionRequest,
    SystemObservabilityEnvelope,
    SystemRuleEnvelope,
    SystemRuleListEnvelope,
    audit_to_dto,
    observability_to_dto,
    rule_to_dto,
)
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.presentation.dependencies import require_access

admin_governance_router = APIRouter(prefix="/api/v1/admin", tags=["Administration & Audit"])


def get_admin_governance_service(request: Request) -> AdminGovernanceService:
    """Resolve AdminGovernanceService wired in composition root."""
    return cast(AdminGovernanceService, request.app.state.admin_governance_service)


@admin_governance_router.get("/rule-versions", response_model=SystemRuleListEnvelope)
async def list_system_rule_versions(
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.DIRECTOR,
                    RoleCode.SYSTEM_ADMIN,
                ),
                required_permissions=("admin.rules.read",),
            )
        ),
    ],
    service: Annotated[AdminGovernanceService, Depends(get_admin_governance_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> SystemRuleListEnvelope:
    rows, total = await service.list_rule_versions(page=page, page_size=page_size)
    return SystemRuleListEnvelope(
        data=[rule_to_dto(r) for r in rows],
        meta=build_pagination_meta(page, page_size, total),
        request_id=request_id_ctx.get(),
    )


@admin_governance_router.post(
    "/rule-versions",
    response_model=SystemRuleEnvelope,
    status_code=status.HTTP_201_CREATED,
)
async def create_system_rule_version(
    body: CreateSystemRuleVersionRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.DIRECTOR,
                    RoleCode.SYSTEM_ADMIN,
                ),
                required_permissions=("admin.rules.write",),
            )
        ),
    ],
    service: Annotated[AdminGovernanceService, Depends(get_admin_governance_service)],
) -> SystemRuleEnvelope:
    entity = await service.create_rule_version(
        principal=principal,
        rule_code=body.rule_code,
        effective_from=body.effective_from,
        effective_until=body.effective_until,
        rule_config=body.rule_config,
        policy_classification=body.policy_classification,
        reason=body.reason,
    )
    return SystemRuleEnvelope(
        data=rule_to_dto(entity),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@admin_governance_router.get("/audit-events", response_model=AuditEventListEnvelope)
async def list_audit_events(
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.DIRECTOR, RoleCode.SYSTEM_ADMIN),
                required_permissions=("admin.audit.read",),
            )
        ),
    ],
    service: Annotated[AdminGovernanceService, Depends(get_admin_governance_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
    request_id: Annotated[str | None, Query()] = None,
    module: Annotated[str | None, Query()] = None,
) -> AuditEventListEnvelope:
    rows, total = await service.list_audit_events(
        page=page,
        page_size=page_size,
        date_from=date_from,
        date_to=date_to,
        request_id=request_id,
        module=module,
    )
    return AuditEventListEnvelope(
        data=[audit_to_dto(e) for e in rows],
        meta=build_pagination_meta(page, page_size, total),
        request_id=request_id_ctx.get(),
    )


@admin_governance_router.get("/system-health", response_model=SystemObservabilityEnvelope)
async def get_system_observability_summary(
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.SYSTEM_ADMIN,),
                required_permissions=("admin.health.read",),
            )
        ),
    ],
    service: Annotated[AdminGovernanceService, Depends(get_admin_governance_service)],
) -> SystemObservabilityEnvelope:
    summary = await service.get_system_observability()
    return SystemObservabilityEnvelope(
        data=observability_to_dto(summary),
        meta=None,
        request_id=request_id_ctx.get(),
    )
