"""Use cases orchestrating e-DO multi-farmer load, atomic issue, SM-05, & QR verification."""

from __future__ import annotations

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
    allowed_mill_ids,
    assert_cooperative_scope,
    has_global_scope,
)
from app.modules.logistics.application.ports import LogisticsRepositoryPort
from app.modules.logistics.domain.entities import DeliveryOrderEntity, DeliveryOrderStatus

EDO_ISSUANCE_NOTICE = (
    "Hak penerbitan & pembatalan e-DO antar peran berstatus PENDING_SOP (BSD-DEC-009/010)."
)


def _resolve_read_scope(
    principal: AuthenticatedPrincipal,
) -> tuple[set[UUID] | None, set[UUID] | None, set[UUID] | None]:
    if has_global_scope(principal):
        return None, None, None
    if RoleCode.FARMER in principal.roles:
        return allowed_farmer_ids(principal), None, None
    if RoleCode.COOPERATIVE_OPERATOR in principal.roles:
        return None, allowed_cooperative_ids(principal), None
    if RoleCode.MILL_OPERATOR in principal.roles:
        return None, None, allowed_mill_ids(principal)
    raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)


def _resolve_coop_write_scope(principal: AuthenticatedPrincipal) -> set[UUID] | None:
    if has_global_scope(principal):
        return None
    if RoleCode.COOPERATIVE_OPERATOR in principal.roles:
        cids = allowed_cooperative_ids(principal)
        if not cids:
            raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)
        return cids
    raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)


