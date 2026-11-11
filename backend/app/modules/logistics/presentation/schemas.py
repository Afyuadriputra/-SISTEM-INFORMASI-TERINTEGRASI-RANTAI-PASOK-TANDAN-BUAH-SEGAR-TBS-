"""Strict OpenAPI 3.1.0 request/response DTOs for /api/v1/delivery-orders* endpoints."""

from __future__ import annotations

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
from app.modules.logistics.domain.entities import (
    AllocationStatus,
    DeliveryOrderEntity,
    DeliveryOrderLineEntity,
    DeliveryOrderStatus,
    DeliveryStatusEventEntity,
)


class DeliveryOrderLineDto(StrictContractModel):
    id: str
    receipt_id: str
    receipt_number: str
    farmer_id: str
    farmer_name: str
    origin_weight_snapshot_kg: str
    allocation_status: AllocationStatus


class DeliveryStatusEventDto(StrictContractModel):
    id: str
    previous_status: DeliveryOrderStatus | None
    new_status: DeliveryOrderStatus
    actor_id: str
    event_time: str
    reason: str | None


class DeliveryOrderDto(StrictContractModel):
    id: str
    delivery_order_number: str
    cooperative_id: str
    mill_id: str
    mill_name: str
    contract_id: str
    vehicle_id: str
    vehicle_plate: str
    driver_id: str
    driver_name: str
    total_origin_weight_kg: str
    status: DeliveryOrderStatus
    gps_tracking_supported: Literal[False] = False
    qr_verification_token: str | None
    lines: list[DeliveryOrderLineDto]
    status_events: list[DeliveryStatusEventDto]
    issued_at: str | None
    departed_at: str | None
    arrived_at: str | None
    completed_at: str | None
    version: int = Field(ge=1)
    created_at: str


class CreateDeliveryOrderDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mill_id: UUID
    contract_id: UUID
    vehicle_id: UUID
    driver_id: UUID
    receipt_ids: list[UUID] = Field(min_length=1)


class IssueDeliveryOrderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=1)
    confirm_lock_allocations: Literal[True]


class TransitionDeliveryStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_status: DeliveryOrderStatus
    reason: str | None = Field(default=None, max_length=500)
    version: int = Field(ge=1)


class CancelDeliveryOrderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(min_length=5, max_length=500)
    version: int = Field(ge=1)


class VerifyDeliveryQrRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    qr_token_or_edo_number: str = Field(min_length=4, max_length=160)
    observed_plate_number: str | None = Field(default=None, max_length=40)


class DeliveryOrderListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[DeliveryOrderDto]
    meta: PaginationMeta
    request_id: str


class DeliveryOrderEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: DeliveryOrderDto
    meta: SimpleSuccessMeta
    request_id: str


def _line_to_dto(ln: DeliveryOrderLineEntity) -> DeliveryOrderLineDto:
    return DeliveryOrderLineDto(
        id=str(ln.id),
        receipt_id=str(ln.receipt_id),
        receipt_number=ln.receipt_number,
        farmer_id=str(ln.farmer_id),
        farmer_name=ln.farmer_name,
        origin_weight_snapshot_kg=format_decimal(ln.origin_weight_snapshot_kg, 3) or "0.000",
        allocation_status=ln.allocation_status,
    )


def _event_to_dto(ev: DeliveryStatusEventEntity) -> DeliveryStatusEventDto:
    return DeliveryStatusEventDto(
        id=str(ev.id),
        previous_status=ev.previous_status,
        new_status=ev.new_status,
        actor_id=str(ev.actor_id),
        event_time=format_utc_iso(ev.event_time) or "",
        reason=ev.reason,
    )


def delivery_order_to_dto(entity: DeliveryOrderEntity) -> DeliveryOrderDto:
    return DeliveryOrderDto(
        id=str(entity.id),
        delivery_order_number=entity.delivery_order_number,
        cooperative_id=str(entity.cooperative_id),
        mill_id=str(entity.mill_id),
        mill_name=entity.mill_name,
        contract_id=str(entity.contract_id),
        vehicle_id=str(entity.vehicle_id),
        vehicle_plate=entity.vehicle_plate,
        driver_id=str(entity.driver_id),
        driver_name=entity.driver_name,
        total_origin_weight_kg=format_decimal(entity.total_origin_weight_kg, 3) or "0.000",
        status=entity.status,
        gps_tracking_supported=False,
        qr_verification_token=entity.qr_verification_token,
        lines=[_line_to_dto(ln) for ln in entity.lines],
        status_events=[_event_to_dto(ev) for ev in entity.status_events],
        issued_at=format_utc_iso(entity.issued_at),
        departed_at=format_utc_iso(entity.departed_at),
        arrived_at=format_utc_iso(entity.arrived_at),
        completed_at=format_utc_iso(entity.completed_at),
        version=entity.version,
        created_at=format_utc_iso(entity.created_at) or "",
    )
