"""Pure domain entities for TBS Receiving, Weighing Revisions, and Grading (DBD §9)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


class ReceiptStatus(StrEnum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    ALLOCATED = "ALLOCATED"
    SHIPPED = "SHIPPED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class GradingDeductionType(StrEnum):
    WEIGHT_PERCENT = "WEIGHT_PERCENT"
    WEIGHT_KG = "WEIGHT_KG"
    VALUE_AMOUNT = "VALUE_AMOUNT"


@dataclass(frozen=True, slots=True)
class ReceiptWeighingRevisionEntity:
    id: UUID
    revision_number: int
    gross_weight_kg: Decimal
    tare_weight_kg: Decimal
    net_weight_kg: Decimal
    weighed_at: datetime
    weighed_by: UUID
    is_current: bool
    correction_reason: str | None


@dataclass(frozen=True, slots=True)
class ReceiptGradingItemEntity:
    id: UUID
    grading_category: str
    measurement_value: Decimal
    deduction_type: GradingDeductionType
    deduction_value: Decimal
    deduction_weight_kg: Decimal | None
    deduction_amount: Decimal | None
    calculation_basis: str
    is_simulation: bool
    notes: str | None


@dataclass(frozen=True, slots=True)
class TbsReceiptEntity:
    id: UUID
    receipt_number: str
    farmer_id: UUID
    farmer_name: str
    farm_id: UUID
    farm_name: str
    cooperative_id: UUID
    harvest_date: date | None
    received_at: datetime
    status: ReceiptStatus
    current_weighing: ReceiptWeighingRevisionEntity | None
    net_weight_after_grading_kg: Decimal | None
    weighing_revisions: tuple[ReceiptWeighingRevisionEntity, ...]
    grading_items: tuple[ReceiptGradingItemEntity, ...]
    version: int
    created_at: datetime
    updated_at: datetime