class LogisticsService:
    """Manages consolidated delivery orders, atomic locks, and gate QR arrival verification."""

    def __init__(
        self,
        *,
        repo: LogisticsRepositoryPort,
        idempotency: IdempotencySlotPort,
    ) -> None:
        self._repo = repo
        self._idempotency = idempotency

    async def list_delivery_orders(
        self,
        *,
        principal: AuthenticatedPrincipal,
        status_filter: DeliveryOrderStatus | None,
        mill_id: UUID | None,
        page: int,
        page_size: int,
    ) -> tuple[list[DeliveryOrderEntity], int]:
        f_ids, c_ids, m_ids = _resolve_read_scope(principal)
        return await self._repo.list_delivery_orders(
            allowed_farmer_ids=f_ids,
            allowed_cooperative_ids=c_ids,
            allowed_mill_ids=m_ids,
            status_filter=status_filter,
            mill_id=mill_id,
            page=page,
            page_size=page_size,
        )

    async def get_delivery_order_detail(
        self,
        *,
        principal: AuthenticatedPrincipal,
        delivery_order_id: UUID,
    ) -> DeliveryOrderEntity:
        f_ids, c_ids, m_ids = _resolve_read_scope(principal)
        do = await self._repo.get_delivery_order_by_id(
            delivery_order_id,
            filter_farmer_ids=f_ids,
        )
        if do is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        if c_ids is not None:
            assert_cooperative_scope(principal, do.cooperative_id)
        if m_ids is not None and do.mill_id not in m_ids:
            raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)
        if f_ids is not None and not do.lines:
            raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)
        return do

    async def create_draft(
        self,
        *,
        principal: AuthenticatedPrincipal,
        mill_id: UUID,
        contract_id: UUID,
        vehicle_id: UUID,
        driver_id: UUID,
        receipt_ids: list[UUID],
    ) -> DeliveryOrderEntity:
        if not receipt_ids or len(set(receipt_ids)) != len(receipt_ids):
            raise AppError(
                ErrorCode.VAL_INVALID_FORMAT,
                details=[
                    {
                        "field": "receipt_ids",
                        "reason": "Daftar receipt_ids tidak boleh kosong atau terduplikasi.",
                        "code": ErrorCode.VAL_INVALID_FORMAT.value,
                    }
                ],
            )
        allowed_coops = _resolve_coop_write_scope(principal)
        return await self._repo.create_draft(
            mill_id=mill_id,
            contract_id=contract_id,
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            receipt_ids=receipt_ids,
            allowed_cooperative_ids=allowed_coops,
            actor_id=principal.user_id,
        )

    async def issue_delivery_order(
        self,
        *,
        principal: AuthenticatedPrincipal,
        raw_idempotency_key: str | None,
        delivery_order_id: UUID,
        expected_version: int,
        confirm_lock_allocations: bool,
    ) -> tuple[DeliveryOrderEntity, bool]:
        if not confirm_lock_allocations:
            raise AppError(ErrorCode.VAL_INVALID_FORMAT)
        idempotency_key = validate_idempotency_key(raw_idempotency_key)
        allowed_coops = _resolve_coop_write_scope(principal)

        request_hash = compute_request_hash(
            {
                "delivery_order_id": str(delivery_order_id),
                "version": expected_version,
                "confirm_lock_allocations": confirm_lock_allocations,
            }
        )
        slot = await self._idempotency.reserve(
            actor_id=principal.user_id,
            operation_key="issueDeliveryOrder",
            idempotency_key=idempotency_key,
            request_hash=request_hash,
        )
        if slot.is_replay:
            if slot.response_reference is None:
                raise AppError(ErrorCode.SYS_DEPENDENCY_UNAVAILABLE)
            existing = await self._repo.get_delivery_order_by_id(slot.response_reference)
            if existing is None:
                raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
            if allowed_coops is not None and existing.cooperative_id not in allowed_coops:
                raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)
            return existing, True

        try:
            do = await self._repo.issue_delivery_order(
                delivery_order_id=delivery_order_id,
                expected_version=expected_version,
                allowed_cooperative_ids=allowed_coops,
                actor_id=principal.user_id,
                idempotency_record_id=slot.record_id,
            )
        except Exception:
            await self._idempotency.release_on_error(record_id=slot.record_id)
            raise
        return do, False

    async def transition_status(
        self,
        *,
        principal: AuthenticatedPrincipal,
        delivery_order_id: UUID,
        target_status: DeliveryOrderStatus,
        reason: str | None,
        expected_version: int,
    ) -> DeliveryOrderEntity:
        allowed_coops = _resolve_coop_write_scope(principal)
        global_ops = has_global_scope(principal) and RoleCode.PERUMDA_OPERATIONS in principal.roles
        reason_clean = reason.strip() if reason is not None and reason.strip() else None
        return await self._repo.transition_status(
            delivery_order_id=delivery_order_id,
            target_status=target_status,
            reason=reason_clean,
            expected_version=expected_version,
            allowed_cooperative_ids=allowed_coops,
            has_global_ops=global_ops,
            actor_id=principal.user_id,
        )

    async def cancel_delivery_order(
        self,
        *,
        principal: AuthenticatedPrincipal,
        delivery_order_id: UUID,
        reason: str,
        expected_version: int,
    ) -> DeliveryOrderEntity:
        allowed_coops = _resolve_coop_write_scope(principal)
        global_ops = has_global_scope(principal) and RoleCode.PERUMDA_OPERATIONS in principal.roles
        reason_clean = reason.strip()
        if len(reason_clean) < 5:
            raise AppError(
                ErrorCode.VAL_REQUIRED_FIELD,
                details=[
                    {
                        "field": "reason",
                        "reason": "Alasan pembatalan e-DO wajib minimal 5 karakter.",
                        "code": ErrorCode.VAL_REQUIRED_FIELD.value,
                    }
                ],
            )
        return await self._repo.cancel_delivery_order(
            delivery_order_id=delivery_order_id,
            reason=reason_clean,
            expected_version=expected_version,
            allowed_cooperative_ids=allowed_coops,
            has_global_ops=global_ops,
            actor_id=principal.user_id,
        )

    async def verify_qr_arrival(
        self,
        *,
        principal: AuthenticatedPrincipal,
        qr_token_or_edo_number: str,
        observed_plate_number: str | None,
    ) -> DeliveryOrderEntity:
        token_clean = qr_token_or_edo_number.strip()
        if len(token_clean) < 4:
            raise AppError(ErrorCode.LOG_QR_VERIFICATION_FAILED)
        global_ops = has_global_scope(principal)
        m_ids = None if global_ops else allowed_mill_ids(principal)
        if m_ids is not None and not m_ids:
            raise AppError(ErrorCode.MILL_EDO_MILL_MISMATCH)
        plate_clean = (
            observed_plate_number.strip().upper()
            if observed_plate_number is not None and observed_plate_number.strip()
            else None
        )
        return await self._repo.verify_qr_arrival(
            qr_token_or_edo_number=token_clean,
            observed_plate_number=plate_clean,
            allowed_mill_ids=m_ids,
            has_global_ops=global_ops,
            actor_id=principal.user_id,
        )
