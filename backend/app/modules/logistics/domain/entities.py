"""Domain entities and status enums for Logistics & e-DO (DBD §11)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


class DeliveryOrderStatus(StrEnum):
    DRAFT = "DRAFT"
    READY = "READY"
    IN_TRANSIT = "IN_TRANSIT"
    ARRIVED = "ARRIVED"
    RECEIVED = "RECEIVED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class AllocationStatus(StrEnum):
    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"


@dataclass(frozen=True, slots=True)
class DeliveryOrderLineEntity:
    id: UUID
    receipt_id: UUID
    receipt_number: str
    farmer_id: UUID
    farmer_name: str
    origin_weight_snapshot_kg: Decimal
    allocation_status: AllocationStatus


@dataclass(frozen=True, slots=True)
class DeliveryStatusEventEntity:
    id: UUID
    previous_status: DeliveryOrderStatus | None
    new_status: DeliveryOrderStatus
    actor_id: UUID
    event_time: datetime
    reason: str | None


@dataclass(frozen=True, slots=True)
class DeliveryOrderEntity:
    id: UUID
    delivery_order_number: str
    cooperative_id: UUID
    mill_id: UUID
    mill_name: str
    contract_id: UUID
    vehicle_id: UUID
    vehicle_plate: str
    driver_id: UUID
    driver_name: str
    total_origin_weight_kg: Decimal
    status: DeliveryOrderStatus
    qr_verification_token: str | None
    lines: tuple[DeliveryOrderLineEntity, ...]
    status_events: tuple[DeliveryStatusEventEntity, ...]
    issued_at: datetime | None
    departed_at: datetime | None
    arrived_at: datetime | None
    completed_at: datetime | None
    version: int
    created_at: datetime
