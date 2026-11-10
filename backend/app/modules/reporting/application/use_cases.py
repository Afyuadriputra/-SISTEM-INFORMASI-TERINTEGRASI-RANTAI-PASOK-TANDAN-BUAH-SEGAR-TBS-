"""Use cases orchestrating scoped reporting queries + Redis cache-aside with PG fallback."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from app.modules.contracts.domain.entities import PolicyClassification
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.domain.rules import (
    allowed_cooperative_ids,
    allowed_farmer_ids,
    allowed_mill_ids,
    has_global_scope,
)
from app.modules.reporting.application.ports import ReportingCachePort, ReportingRepositoryPort
from app.modules.reporting.domain.entities import (
    FinanceReportEntity,
    OverviewReportEntity,
    ReconciliationReportEntity,
    SupplyByMillEntity,
    SupplyReportEntity,
)
from app.modules.reporting.domain.rules import (
    REPORTING_SIMULATION_NOTICE,
    build_report_scope_key,
    resolve_report_date_window,
)

__all__ = ["REPORTING_SIMULATION_NOTICE", "ReportingService"]

_CACHE_TTL_SECONDS = 60

_ROLE_PRECEDENCE = (
    RoleCode.DIRECTOR,
    RoleCode.PERUMDA_FINANCE,
    RoleCode.PERUMDA_OPERATIONS,
    RoleCode.MILL_OPERATOR,
    RoleCode.COOPERATIVE_OPERATOR,
    RoleCode.FARMER,
)


def _primary_role(principal: AuthenticatedPrincipal) -> RoleCode:
    for candidate in _ROLE_PRECEDENCE:
        if candidate in principal.roles:
            return candidate
    return principal.roles[0]


def _resolve_scope(
    principal: AuthenticatedPrincipal,
) -> tuple[RoleCode, set[UUID] | None, set[UUID] | None, set[UUID] | None]:
    role = _primary_role(principal)
    if has_global_scope(principal):
        return role, None, None, None
    if role == RoleCode.FARMER:
        return role, allowed_farmer_ids(principal), None, None
    if role == RoleCode.COOPERATIVE_OPERATOR:
        return role, None, allowed_cooperative_ids(principal), None
    if role == RoleCode.MILL_OPERATOR:
        return role, None, None, allowed_mill_ids(principal)
    return role, set(), set(), set()


class ReportingService:
    """Provides isolated role-aware dashboard aggregations with scoped Redis caching."""

    def __init__(
        self,
        *,
        repo: ReportingRepositoryPort,
        cache: ReportingCachePort,
    ) -> None:
        self._repo = repo
        self._cache = cache

    async def _cache_aside[T](
        self,
        *,
        cache_key: str,
        decode: Callable[[dict], T],
        encode: Callable[[T], dict],
        loader: Callable[[], Awaitable[T]],
    ) -> T:
        raw = await self._cache.get_json(cache_key)
        if raw is not None:
            return decode(json.loads(raw))
        fresh = await loader()
        await self._cache.set_json(cache_key, json.dumps(encode(fresh)), _CACHE_TTL_SECONDS)
        return fresh

    async def get_overview(
        self,
        *,
        principal: AuthenticatedPrincipal,
        date_from: date | None,
        date_to: date | None,
    ) -> OverviewReportEntity:
        start_d, end_d = resolve_report_date_window(date_from, date_to)
        role, f_ids, c_ids, m_ids = _resolve_scope(principal)
        scope_key = build_report_scope_key(
            role_code=role, farmer_ids=f_ids, coop_ids=c_ids, mill_ids=m_ids
        )
        cache_key = f"reports:overview:v1:{scope_key}:{start_d}:{end_d}"

        return await self._cache_aside(
            cache_key=cache_key,
            decode=lambda d: OverviewReportEntity(
                role_code=RoleCode(d["role_code"]),
                period_from=date.fromisoformat(d["period_from"]),
                period_to=date.fromisoformat(d["period_to"]),
                total_receipts_count=int(d["total_receipts_count"]),
                total_received_weight_kg=Decimal(d["total_received_weight_kg"]),
                active_deliveries_count=int(d["active_deliveries_count"]),
                matched_reconciliations_count=int(d["matched_reconciliations_count"]),
                dispute_reconciliations_count=int(d["dispute_reconciliations_count"]),
                farmer_paid_amount=(
                    Decimal(d["farmer_paid_amount"])
                    if d["farmer_paid_amount"] is not None
                    else None
                ),
                farmer_pending_amount=(
                    Decimal(d["farmer_pending_amount"])
                    if d["farmer_pending_amount"] is not None
                    else None
                ),
                is_simulation_data=bool(d["is_simulation_data"]),
                data_freshness_at=datetime.fromisoformat(d["data_freshness_at"]).astimezone(UTC),
            ),
            encode=lambda e: {
                "role_code": e.role_code.value,
                "period_from": e.period_from.isoformat(),
                "period_to": e.period_to.isoformat(),
                "total_receipts_count": e.total_receipts_count,
                "total_received_weight_kg": f"{e.total_received_weight_kg:.3f}",
                "active_deliveries_count": e.active_deliveries_count,
                "matched_reconciliations_count": e.matched_reconciliations_count,
                "dispute_reconciliations_count": e.dispute_reconciliations_count,
                "farmer_paid_amount": (
                    f"{e.farmer_paid_amount:.2f}" if e.farmer_paid_amount is not None else None
                ),
                "farmer_pending_amount": (
                    f"{e.farmer_pending_amount:.2f}"
                    if e.farmer_pending_amount is not None
                    else None
                ),
                "is_simulation_data": e.is_simulation_data,
                "data_freshness_at": e.data_freshness_at.isoformat(),
            },
            loader=lambda: self._repo.fetch_overview(
                role_code=role,
                period_from=start_d,
                period_to=end_d,
                allowed_farmer_ids=f_ids,
                allowed_cooperative_ids=c_ids,
                allowed_mill_ids=m_ids,
            ),
        )

    async def get_supply(
        self,
        *,
        principal: AuthenticatedPrincipal,
        date_from: date | None,
        date_to: date | None,
        mill_id: UUID | None,
    ) -> SupplyReportEntity:
        start_d, end_d = resolve_report_date_window(date_from, date_to)
        role, _, c_ids, _ = _resolve_scope(principal)
        scope_key = build_report_scope_key(
            role_code=role, farmer_ids=None, coop_ids=c_ids, mill_ids=None
        )
        cache_key = f"reports:supply:v1:{scope_key}:{start_d}:{end_d}:{mill_id or 'all'}"

        return await self._cache_aside(
            cache_key=cache_key,
            decode=lambda d: SupplyReportEntity(
                period_from=date.fromisoformat(d["period_from"]),
                period_to=date.fromisoformat(d["period_to"]),
                total_origin_kg=Decimal(d["total_origin_kg"]),
                total_mill_received_kg=Decimal(d["total_mill_received_kg"]),
                excluded_cancelled_count=int(d["excluded_cancelled_count"]),
                by_mill=tuple(
                    SupplyByMillEntity(
                        mill_id=UUID(item["mill_id"]),
                        mill_name=item["mill_name"],
                        delivery_count=int(item["delivery_count"]),
                        total_mill_weight_kg=Decimal(item["total_mill_weight_kg"]),
                    )
                    for item in d["by_mill"]
                ),
                data_freshness_at=datetime.fromisoformat(d["data_freshness_at"]).astimezone(UTC),
            ),
            encode=lambda e: {
                "period_from": e.period_from.isoformat(),
                "period_to": e.period_to.isoformat(),
                "total_origin_kg": f"{e.total_origin_kg:.3f}",
                "total_mill_received_kg": f"{e.total_mill_received_kg:.3f}",
                "excluded_cancelled_count": e.excluded_cancelled_count,
                "by_mill": [
                    {
                        "mill_id": str(item.mill_id),
                        "mill_name": item.mill_name,
                        "delivery_count": item.delivery_count,
                        "total_mill_weight_kg": f"{item.total_mill_weight_kg:.3f}",
                    }
                    for item in e.by_mill
                ],
                "data_freshness_at": e.data_freshness_at.isoformat(),
            },
            loader=lambda: self._repo.fetch_supply(
                period_from=start_d,
                period_to=end_d,
                allowed_cooperative_ids=c_ids,
                mill_id=mill_id,
            ),
        )

    async def get_reconciliation(
        self,
        *,
        principal: AuthenticatedPrincipal,
        date_from: date | None,
        date_to: date | None,
    ) -> ReconciliationReportEntity:
        start_d, end_d = resolve_report_date_window(date_from, date_to)
        role, _, c_ids, _ = _resolve_scope(principal)
        scope_key = build_report_scope_key(
            role_code=role, farmer_ids=None, coop_ids=c_ids, mill_ids=None
        )
        cache_key = f"reports:reconciliation:v1:{scope_key}:{start_d}:{end_d}"

        return await self._cache_aside(
            cache_key=cache_key,
            decode=lambda d: ReconciliationReportEntity(
                period_from=date.fromisoformat(d["period_from"]),
                period_to=date.fromisoformat(d["period_to"]),
                waiting_ticket_count=int(d["waiting_ticket_count"]),
                ready_count=int(d["ready_count"]),
                matched_count=int(d["matched_count"]),
                dispute_hold_count=int(d["dispute_hold_count"]),
                resolved_count=int(d["resolved_count"]),
                negative_difference_count=int(d["negative_difference_count"]),
                active_rule_version_id=UUID(d["active_rule_version_id"]),
                data_freshness_at=datetime.fromisoformat(d["data_freshness_at"]).astimezone(UTC),
            ),
            encode=lambda e: {
                "period_from": e.period_from.isoformat(),
                "period_to": e.period_to.isoformat(),
                "waiting_ticket_count": e.waiting_ticket_count,
                "ready_count": e.ready_count,
                "matched_count": e.matched_count,
                "dispute_hold_count": e.dispute_hold_count,
                "resolved_count": e.resolved_count,
                "negative_difference_count": e.negative_difference_count,
                "active_rule_version_id": str(e.active_rule_version_id),
                "data_freshness_at": e.data_freshness_at.isoformat(),
            },
            loader=lambda: self._repo.fetch_reconciliation(
                period_from=start_d,
                period_to=end_d,
                allowed_cooperative_ids=c_ids,
            ),
        )

    async def get_finance(
        self,
        *,
        date_from: date | None,
        date_to: date | None,
    ) -> FinanceReportEntity:
        start_d, end_d = resolve_report_date_window(date_from, date_to)
        cache_key = f"reports:finance:v1:global:{start_d}:{end_d}"

        return await self._cache_aside(
            cache_key=cache_key,
            decode=lambda d: FinanceReportEntity(
                period_from=date.fromisoformat(d["period_from"]),
                period_to=date.fromisoformat(d["period_to"]),
                ar_billed_total=Decimal(d["ar_billed_total"]),
                ar_cash_collected_total=Decimal(d["ar_cash_collected_total"]),
                ap_approved_unpaid_total=Decimal(d["ap_approved_unpaid_total"]),
                ap_verified_paid_total=Decimal(d["ap_verified_paid_total"]),
                farmer_disbursed_verified_total=Decimal(d["farmer_disbursed_verified_total"]),
                gross_contribution_simulation=(
                    Decimal(d["gross_contribution_simulation"])
                    if d["gross_contribution_simulation"] is not None
                    else None
                ),
                margin_label=str(d["margin_label"]),
                is_net_profit=bool(d["is_net_profit"]),
                policy_classification=PolicyClassification(d["policy_classification"]),
                data_freshness_at=datetime.fromisoformat(d["data_freshness_at"]).astimezone(UTC),
            ),
            encode=lambda e: {
                "period_from": e.period_from.isoformat(),
                "period_to": e.period_to.isoformat(),
                "ar_billed_total": f"{e.ar_billed_total:.2f}",
                "ar_cash_collected_total": f"{e.ar_cash_collected_total:.2f}",
                "ap_approved_unpaid_total": f"{e.ap_approved_unpaid_total:.2f}",
                "ap_verified_paid_total": f"{e.ap_verified_paid_total:.2f}",
                "farmer_disbursed_verified_total": f"{e.farmer_disbursed_verified_total:.2f}",
                "gross_contribution_simulation": (
                    f"{e.gross_contribution_simulation:.2f}"
                    if e.gross_contribution_simulation is not None
                    else None
                ),
                "margin_label": e.margin_label,
                "is_net_profit": e.is_net_profit,
                "policy_classification": e.policy_classification.value,
                "data_freshness_at": e.data_freshness_at.isoformat(),
            },
            loader=lambda: self._repo.fetch_finance(period_from=start_d, period_to=end_d),
        )
