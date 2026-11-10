"""Use cases orchestrating Trade Contracts SM-03, SOD-02, and atomic Quota Reservations SM-04."""

from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID

from app.core.exceptions import AppError, ErrorCode
from app.core.idempotency_primitives import (
    IdempotencySlotPort,
    compute_request_hash,
    validate_idempotency_key,
)
from app.modules.contracts.application.ports import ContractsRepositoryPort
from app.modules.contracts.domain.entities import (
    BusinessModelCode,
    ContractStatus,
    PerumdaRoleCode,
    PriceRuleType,
    QuotaPeriodEntity,
    QuotaReservationEntity,
    TradeContractEntity,
)
from app.modules.contracts.domain.rules import (
    parse_agreed_price,
    parse_positive_kg,
    validate_contract_party_structure,
)
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal
from app.modules.identity_access.domain.rules import is_non_approver_admin

CONTRACT_POLICY_NOTICE = (
    "Klasifikasi model bisnis dan kuota mengikuti kebijakan rule version kontrak (BSD-DEC-001/008)."
)


class ContractsService:
    """Manages confidential commercial contracts, approvals, and PostgreSQL quota locks."""

    def __init__(
        self,
        *,
        repo: ContractsRepositoryPort,
        idempotency: IdempotencySlotPort,
    ) -> None:
        self._repo = repo
        self._idempotency = idempotency

    async def list_contracts(
        self,
        *,
        status_filter: ContractStatus | None,
        mill_id: UUID | None,
        page: int,
        page_size: int,
    ) -> tuple[list[TradeContractEntity], int]:
        return await self._repo.list_contracts(
            status_filter=status_filter,
            mill_id=mill_id,
            page=page,
            page_size=page_size,
        )

    async def get_contract_detail(self, *, contract_id: UUID) -> TradeContractEntity:
        contract = await self._repo.get_contract_by_id(contract_id)
        if contract is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        return contract

    async def create_contract(
        self,
        *,
        principal: AuthenticatedPrincipal,
        contract_number: str,
        mill_id: UUID,
        start_date: date,
        end_date: date,
        price_rule_type: PriceRuleType,
        agreed_price_per_kg_raw: str | None,
        business_model_code: BusinessModelCode,
        perumda_role: PerumdaRoleCode,
        seller_party_id: UUID,
        buyer_party_id: UUID,
        agent_party_id: UUID | None,
        represented_party_id: UUID | None,
        payment_terms: str,
        initial_quota_kg_raw: str,
    ) -> TradeContractEntity:
        code_clean = contract_number.strip()
        terms_clean = payment_terms.strip()
        if not code_clean or not terms_clean:
            raise AppError(ErrorCode.VAL_REQUIRED_FIELD)
        if end_date < start_date:
            raise AppError(ErrorCode.VAL_INVALID_DATE_RANGE)

        agreed_price = parse_agreed_price(
            price_rule_type=price_rule_type,
            raw_price=agreed_price_per_kg_raw,
        )
        initial_quota = parse_positive_kg(initial_quota_kg_raw, field_name="initial_quota_kg")
        validate_contract_party_structure(
            business_model_code=business_model_code,
            perumda_role=perumda_role,
            seller_party_id=seller_party_id,
            buyer_party_id=buyer_party_id,
            agent_party_id=agent_party_id,
            represented_party_id=represented_party_id,
        )
        return await self._repo.create_contract(
            contract_number=code_clean,
            mill_id=mill_id,
            start_date=start_date,
            end_date=end_date,
            price_rule_type=price_rule_type,
            agreed_price_per_kg=agreed_price,
            business_model_code=business_model_code,
            perumda_role=perumda_role,
            seller_party_id=seller_party_id,
            buyer_party_id=buyer_party_id,
            agent_party_id=agent_party_id,
            represented_party_id=represented_party_id,
            payment_terms=terms_clean,
            initial_quota_kg=initial_quota,
            actor_id=principal.user_id,
        )

    async def approve_contract(
        self,
        *,
        principal: AuthenticatedPrincipal,
        contract_id: UUID,
    ) -> TradeContractEntity:
        return await self._repo.approve_contract(
            contract_id=contract_id,
            actor_id=principal.user_id,
            non_approver_admin=is_non_approver_admin(principal.roles),
        )

    async def get_quota_status(self, *, contract_id: UUID) -> list[QuotaPeriodEntity]:
        return await self._repo.get_quota_periods(contract_id)

    async def reserve_quota(
        self,
        *,
        principal: AuthenticatedPrincipal,
        raw_idempotency_key: str | None,
        contract_id: UUID,
        quota_period_id: UUID,
        delivery_order_id: UUID,
        reserved_weight_kg_raw: str,
    ) -> tuple[QuotaReservationEntity, bool]:
        idempotency_key = validate_idempotency_key(raw_idempotency_key)
        weight_kg = parse_positive_kg(reserved_weight_kg_raw, field_name="reserved_weight_kg")

        request_hash = compute_request_hash(
            {
                "contract_id": str(contract_id),
                "quota_period_id": str(quota_period_id),
                "delivery_order_id": str(delivery_order_id),
                "reserved_weight_kg": f"{weight_kg:.3f}",
            }
        )
        reservation_slot = await self._idempotency.reserve(
            actor_id=principal.user_id,
            operation_key="reserveContractQuota",
            idempotency_key=idempotency_key,
            request_hash=request_hash,
        )
        if reservation_slot.is_replay:
            if reservation_slot.response_reference is None:
                raise AppError(ErrorCode.SYS_DEPENDENCY_UNAVAILABLE)
            existing = await self._repo.get_reservation_by_id(reservation_slot.response_reference)
            if existing is None:
                raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
            return existing, True

        try:
            reservation = await self._repo.reserve_quota(
                contract_id=contract_id,
                quota_period_id=quota_period_id,
                delivery_order_id=delivery_order_id,
                reserved_weight_kg=weight_kg,
                as_of_date=datetime.now(UTC).date(),
                actor_id=principal.user_id,
                idempotency_record_id=reservation_slot.record_id,
            )
        except Exception:
            await self._idempotency.release_on_error(record_id=reservation_slot.record_id)
            raise
        return reservation, False
