"""Repository and cache ports for scoped operational and executive reports."""

from __future__ import annotations

from datetime import date
from typing import Protocol
from uuid import UUID

from app.modules.identity_access.domain.entities import RoleCode
from app.modules.reporting.domain.entities import (
    FinanceReportEntity,
    OverviewReportEntity,
    ReconciliationReportEntity,
    SupplyReportEntity,
)


class ReportingRepositoryPort(Protocol):
    async def fetch_overview(
        self,
        *,
        role_code: RoleCode,
        period_from: date,
        period_to: date,
        allowed_farmer_ids: set[UUID] | None,
        allowed_cooperative_ids: set[UUID] | None,
        allowed_mill_ids: set[UUID] | None,
    ) -> OverviewReportEntity: ...

    async def fetch_supply(
        self,
        *,
        period_from: date,
        period_to: date,
        allowed_cooperative_ids: set[UUID] | None,
        mill_id: UUID | None,
    ) -> SupplyReportEntity: ...

    async def fetch_reconciliation(
        self,
        *,
        period_from: date,
        period_to: date,
        allowed_cooperative_ids: set[UUID] | None,
    ) -> ReconciliationReportEntity: ...

    async def fetch_finance(
        self,
        *,
        period_from: date,
        period_to: date,
    ) -> FinanceReportEntity: ...


class ReportingCachePort(Protocol):
    async def get_json(self, key: str) -> str | None: ...

    async def set_json(self, key: str, value: str, ttl_seconds: int) -> None: ...
