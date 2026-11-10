"""FastAPI endpoints for Scoped Dashboard Reporting (/api/v1/reports/*)."""

from __future__ import annotations

from datetime import date
from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.core.logging import format_utc_iso, request_id_ctx
from app.core.schemas import SimpleSuccessMeta
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.presentation.dependencies import require_access
from app.modules.reporting.application.use_cases import (
    REPORTING_SIMULATION_NOTICE,
    ReportingService,
)
from app.modules.reporting.presentation.schemas import (
    FinanceReportEnvelope,
    OverviewReportEnvelope,
    ReconciliationReportEnvelope,
    SupplyReportEnvelope,
    finance_report_to_dto,
    overview_to_dto,
    reconciliation_report_to_dto,
    supply_to_dto,
)

reporting_router = APIRouter(prefix="/api/v1/reports", tags=["Reporting"])


def get_reporting_service(request: Request) -> ReportingService:
    """Resolve ReportingService wired in composition root."""
    return cast(ReportingService, request.app.state.reporting_service)


@reporting_router.get("/overview", response_model=OverviewReportEnvelope)
async def get_overview_report(
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.FARMER,
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.MILL_OPERATOR,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("reports.operational.read",),
            )
        ),
    ],
    service: Annotated[ReportingService, Depends(get_reporting_service)],
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
) -> OverviewReportEnvelope:
    entity = await service.get_overview(principal=principal, date_from=date_from, date_to=date_to)
    return OverviewReportEnvelope(
        data=overview_to_dto(entity),
        meta=SimpleSuccessMeta(
            data_freshness_at=format_utc_iso(entity.data_freshness_at),
            simulation_notice=REPORTING_SIMULATION_NOTICE if entity.is_simulation_data else None,
        ),
        request_id=request_id_ctx.get(),
    )


@reporting_router.get("/supply", response_model=SupplyReportEnvelope)
async def get_supply_report(
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("reports.operational.read",),
            )
        ),
    ],
    service: Annotated[ReportingService, Depends(get_reporting_service)],
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
    mill_id: Annotated[UUID | None, Query()] = None,
) -> SupplyReportEnvelope:
    entity = await service.get_supply(
        principal=principal, date_from=date_from, date_to=date_to, mill_id=mill_id
    )
    return SupplyReportEnvelope(
        data=supply_to_dto(entity),
        meta=SimpleSuccessMeta(
            data_freshness_at=format_utc_iso(entity.data_freshness_at),
            simulation_notice=REPORTING_SIMULATION_NOTICE,
        ),
        request_id=request_id_ctx.get(),
    )


@reporting_router.get("/reconciliation", response_model=ReconciliationReportEnvelope)
async def get_reconciliation_report(
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("reports.operational.read",),
            )
        ),
    ],
    service: Annotated[ReportingService, Depends(get_reporting_service)],
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
) -> ReconciliationReportEnvelope:
    entity = await service.get_reconciliation(
        principal=principal, date_from=date_from, date_to=date_to
    )
    return ReconciliationReportEnvelope(
        data=reconciliation_report_to_dto(entity),
        meta=SimpleSuccessMeta(
            data_freshness_at=format_utc_iso(entity.data_freshness_at),
            simulation_notice=REPORTING_SIMULATION_NOTICE,
        ),
        request_id=request_id_ctx.get(),
    )


@reporting_router.get("/finance", response_model=FinanceReportEnvelope)
async def get_finance_report(
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_FINANCE, RoleCode.DIRECTOR),
                required_permissions=("reports.finance.read",),
            )
        ),
    ],
    service: Annotated[ReportingService, Depends(get_reporting_service)],
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
) -> FinanceReportEnvelope:
    entity = await service.get_finance(date_from=date_from, date_to=date_to)
    return FinanceReportEnvelope(
        data=finance_report_to_dto(entity),
        meta=SimpleSuccessMeta(
            data_freshness_at=format_utc_iso(entity.data_freshness_at),
            simulation_notice=REPORTING_SIMULATION_NOTICE,
        ),
        request_id=request_id_ctx.get(),
    )
