"""Strict OpenAPI 3.1.0 request/response DTOs for /api/v1/mill-tickets* endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.logging import format_utc_iso
from app.core.schemas import (
    PaginationMeta,
    SimpleSuccessMeta,
    StrictContractModel,
    format_decimal,
)
from app.modules.mill_weighing.domain.entities import (
    MillGradingDeductionType,
    MillGradingItemEntity,
    MillTicketStatus,
    MillWeighingTicketEntity,
)


class MillGradingItemDto(StrictContractModel):
    id: str
    grading_category: str
    deduction_type: MillGradingDeductionType
    deduction_value: str
    calculation_basis: str
    is_simulation: bool
    notes: str | None


class MillWeighingTicketDto(StrictContractModel):
    id: str
    delivery_order_id: str
    mill_id: str
    ticket_number: str
    revision_number: int = Field(ge=1)
    previous_ticket_id: str | None
    gross_weight_kg: str
    tare_weight_kg: str
    net_weight_kg: str
    weighed_at: str
    verified_at: str | None
    verified_by: str | None
    is_current: bool
    status: MillTicketStatus
    proof_file_id: str | None
    correction_reason: str | None
    grading_items: list[MillGradingItemDto]
    created_at: str


class CreateMillGradingItemInputDto(BaseModel):
    model_config = ConfigDict(extra="forbid")

    grading_category: str = Field(min_length=1, max_length=120)
    deduction_type: MillGradingDeductionType
    deduction_value: str = Field(min_length=1, max_length=32)
    calculation_basis: str = Field(min_length=1, max_length=60)
    notes: str | None = Field(default=None, max_length=500)


class CreateMillTicketRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    delivery_order_id: UUID
    ticket_number: str = Field(min_length=3, max_length=60)
    gross_weight_kg: str = Field(min_length=1, max_length=32)
    tare_weight_kg: str = Field(min_length=1, max_length=32)
    weighed_at: datetime
    proof_file_id: UUID | None = None
    grading_items: list[CreateMillGradingItemInputDto] = Field(default_factory=list)


class ReviseMillTicketRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gross_weight_kg: str = Field(min_length=1, max_length=32)
    tare_weight_kg: str = Field(min_length=1, max_length=32)
    proof_file_id: UUID | None = None
    correction_reason: str = Field(min_length=5, max_length=500)


class MillTicketListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[MillWeighingTicketDto]
    meta: PaginationMeta
    request_id: str


class MillTicketEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: MillWeighingTicketDto
    meta: SimpleSuccessMeta
    request_id: str


def _grading_to_dto(item: MillGradingItemEntity) -> MillGradingItemDto:
    return MillGradingItemDto(
        id=str(item.id),
        grading_category=item.grading_category,
        deduction_type=item.deduction_type,
        deduction_value=format_decimal(item.deduction_value, 4) or "0.0000",
        calculation_basis=item.calculation_basis,
        is_simulation=item.is_simulation,
        notes=item.notes,
    )


def mill_ticket_to_dto(entity: MillWeighingTicketEntity) -> MillWeighingTicketDto:
    return MillWeighingTicketDto(
        id=str(entity.id),
        delivery_order_id=str(entity.delivery_order_id),
        mill_id=str(entity.mill_id),
        ticket_number=entity.ticket_number,
        revision_number=entity.revision_number,
        previous_ticket_id=(
            str(entity.previous_ticket_id) if entity.previous_ticket_id is not None else None
        ),
        gross_weight_kg=format_decimal(entity.gross_weight_kg, 3) or "0.000",
        tare_weight_kg=format_decimal(entity.tare_weight_kg, 3) or "0.000",
        net_weight_kg=format_decimal(entity.net_weight_kg, 3) or "0.000",
        weighed_at=format_utc_iso(entity.weighed_at) or "",
        verified_at=format_utc_iso(entity.verified_at),
        verified_by=str(entity.verified_by) if entity.verified_by is not None else None,
        is_current=entity.is_current,
        status=entity.status,
        proof_file_id=str(entity.proof_file_id) if entity.proof_file_id is not None else None,
        correction_reason=entity.correction_reason,
        grading_items=[_grading_to_dto(g) for g in entity.grading_items],
        created_at=format_utc_iso(entity.created_at) or "",
    )
