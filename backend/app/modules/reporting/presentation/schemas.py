"""Strict OpenAPI 3.1.0 DTOs for /api/v1/reports/*."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.core.logging import format_utc_iso
from app.core.schemas import SimpleSuccessMeta, StrictContractModel, format_decimal
from app.modules.contracts.domain.entities import PolicyClassification
from app.modules.identity_access.domain.entities import RoleCode
from app.modules.reporting.domain.entities import (
    FinanceReportEntity,
    OverviewReportEntity,
    ReconciliationReportEntity,
    SupplyReportEntity,
)


class OverviewReportDto(StrictContractModel):
    role_code: RoleCode
    period_from: str
    period_to: str
    total_receipts_count: int = Field(ge=0)
    total_received_weight_kg: str
    active_deliveries_count: int = Field(ge=0)
    matched_reconciliations_count: int = Field(ge=0)
    dispute_reconciliations_count: int = Field(ge=0)
    farmer_paid_amount: str | None
    farmer_pending_amount: str | None
    is_simulation_data: bool
    data_freshness_at: str


class SupplyByMillDto(StrictContractModel):
    mill_id: str
    mill_name: str
    delivery_count: int = Field(ge=0)
    total_mill_weight_kg: str


class SupplyReportDto(StrictContractModel):
    period_from: str
    period_to: str
    total_origin_kg: str
    total_mill_received_kg: str
    excluded_cancelled_count: int = Field(ge=0)
    by_mill: list[SupplyByMillDto]
    data_freshness_at: str


class ReconciliationReportDto(StrictContractModel):
    period_from: str
    period_to: str
    waiting_ticket_count: int = Field(ge=0)
    ready_count: int = Field(ge=0)
    matched_count: int = Field(ge=0)
    dispute_hold_count: int = Field(ge=0)
    resolved_count: int = Field(ge=0)
    negative_difference_count: int = Field(ge=0)
    active_rule_version_id: str
    data_freshness_at: str


class FinanceReportDto(StrictContractModel):
    period_from: str
    period_to: str
    ar_billed_total: str
    ar_cash_collected_total: str
    ap_approved_unpaid_total: str
    ap_verified_paid_total: str
    farmer_disbursed_verified_total: str
    gross_contribution_simulation: str | None
    margin_label: str
    is_net_profit: Literal[False] = False
    policy_classification: PolicyClassification
    data_freshness_at: str


class OverviewReportEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: OverviewReportDto
    meta: SimpleSuccessMeta
    request_id: str


class SupplyReportEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: SupplyReportDto
    meta: SimpleSuccessMeta
    request_id: str


class ReconciliationReportEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: ReconciliationReportDto
    meta: SimpleSuccessMeta
    request_id: str


class FinanceReportEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: FinanceReportDto
    meta: SimpleSuccessMeta
    request_id: str


def overview_to_dto(entity: OverviewReportEntity) -> OverviewReportDto:
    return OverviewReportDto(
        role_code=entity.role_code,
        period_from=entity.period_from.isoformat(),
        period_to=entity.period_to.isoformat(),
        total_receipts_count=entity.total_receipts_count,
        total_received_weight_kg=format_decimal(entity.total_received_weight_kg, 3) or "0.000",
        active_deliveries_count=entity.active_deliveries_count,
        matched_reconciliations_count=entity.matched_reconciliations_count,
        dispute_reconciliations_count=entity.dispute_reconciliations_count,
        farmer_paid_amount=format_decimal(entity.farmer_paid_amount, 2),
        farmer_pending_amount=format_decimal(entity.farmer_pending_amount, 2),
        is_simulation_data=entity.is_simulation_data,
        data_freshness_at=format_utc_iso(entity.data_freshness_at) or "",
    )


def supply_to_dto(entity: SupplyReportEntity) -> SupplyReportDto:
    return SupplyReportDto(
        period_from=entity.period_from.isoformat(),
        period_to=entity.period_to.isoformat(),
        total_origin_kg=format_decimal(entity.total_origin_kg, 3) or "0.000",
        total_mill_received_kg=format_decimal(entity.total_mill_received_kg, 3) or "0.000",
        excluded_cancelled_count=entity.excluded_cancelled_count,
        by_mill=[
            SupplyByMillDto(
                mill_id=str(item.mill_id),
                mill_name=item.mill_name,
                delivery_count=item.delivery_count,
                total_mill_weight_kg=format_decimal(item.total_mill_weight_kg, 3) or "0.000",
            )
            for item in entity.by_mill
        ],
        data_freshness_at=format_utc_iso(entity.data_freshness_at) or "",
    )


def reconciliation_report_to_dto(entity: ReconciliationReportEntity) -> ReconciliationReportDto:
    return ReconciliationReportDto(
        period_from=entity.period_from.isoformat(),
        period_to=entity.period_to.isoformat(),
        waiting_ticket_count=entity.waiting_ticket_count,
        ready_count=entity.ready_count,
        matched_count=entity.matched_count,
        dispute_hold_count=entity.dispute_hold_count,
        resolved_count=entity.resolved_count,
        negative_difference_count=entity.negative_difference_count,
        active_rule_version_id=str(entity.active_rule_version_id),
        data_freshness_at=format_utc_iso(entity.data_freshness_at) or "",
    )


def finance_report_to_dto(entity: FinanceReportEntity) -> FinanceReportDto:
    return FinanceReportDto(
        period_from=entity.period_from.isoformat(),
        period_to=entity.period_to.isoformat(),
        ar_billed_total=format_decimal(entity.ar_billed_total, 2) or "0.00",
        ar_cash_collected_total=format_decimal(entity.ar_cash_collected_total, 2) or "0.00",
        ap_approved_unpaid_total=format_decimal(entity.ap_approved_unpaid_total, 2) or "0.00",
        ap_verified_paid_total=format_decimal(entity.ap_verified_paid_total, 2) or "0.00",
        farmer_disbursed_verified_total=(
            format_decimal(entity.farmer_disbursed_verified_total, 2) or "0.00"
        ),
        gross_contribution_simulation=format_decimal(entity.gross_contribution_simulation, 2),
        margin_label=entity.margin_label,
        is_net_profit=False,
        policy_classification=entity.policy_classification,
        data_freshness_at=format_utc_iso(entity.data_freshness_at) or "",
    )
