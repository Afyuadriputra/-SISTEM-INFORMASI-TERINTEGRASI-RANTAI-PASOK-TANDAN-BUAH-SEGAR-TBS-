"""SQLAlchemy 2 ORM models for trade_contracts, quota periods, reservations, and approval events."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TradeContractModel(Base):
    """Confidential commercial contract between Perumda / Principal and PKS (DBD §10.1)."""

    __tablename__ = "trade_contracts"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    contract_number: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    mill_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("mills.id"), nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    price_rule_type: Mapped[str] = mapped_column(String(30), nullable=False)
    agreed_price_per_kg: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    grading_policy_reference: Mapped[str] = mapped_column(
        String(120), nullable=False, default="BSD-DEC-006-SIMULATION"
    )
    business_model_code: Mapped[str] = mapped_column(String(20), nullable=False)
    perumda_role: Mapped[str] = mapped_column(String(20), nullable=False)
    seller_party_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False
    )
    buyer_party_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False
    )
    agent_party_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("parties.id"), nullable=True
    )
    represented_party_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("parties.id"), nullable=True
    )
    business_model_rule_version: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("system_rule_versions.id"), nullable=False
    )
    payment_terms: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(25), nullable=False, default="PENDING_APPROVAL")
    created_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    approved_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    quota_periods: Mapped[list[ContractQuotaPeriodModel]] = relationship(
        back_populates="contract", order_by="ContractQuotaPeriodModel.period_start"
    )

    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="trade_contract_date_range_valid"),
        CheckConstraint(
            "price_rule_type IN ('FIXED', 'REFERENCE_FORMULA', 'PERIOD_SCHEDULE')",
            name="trade_contract_price_rule_valid",
        ),
        CheckConstraint(
            "agreed_price_per_kg IS NULL OR agreed_price_per_kg > 0",
            name="trade_contract_agreed_price_positive",
        ),
        CheckConstraint(
            "business_model_code IN ('PRINCIPAL', 'AGENT', 'UNCONFIRMED')",
            name="trade_contract_business_model_valid",
        ),
        CheckConstraint(
            "perumda_role IN ('BUYER', 'SELLER', 'AGENT', 'UNCONFIRMED')",
            name="trade_contract_perumda_role_valid",
        ),
        CheckConstraint(
            "(business_model_code != 'AGENT' OR "
            "(agent_party_id IS NOT NULL AND represented_party_id IS NOT NULL "
            "AND perumda_role = 'AGENT'))",
            name="trade_contract_agent_parties_valid",
        ),
        CheckConstraint(
            "(business_model_code != 'PRINCIPAL' OR "
            "(represented_party_id IS NULL AND perumda_role IN ('BUYER', 'SELLER')))",
            name="trade_contract_principal_parties_valid",
        ),
        CheckConstraint(
            "seller_party_id <> buyer_party_id", name="trade_contract_distinct_parties"
        ),
        CheckConstraint(
            "status IN "
            "('DRAFT', 'PENDING_APPROVAL', 'ACTIVE', 'SUSPENDED', 'COMPLETED', 'CANCELLED')",
            name="trade_contract_status_valid",
        ),
        CheckConstraint("version >= 1", name="trade_contract_version_positive"),
        Index("ix_trade_contracts_mill_status", "mill_id", "status"),
    )


class ContractQuotaPeriodModel(Base):
    """Contract delivery quota window (DBD §10.2)."""

    __tablename__ = "contract_quota_periods"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    contract_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("trade_contracts.id"), nullable=False
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    quota_limit_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    contract: Mapped[TradeContractModel] = relationship(back_populates="quota_periods")
    reservations: Mapped[list[QuotaReservationModel]] = relationship(back_populates="quota_period")

    __table_args__ = (
        CheckConstraint("period_end >= period_start", name="quota_period_dates_valid"),
        CheckConstraint("quota_limit_kg > 0", name="quota_period_limit_positive"),
        CheckConstraint("status IN ('ACTIVE', 'CLOSED')", name="quota_period_status_valid"),
        Index("ix_contract_quota_periods_contract_status", "contract_id", "status"),
    )


class QuotaReservationModel(Base):
    """Quota reservation & consumption ledger row linked to e-DO (DBD §10.3)."""

    __tablename__ = "quota_reservations"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    quota_period_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("contract_quota_periods.id"), nullable=False
    )
    delivery_order_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    reserved_weight_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    consumed_weight_kg: Mapped[Decimal] = mapped_column(
        Numeric(14, 3), nullable=False, default=Decimal("0.000")
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="RESERVED")
    reserved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    quota_period: Mapped[ContractQuotaPeriodModel] = relationship(back_populates="reservations")

    __table_args__ = (
        CheckConstraint("reserved_weight_kg > 0", name="quota_res_reserved_positive"),
        CheckConstraint("consumed_weight_kg >= 0", name="quota_res_consumed_non_negative"),
        CheckConstraint(
            "status IN ('RESERVED', 'CONSUMED', 'RELEASED')",
            name="quota_res_status_valid",
        ),
        Index("ix_quota_reservations_period_status", "quota_period_id", "status"),
        Index(
            "uq_quota_reservations_active_do",
            "delivery_order_id",
            unique=True,
            postgresql_where=text("status IN ('RESERVED', 'CONSUMED')"),
        ),
    )


class ContractApprovalEventModel(Base):
    """Append-only approval & transition history on commercial contracts."""

    __tablename__ = "contract_approval_events"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    contract_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("trade_contracts.id"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(40), nullable=False)
    previous_status: Mapped[str] = mapped_column(String(25), nullable=False)
    new_status: Mapped[str] = mapped_column(String(25), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        Index("ix_contract_approval_events_contract_id", "contract_id", "created_at"),
    )
