"""Pure domain entities for Reporting (/api/v1/reports/*)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from app.modules.contracts.domain.entities import PolicyClassification
from app.modules.identity_access.domain.entities import RoleCode


@dataclass(frozen=True, slots=True)
class OverviewReportEntity:
    role_code: RoleCode
    period_from: date
    period_to: date
    total_receipts_count: int
    total_received_weight_kg: Decimal
    active_deliveries_count: int
    matched_reconciliations_count: int
    dispute_reconciliations_count: int
    farmer_paid_amount: Decimal | None
    farmer_pending_amount: Decimal | None
    is_simulation_data: bool
    data_freshness_at: datetime


@dataclass(frozen=True, slots=True)
class SupplyByMillEntity:
    mill_id: UUID
    mill_name: str
    delivery_count: int
    total_mill_weight_kg: Decimal


@dataclass(frozen=True, slots=True)
class SupplyReportEntity:
    period_from: date
    period_to: date
    total_origin_kg: Decimal
    total_mill_received_kg: Decimal
    excluded_cancelled_count: int
    by_mill: tuple[SupplyByMillEntity, ...]
    data_freshness_at: datetime


@dataclass(frozen=True, slots=True)
class ReconciliationReportEntity:
    period_from: date
    period_to: date
    waiting_ticket_count: int
    ready_count: int
    matched_count: int
    dispute_hold_count: int
    resolved_count: int
    negative_difference_count: int
    active_rule_version_id: UUID
    data_freshness_at: datetime


@dataclass(frozen=True, slots=True)
class FinanceReportEntity:
    period_from: date
    period_to: date
    ar_billed_total: Decimal
    ar_cash_collected_total: Decimal
    ap_approved_unpaid_total: Decimal
    ap_verified_paid_total: Decimal
    farmer_disbursed_verified_total: Decimal
    gross_contribution_simulation: Decimal | None
    margin_label: str
    is_net_profit: bool
    policy_classification: PolicyClassification
    data_freshness_at: datetime
