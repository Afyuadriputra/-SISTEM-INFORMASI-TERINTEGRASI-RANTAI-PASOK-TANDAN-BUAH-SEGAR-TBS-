"""Repository port contract for Logistics, e-DO lines, status events, and QR arrival check."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.modules.logistics.domain.entities import DeliveryOrderEntity, DeliveryOrderStatus


class LogisticsRepositoryPort(Protocol):
    """Storage abstraction orchestrating delivery_orders, lines, SM-05, and atomic locks."""

    async def list_delivery_orders(
        self,
        *,
        allowed_farmer_ids: set[UUID] | None,
        allowed_cooperative_ids: set[UUID] | None,
        allowed_mill_ids: set[UUID] | None,
        status_filter: DeliveryOrderStatus | None,
        mill_id: UUID | None,
        page: int,
        page_size: int,
    ) -> tuple[list[DeliveryOrderEntity], int]: ...

    async def get_delivery_order_by_id(
        self,
        delivery_order_id: UUID,
        *,
        filter_farmer_ids: set[UUID] | None = None,
    ) -> DeliveryOrderEntity | None: ...

    async def create_draft(
        self,
        *,
        mill_id: UUID,
        contract_id: UUID,
        vehicle_id: UUID,
        driver_id: UUID,
        receipt_ids: list[UUID],
        allowed_cooperative_ids: set[UUID] | None,
        actor_id: UUID,
    ) -> DeliveryOrderEntity: ...

    async def issue_delivery_order(
        self,
        *,
        delivery_order_id: UUID,
        expected_version: int,
        allowed_cooperative_ids: set[UUID] | None,
        actor_id: UUID,
        idempotency_record_id: UUID,
    ) -> DeliveryOrderEntity: ...

    async def transition_status(
        self,
        *,
        delivery_order_id: UUID,
        target_status: DeliveryOrderStatus,
        reason: str | None,
        expected_version: int,
        allowed_cooperative_ids: set[UUID] | None,
        has_global_ops: bool,
        actor_id: UUID,
    ) -> DeliveryOrderEntity: ...

    async def cancel_delivery_order(
        self,
        *,
        delivery_order_id: UUID,
        reason: str,
        expected_version: int,
        allowed_cooperative_ids: set[UUID] | None,
        has_global_ops: bool,
        actor_id: UUID,
    ) -> DeliveryOrderEntity: ...

    async def verify_qr_arrival(
        self,
        *,
        qr_token_or_edo_number: str,
        observed_plate_number: str | None,
        allowed_mill_ids: set[UUID] | None,
        has_global_ops: bool,
        actor_id: UUID,
    ) -> DeliveryOrderEntity: ...
