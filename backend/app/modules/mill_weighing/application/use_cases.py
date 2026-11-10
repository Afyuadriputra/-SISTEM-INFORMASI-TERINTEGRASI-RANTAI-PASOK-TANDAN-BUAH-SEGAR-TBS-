"""Use cases orchestrating Mill Weighing Tickets SM-06, revisions, & verification."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.core.exceptions import AppError, ErrorCode
from app.core.idempotency_primitives import (
    IdempotencySlotPort,
    compute_request_hash,
    validate_idempotency_key,
)
from app.core.weight_primitives import parse_weighing_pair
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.domain.rules import (
    allowed_cooperative_ids,
    allowed_mill_ids,
    has_global_scope,
)
from app.modules.mill_weighing.application.ports import MillWeighingRepositoryPort
from app.modules.mill_weighing.domain.entities import (
    MillTicketStatus,
    MillWeighingTicketEntity,
)
from app.modules.mill_weighing.domain.rules import (
    MillGradingInput,
    validate_mill_grading_items,
)


def _resolve_read_scope(
    principal: AuthenticatedPrincipal,
) -> tuple[set[UUID] | None, set[UUID] | None]:
    if has_global_scope(principal):
        return None, None
    if RoleCode.MILL_OPERATOR in principal.roles:
        return allowed_mill_ids(principal), None
    if RoleCode.COOPERATIVE_OPERATOR in principal.roles:
        return None, allowed_cooperative_ids(principal)
    raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)


def _resolve_mill_write_scope(principal: AuthenticatedPrincipal) -> set[UUID] | None:
    if has_global_scope(principal):
        return None
    if RoleCode.MILL_OPERATOR in principal.roles:
        m_ids = allowed_mill_ids(principal)
        if not m_ids:
            raise AppError(ErrorCode.MILL_EDO_MILL_MISMATCH)
        return m_ids
    raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)


class MillWeighingService:
    """Handles unique mill weighing tickets, immutable revision chains, and arrival receipt."""

    def __init__(
        self,
        *,
        repo: MillWeighingRepositoryPort,
        idempotency: IdempotencySlotPort,
    ) -> None:
        self._repo = repo
        self._idempotency = idempotency

    async def list_tickets(
        self,
        *,
        principal: AuthenticatedPrincipal,
        status_filter: MillTicketStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[MillWeighingTicketEntity], int]:
        m_ids, c_ids = _resolve_read_scope(principal)
        return await self._repo.list_tickets(
            allowed_mill_ids=m_ids,
            allowed_cooperative_ids=c_ids,
            status_filter=status_filter,
            page=page,
            page_size=page_size,
        )

    async def get_ticket_detail(
        self, *, principal: AuthenticatedPrincipal, ticket_id: UUID
    ) -> MillWeighingTicketEntity:
        ticket = await self._repo.get_ticket_by_id(ticket_id)
        if ticket is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        m_ids, c_ids = _resolve_read_scope(principal)
        if m_ids is not None and ticket.mill_id not in m_ids:
            raise AppError(ErrorCode.MILL_EDO_MILL_MISMATCH)
        if c_ids is not None:
            coop_id = await self._repo.get_ticket_coop_id(ticket_id)
            if coop_id is None or coop_id not in c_ids:
                raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)
        return ticket

    async def create_ticket(
        self,
        *,
        principal: AuthenticatedPrincipal,
        raw_idempotency_key: str | None,
        delivery_order_id: UUID,
        ticket_number: str,
        gross_weight_kg_raw: str,
        tare_weight_kg_raw: str,
        weighed_at: datetime,
        proof_file_id: UUID | None,
        grading_items: list[MillGradingInput],
    ) -> tuple[MillWeighingTicketEntity, bool]:
        idempotency_key = validate_idempotency_key(raw_idempotency_key)
        allowed_mills = _resolve_mill_write_scope(principal)

        ticket_num_clean = ticket_number.strip()
        if len(ticket_num_clean) < 3:
            raise AppError(ErrorCode.VAL_REQUIRED_FIELD)

        gross, tare, net = parse_weighing_pair(gross_weight_kg_raw, tare_weight_kg_raw)
        validated_grading = validate_mill_grading_items(grading_items)

        request_hash = compute_request_hash(
            {
                "delivery_order_id": str(delivery_order_id),
                "ticket_number": ticket_num_clean,
                "gross_weight_kg": f"{gross:.3f}",
                "tare_weight_kg": f"{tare:.3f}",
                "weighed_at": weighed_at.isoformat(),
                "proof_file_id": str(proof_file_id) if proof_file_id else None,
                "grading_count": len(validated_grading),
            }
        )
        slot = await self._idempotency.reserve(
            actor_id=principal.user_id,
            operation_key="createMillTicket",
            idempotency_key=idempotency_key,
            request_hash=request_hash,
        )
        if slot.is_replay:
            if slot.response_reference is None:
                raise AppError(ErrorCode.SYS_DEPENDENCY_UNAVAILABLE)
            existing = await self._repo.get_ticket_by_id(slot.response_reference)
            if existing is None:
                raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
            if allowed_mills is not None and existing.mill_id not in allowed_mills:
                raise AppError(ErrorCode.MILL_EDO_MILL_MISMATCH)
            return existing, True

        try:
            ticket = await self._repo.create_ticket(
                delivery_order_id=delivery_order_id,
                ticket_number=ticket_num_clean,
                gross_weight_kg=gross,
                tare_weight_kg=tare,
                net_weight_kg=net,
                weighed_at=weighed_at,
                proof_file_id=proof_file_id,
                grading_items=validated_grading,
                allowed_mill_ids=allowed_mills,
                actor_id=principal.user_id,
                idempotency_record_id=slot.record_id,
            )
        except Exception:
            await self._idempotency.release_on_error(record_id=slot.record_id)
            raise
        return ticket, False

    async def revise_ticket(
        self,
        *,
        principal: AuthenticatedPrincipal,
        ticket_id: UUID,
        gross_weight_kg_raw: str,
        tare_weight_kg_raw: str,
        proof_file_id: UUID | None,
        correction_reason: str,
    ) -> MillWeighingTicketEntity:
        allowed_mills = _resolve_mill_write_scope(principal)
        reason_clean = correction_reason.strip()
        if len(reason_clean) < 5:
            raise AppError(
                ErrorCode.VAL_REQUIRED_FIELD,
                details=[
                    {
                        "field": "correction_reason",
                        "reason": "Alasan revisi tiket timbang wajib minimal 5 karakter.",
                        "code": ErrorCode.VAL_REQUIRED_FIELD.value,
                    }
                ],
            )
        gross, tare, net = parse_weighing_pair(gross_weight_kg_raw, tare_weight_kg_raw)
        return await self._repo.revise_ticket(
            ticket_id=ticket_id,
            gross_weight_kg=gross,
            tare_weight_kg=tare,
            net_weight_kg=net,
            proof_file_id=proof_file_id,
            correction_reason=reason_clean,
            allowed_mill_ids=allowed_mills,
            actor_id=principal.user_id,
        )

    async def verify_ticket(
        self,
        *,
        principal: AuthenticatedPrincipal,
        ticket_id: UUID,
    ) -> MillWeighingTicketEntity:
        allowed_mills = _resolve_mill_write_scope(principal)
        return await self._repo.verify_ticket(
            ticket_id=ticket_id,
            allowed_mill_ids=allowed_mills,
            actor_id=principal.user_id,
        )
