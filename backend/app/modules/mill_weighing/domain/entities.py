"""Domain entities and enums for mill_weighing_tickets and mill_grading_items (DBD §12)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


class MillTicketStatus(StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    VERIFIED = "VERIFIED"


class MillGradingDeductionType(StrEnum):
    WEIGHT_PERCENT = "WEIGHT_PERCENT"
    WEIGHT_KG = "WEIGHT_KG"
    VALUE_AMOUNT = "VALUE_AMOUNT"


@dataclass(frozen=True, slots=True)
class MillGradingItemEntity:
    id: UUID
    grading_category: str
    deduction_type: MillGradingDeductionType
    deduction_value: Decimal
    calculation_basis: str
    is_simulation: bool
    notes: str | None


@dataclass(frozen=True, slots=True)
class MillWeighingTicketEntity:
    id: UUID
    delivery_order_id: UUID
    mill_id: UUID
    ticket_number: str
    revision_number: int
    previous_ticket_id: UUID | None
    gross_weight_kg: Decimal
    tare_weight_kg: Decimal
    net_weight_kg: Decimal
    weighed_at: datetime
    verified_at: datetime | None
    verified_by: UUID | None
    is_current: bool
    status: MillTicketStatus
    proof_file_id: UUID | None
    correction_reason: str | None
    grading_items: tuple[MillGradingItemEntity, ...]
    created_at: datetime
