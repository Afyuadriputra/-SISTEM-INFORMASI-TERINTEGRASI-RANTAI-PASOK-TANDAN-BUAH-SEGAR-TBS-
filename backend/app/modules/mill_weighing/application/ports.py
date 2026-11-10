"""Repository port contract for Mill Weighing Tickets and Grading Items."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from app.modules.mill_weighing.domain.entities import (
    MillTicketStatus,
    MillWeighingTicketEntity,
)
from app.modules.mill_weighing.domain.rules import ValidatedMillGradingItem


class MillWeighingRepositoryPort(Protocol):
    """Storage abstraction for mill_weighing_tickets and cross-module triggers."""

    async def list_tickets(
        self,
        *,
        allowed_mill_ids: set[UUID] | None,
        allowed_cooperative_ids: set[UUID] | None,
        status_filter: MillTicketStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[MillWeighingTicketEntity], int]: ...

    async def get_ticket_by_id(self, ticket_id: UUID) -> MillWeighingTicketEntity | None: ...

    async def get_ticket_coop_id(self, ticket_id: UUID) -> UUID | None: ...

    async def create_ticket(
        self,
        *,
        delivery_order_id: UUID,
        ticket_number: str,
        gross_weight_kg: Decimal,
        tare_weight_kg: Decimal,
        net_weight_kg: Decimal,
        weighed_at: datetime,
        proof_file_id: UUID | None,
        grading_items: list[ValidatedMillGradingItem],
        allowed_mill_ids: set[UUID] | None,
        actor_id: UUID,
        idempotency_record_id: UUID,
    ) -> MillWeighingTicketEntity: ...

    async def revise_ticket(
        self,
        *,
        ticket_id: UUID,
        gross_weight_kg: Decimal,
        tare_weight_kg: Decimal,
        net_weight_kg: Decimal,
        proof_file_id: UUID | None,
        correction_reason: str,
        allowed_mill_ids: set[UUID] | None,
        actor_id: UUID,
    ) -> MillWeighingTicketEntity: ...

    async def verify_ticket(
        self,
        *,
        ticket_id: UUID,
        allowed_mill_ids: set[UUID] | None,
        actor_id: UUID,
    ) -> MillWeighingTicketEntity: ...
