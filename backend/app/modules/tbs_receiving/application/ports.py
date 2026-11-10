"""Repository port contract for TBS Receiving, Weighing Revisions, and Grading."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from app.modules.tbs_receiving.domain.entities import (
    ReceiptStatus,
    TbsReceiptEntity,
)
from app.modules.tbs_receiving.domain.rules import GradingInputItem


class TbsReceivingRepositoryPort(Protocol):
    """Storage abstraction for tbs_receipts, weighing revisions, and grading items."""

    async def list_receipts(
        self,
        *,
        allowed_farmer_ids: set[UUID] | None,
        allowed_cooperative_ids: set[UUID] | None,
        status_filter: ReceiptStatus | None,
        date_from: date | None,
        date_to: date | None,
        page: int,
        page_size: int,
    ) -> tuple[list[TbsReceiptEntity], int]: ...

    async def get_receipt_by_id(self, receipt_id: UUID) -> TbsReceiptEntity | None: ...

    async def create_receipt_draft(
        self,
        *,
        farmer_id: UUID,
        farm_id: UUID,
        harvest_date: date | None,
        received_at: datetime,
        notes: str | None,
        allowed_cooperative_ids: set[UUID] | None,
        actor_id: UUID,
        idempotency_record_id: UUID,
    ) -> TbsReceiptEntity: ...

    async def record_weighing(
        self,
        *,
        receipt_id: UUID,
        expected_version: int,
        gross_weight_kg: Decimal,
        tare_weight_kg: Decimal,
        net_weight_kg: Decimal,
        correction_reason: str | None,
        allowed_cooperative_ids: set[UUID] | None,
        actor_id: UUID,
    ) -> TbsReceiptEntity: ...

    async def record_grading(
        self,
        *,
        receipt_id: UUID,
        expected_version: int,
        items: list[GradingInputItem],
        allowed_cooperative_ids: set[UUID] | None,
        actor_id: UUID,
    ) -> TbsReceiptEntity: ...

    async def validate_receipt(
        self,
        *,
        receipt_id: UUID,
        allowed_cooperative_ids: set[UUID] | None,
        actor_id: UUID,
    ) -> TbsReceiptEntity: ...

    async def cancel_receipt(
        self,
        *,
        receipt_id: UUID,
        expected_version: int,
        reason: str,
        allowed_cooperative_ids: set[UUID] | None,
        actor_id: UUID,
    ) -> TbsReceiptEntity: ...
