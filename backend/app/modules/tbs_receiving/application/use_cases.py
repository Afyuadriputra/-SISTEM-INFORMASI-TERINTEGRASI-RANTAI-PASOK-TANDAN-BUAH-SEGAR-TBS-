"""Use cases orchestrating TBS Receiving, versioned weighing, separate grading, and idempotency."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from app.core.exceptions import AppError, ErrorCode
from app.core.idempotency_primitives import (
    IdempotencySlotPort,
    compute_request_hash,
    validate_idempotency_key,
)
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.domain.rules import (
    allowed_cooperative_ids,
    allowed_farmer_ids,
    assert_cooperative_scope,
    assert_farmer_scope,
    has_global_scope,
)
from app.modules.tbs_receiving.application.ports import TbsReceivingRepositoryPort
from app.modules.tbs_receiving.domain.entities import ReceiptStatus, TbsReceiptEntity
from app.modules.tbs_receiving.domain.rules import GradingInputItem, parse_weighing_pair

GRADING_SIMULATION_NOTICE = (
    "Potongan mutu bersifat SIMULATION_ONLY dan disimpan terpisah dari netto timbangan "
    "(BSD-DEC-006)."
)


def _resolve_read_scope(
    principal: AuthenticatedPrincipal,
) -> tuple[set[UUID] | None, set[UUID] | None]:
    if has_global_scope(principal):
        return None, None
    if RoleCode.FARMER in principal.roles:
        return allowed_farmer_ids(principal), None
    if RoleCode.COOPERATIVE_OPERATOR in principal.roles:
        return None, allowed_cooperative_ids(principal)
    raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)


def _resolve_coop_write_scope(principal: AuthenticatedPrincipal) -> set[UUID] | None:
    if has_global_scope(principal):
        return None
    if RoleCode.COOPERATIVE_OPERATOR in principal.roles:
        coop_ids = allowed_cooperative_ids(principal)
        if not coop_ids:
            raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)
        return coop_ids
    raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)


def _assert_receipt_read_scope(
    principal: AuthenticatedPrincipal, receipt: TbsReceiptEntity
) -> None:
    if has_global_scope(principal):
        return
    if RoleCode.FARMER in principal.roles:
        assert_farmer_scope(principal, receipt.farmer_id)
        return
    if RoleCode.COOPERATIVE_OPERATOR in principal.roles:
        assert_cooperative_scope(principal, receipt.cooperative_id)
        return
    raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)


class TbsReceivingService:
    """Orchestrates SM-02 receipts, revisioned weighing, and simulated grading."""

    def __init__(
        self,
        *,
        repo: TbsReceivingRepositoryPort,
        idempotency: IdempotencySlotPort,
    ) -> None:
        self._repo = repo
        self._idempotency = idempotency

    async def list_receipts(
        self,
        *,
        principal: AuthenticatedPrincipal,
        status: ReceiptStatus | None,
        date_from: date | None,
        date_to: date | None,
        page: int,
        page_size: int,
    ) -> tuple[list[TbsReceiptEntity], int]:
        if date_from is not None and date_to is not None and date_to < date_from:
            raise AppError(ErrorCode.VAL_INVALID_DATE_RANGE)
        farmer_ids, coop_ids = _resolve_read_scope(principal)
        return await self._repo.list_receipts(
            allowed_farmer_ids=farmer_ids,
            allowed_cooperative_ids=coop_ids,
            status_filter=status,
            date_from=date_from,
            date_to=date_to,
            page=page,
            page_size=page_size,
        )

    async def get_receipt_detail(
        self,
        *,
        principal: AuthenticatedPrincipal,
        receipt_id: UUID,
    ) -> TbsReceiptEntity:
        receipt = await self._repo.get_receipt_by_id(receipt_id)
        if receipt is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        _assert_receipt_read_scope(principal, receipt)
        return receipt

    async def create_receipt_draft(
        self,
        *,
        principal: AuthenticatedPrincipal,
        raw_idempotency_key: str | None,
        farmer_id: UUID,
        farm_id: UUID,
        harvest_date: date | None,
        received_at: datetime,
        notes: str | None,
    ) -> tuple[TbsReceiptEntity, bool]:
        idempotency_key = validate_idempotency_key(raw_idempotency_key)
        allowed_coops = _resolve_coop_write_scope(principal)
        normalized_notes = notes.strip() if notes is not None and notes.strip() else None

        request_hash = compute_request_hash(
            {
                "farmer_id": str(farmer_id),
                "farm_id": str(farm_id),
                "harvest_date": harvest_date.isoformat() if harvest_date else None,
                "received_at": received_at.isoformat(),
                "notes": normalized_notes,
            }
        )
        reservation = await self._idempotency.reserve(
            actor_id=principal.user_id,
            operation_key="createReceiptDraft",
            idempotency_key=idempotency_key,
            request_hash=request_hash,
        )
        if reservation.is_replay:
            if reservation.response_reference is None:
                raise AppError(ErrorCode.SYS_DEPENDENCY_UNAVAILABLE)
            existing = await self._repo.get_receipt_by_id(reservation.response_reference)
            if existing is None:
                raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
            _assert_receipt_read_scope(principal, existing)
            return existing, True

        try:
            receipt = await self._repo.create_receipt_draft(
                farmer_id=farmer_id,
                farm_id=farm_id,
                harvest_date=harvest_date,
                received_at=received_at,
                notes=normalized_notes,
                allowed_cooperative_ids=allowed_coops,
                actor_id=principal.user_id,
                idempotency_record_id=reservation.record_id,
            )
        except Exception:
            await self._idempotency.release_on_error(record_id=reservation.record_id)
            raise
        return receipt, False

    async def record_weighing(
        self,
        *,
        principal: AuthenticatedPrincipal,
        receipt_id: UUID,
        gross_weight_kg_raw: str,
        tare_weight_kg_raw: str,
        correction_reason: str | None,
        expected_version: int,
    ) -> TbsReceiptEntity:
        allowed_coops = _resolve_coop_write_scope(principal)
        gross, tare, net = parse_weighing_pair(gross_weight_kg_raw, tare_weight_kg_raw)
        reason_clean = (
            correction_reason.strip()
            if correction_reason is not None and correction_reason.strip()
            else None
        )
        return await self._repo.record_weighing(
            receipt_id=receipt_id,
            expected_version=expected_version,
            gross_weight_kg=gross,
            tare_weight_kg=tare,
            net_weight_kg=net,
            correction_reason=reason_clean,
            allowed_cooperative_ids=allowed_coops,
            actor_id=principal.user_id,
        )

    async def record_grading(
        self,
        *,
        principal: AuthenticatedPrincipal,
        receipt_id: UUID,
        items: list[GradingInputItem],
        expected_version: int,
    ) -> TbsReceiptEntity:
        allowed_coops = _resolve_coop_write_scope(principal)
        if not items:
            raise AppError(
                ErrorCode.TBS_INVALID_GRADING_DEDUCTION,
                details=[
                    {
                        "field": "items",
                        "reason": "Minimal 1 komponen grading wajib diisi.",
                        "code": ErrorCode.TBS_INVALID_GRADING_DEDUCTION.value,
                    }
                ],
            )
        return await self._repo.record_grading(
            receipt_id=receipt_id,
            expected_version=expected_version,
            items=items,
            allowed_cooperative_ids=allowed_coops,
            actor_id=principal.user_id,
        )

    async def validate_receipt(
        self,
        *,
        principal: AuthenticatedPrincipal,
        receipt_id: UUID,
    ) -> TbsReceiptEntity:
        allowed_coops = _resolve_coop_write_scope(principal)
        return await self._repo.validate_receipt(
            receipt_id=receipt_id,
            allowed_cooperative_ids=allowed_coops,
            actor_id=principal.user_id,
        )

    async def cancel_receipt(
        self,
        *,
        principal: AuthenticatedPrincipal,
        receipt_id: UUID,
        reason: str,
        expected_version: int,
    ) -> TbsReceiptEntity:
        allowed_coops = _resolve_coop_write_scope(principal)
        reason_clean = reason.strip()
        if len(reason_clean) < 5:
            raise AppError(
                ErrorCode.VAL_REQUIRED_FIELD,
                details=[
                    {
                        "field": "reason",
                        "reason": "Alasan pembatalan wajib minimal 5 karakter.",
                        "code": ErrorCode.VAL_REQUIRED_FIELD.value,
                    }
                ],
            )
        return await self._repo.cancel_receipt(
            receipt_id=receipt_id,
            expected_version=expected_version,
            reason=reason_clean,
            allowed_cooperative_ids=allowed_coops,
            actor_id=principal.user_id,
        )
