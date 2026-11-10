"""Repository port contract for Trade Contracts, Quota Periods, and Reservations."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from app.modules.contracts.domain.entities import (
    BusinessModelCode,
    ContractStatus,
    PerumdaRoleCode,
    PriceRuleType,
    QuotaPeriodEntity,
    QuotaReservationEntity,
    TradeContractEntity,
)


class ContractsRepositoryPort(Protocol):
    """Storage abstraction backed by PostgreSQL with SQL row locking."""

    async def list_contracts(
        self,
        *,
        status_filter: ContractStatus | None,
        mill_id: UUID | None,
        page: int,
        page_size: int,
    ) -> tuple[list[TradeContractEntity], int]: ...

    async def get_contract_by_id(self, contract_id: UUID) -> TradeContractEntity | None: ...

    async def create_contract(
        self,
        *,
        contract_number: str,
        mill_id: UUID,
        start_date: date,
        end_date: date,
        price_rule_type: PriceRuleType,
        agreed_price_per_kg: Decimal | None,
        business_model_code: BusinessModelCode,
        perumda_role: PerumdaRoleCode,
        seller_party_id: UUID,
        buyer_party_id: UUID,
        agent_party_id: UUID | None,
        represented_party_id: UUID | None,
        payment_terms: str,
        initial_quota_kg: Decimal,
        actor_id: UUID,
    ) -> TradeContractEntity: ...

    async def approve_contract(
        self,
        *,
        contract_id: UUID,
        actor_id: UUID,
        non_approver_admin: bool,
    ) -> TradeContractEntity: ...

    async def get_quota_periods(self, contract_id: UUID) -> list[QuotaPeriodEntity]: ...

    async def get_reservation_by_id(
        self, reservation_id: UUID
    ) -> QuotaReservationEntity | None: ...

    async def reserve_quota(
        self,
        *,
        contract_id: UUID,
        quota_period_id: UUID,
        delivery_order_id: UUID,
        reserved_weight_kg: Decimal,
        as_of_date: date,
        actor_id: UUID,
        idempotency_record_id: UUID,
    ) -> QuotaReservationEntity: ...
