"""Strict OpenAPI 3.1.0 request/response DTOs for /api/v1/receipts* endpoints."""

from __future__ import annotations

from datetime import date, datetime
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
from app.modules.tbs_receiving.domain.entities import (
    GradingDeductionType,
    ReceiptGradingItemEntity,
    ReceiptStatus,
    ReceiptWeighingRevisionEntity,
    TbsReceiptEntity,
)


class ReceiptWeighingRevisionDto(StrictContractModel):
    id: str
    revision_number: int = Field(ge=1)
    gross_weight_kg: str
    tare_weight_kg: str
    net_weight_kg: str
    weighed_at: str
    weighed_by: str
    is_current: bool
    correction_reason: str | None


class ReceiptGradingItemDto(StrictContractModel):
    id: str
    grading_category: str
    measurement_value: str
    deduction_type: GradingDeductionType
    deduction_value: str
    deduction_weight_kg: str | None
    deduction_amount: str | None
    calculation_basis: str
    is_simulation: bool
    notes: str | None


class TbsReceiptDto(StrictContractModel):
    id: str
    receipt_number: str
    farmer_id: str
    farmer_name: str
    farm_id: str
    farm_name: str
    cooperative_id: str
    harvest_date: str | None
    received_at: str
    status: ReceiptStatus
    current_weighing: ReceiptWeighingRevisionDto | None
    net_weight_after_grading_kg: str | None
    weighing_revisions: list[ReceiptWeighingRevisionDto]
    grading_items: list[ReceiptGradingItemDto]
    version: int = Field(ge=1)
    created_at: str
    updated_at: str


class CreateReceiptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    farmer_id: UUID
    farm_id: UUID
    harvest_date: date | None = None
    received_at: datetime
    notes: str | None = Field(default=None, max_length=1000)


class RecordWeighingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gross_weight_kg: str = Field(min_length=1, max_length=32)
    tare_weight_kg: str = Field(min_length=1, max_length=32)
    correction_reason: str | None = Field(default=None, max_length=500)
    version: int = Field(ge=1)


class RecordGradingItemInputDto(BaseModel):
    model_config = ConfigDict(extra="forbid")

    grading_category: str = Field(min_length=1, max_length=120)
    measurement_value: str = Field(min_length=1, max_length=32)
    deduction_type: GradingDeductionType
    deduction_value: str = Field(min_length=1, max_length=32)
    calculation_basis: str = Field(min_length=1, max_length=60)
    notes: str | None = Field(default=None, max_length=500)


class RecordGradingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[RecordGradingItemInputDto] = Field(min_length=1)
    version: int = Field(ge=1)


class ReasonActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(min_length=5, max_length=500)
    version: int = Field(ge=1)


class ReceiptEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: TbsReceiptDto
    meta: SimpleSuccessMeta
    request_id: str


class ReceiptListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[TbsReceiptDto]
    meta: PaginationMeta
    request_id: str


def weighing_to_dto(entity: ReceiptWeighingRevisionEntity) -> ReceiptWeighingRevisionDto:
    weighed_at_iso = format_utc_iso(entity.weighed_at) or ""
    return ReceiptWeighingRevisionDto(
        id=str(entity.id),
        revision_number=entity.revision_number,
        gross_weight_kg=format_decimal(entity.gross_weight_kg, 3) or "0.000",
        tare_weight_kg=format_decimal(entity.tare_weight_kg, 3) or "0.000",
        net_weight_kg=format_decimal(entity.net_weight_kg, 3) or "0.000",
        weighed_at=weighed_at_iso,
        weighed_by=str(entity.weighed_by),
        is_current=entity.is_current,
        correction_reason=entity.correction_reason,
    )


def grading_to_dto(entity: ReceiptGradingItemEntity) -> ReceiptGradingItemDto:
    return ReceiptGradingItemDto(
        id=str(entity.id),
        grading_category=entity.grading_category,
        measurement_value=format_decimal(entity.measurement_value, 4) or "0.0000",
        deduction_type=entity.deduction_type,
        deduction_value=format_decimal(entity.deduction_value, 4) or "0.0000",
        deduction_weight_kg=format_decimal(entity.deduction_weight_kg, 3),
        deduction_amount=format_decimal(entity.deduction_amount, 2),
        calculation_basis=entity.calculation_basis,
        is_simulation=entity.is_simulation,
        notes=entity.notes,
    )


def receipt_to_dto(entity: TbsReceiptEntity) -> TbsReceiptDto:
    received_at_iso = format_utc_iso(entity.received_at) or ""
    created_at_iso = format_utc_iso(entity.created_at) or ""
    updated_at_iso = format_utc_iso(entity.updated_at) or ""
    return TbsReceiptDto(
        id=str(entity.id),
        receipt_number=entity.receipt_number,
        farmer_id=str(entity.farmer_id),
        farmer_name=entity.farmer_name,
        farm_id=str(entity.farm_id),
        farm_name=entity.farm_name,
        cooperative_id=str(entity.cooperative_id),
        harvest_date=entity.harvest_date.isoformat() if entity.harvest_date is not None else None,
        received_at=received_at_iso,
        status=entity.status,
        current_weighing=(
            weighing_to_dto(entity.current_weighing)
            if entity.current_weighing is not None
            else None
        ),
        net_weight_after_grading_kg=format_decimal(entity.net_weight_after_grading_kg, 3),
        weighing_revisions=[weighing_to_dto(r) for r in entity.weighing_revisions],
        grading_items=[grading_to_dto(g) for g in entity.grading_items],
        version=entity.version,
        created_at=created_at_iso,
        updated_at=updated_at_iso,
    )
