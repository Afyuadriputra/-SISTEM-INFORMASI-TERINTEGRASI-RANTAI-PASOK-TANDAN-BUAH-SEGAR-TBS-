"""SQLAlchemy 2 ORM models for reconciliation_cases, dispute_reviews, farmer allocations."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ReconciliationCaseModel(Base):
    """Revisioned reconciliation case comparing e-DO origin weight vs verified mill weight."""

    __tablename__ = "reconciliation_cases"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    delivery_order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("delivery_orders.id"), nullable=False
    )
    mill_ticket_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("mill_weighing_tickets.id"), nullable=True
    )
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    origin_weight_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    mill_weight_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    difference_weight_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    difference_percent: Mapped[Decimal] = mapped_column(Numeric(9, 4), nullable=False)
    tolerance_percent: Mapped[Decimal] = mapped_column(Numeric(9, 4), nullable=False)
    rule_version_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("system_rule_versions.id"), nullable=False
    )
    tolerance_policy_classification: Mapped[str] = mapped_column(String(25), nullable=False)
    is_negative_difference: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(25), nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    agreed_settlement_weight_kg: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 3), nullable=True
    )
    calculated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    dispute_reviews: Mapped[list[DisputeReviewModel]] = relationship(
        back_populates="reconciliation_case", order_by="DisputeReviewModel.reviewed_at"
    )
    farmer_allocations: Mapped[list[FarmerSettlementAllocationModel]] = relationship(
        back_populates="reconciliation_case",
        order_by="FarmerSettlementAllocationModel.created_at",
    )

    __table_args__ = (
        CheckConstraint("revision_number >= 1", name="rec_revision_positive"),
        CheckConstraint("origin_weight_kg >= 0", name="rec_origin_non_negative"),
        CheckConstraint("mill_weight_kg >= 0", name="rec_mill_non_negative"),
        CheckConstraint(
            "tolerance_policy_classification IN "
            "('CONFIRMED', 'SIMULATION_ONLY', 'PENDING_SOP', 'FUTURE')",
            name="rec_policy_class_valid",
        ),
        CheckConstraint(
            "status IN ('WAITING_TICKET', 'READY', 'MATCHED', 'DISPUTE_HOLD', "
            "'UNDER_REVIEW', 'RESOLVED', 'CANCELLED')",
            name="rec_status_valid",
        ),
        UniqueConstraint(
            "delivery_order_id", "revision_number", name="uq_reconciliation_do_revision"
        ),
        Index("ix_reconciliation_cases_status", "status"),
        Index(
            "ux_current_reconciliation_per_do",
            "delivery_order_id",
            unique=True,
            postgresql_where=text("is_current IS TRUE"),
        ),
    )


class DisputeReviewModel(Base):
    """Dual-reviewer dispute examination history linked to ReconciliationCase (DBD §13.4)."""

    __tablename__ = "dispute_reviews"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    reconciliation_case_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("reconciliation_cases.id"), nullable=False
    )
    reviewer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    previous_status: Mapped[str] = mapped_column(String(25), nullable=False)
    decision: Mapped[str] = mapped_column(String(40), nullable=False)
    proposed_settlement_weight_kg: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 3), nullable=True
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_file_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("file_assets.id"), nullable=True
    )
    approved_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=True
    )
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    reconciliation_case: Mapped[ReconciliationCaseModel] = relationship(
        back_populates="dispute_reviews"
    )

    __table_args__ = (
        CheckConstraint(
            "decision IN ('KEEP_ORIGIN_WEIGHT', 'ACCEPT_MILL_WEIGHT', "
            "'AGREED_SETTLEMENT_WEIGHT', 'REQUIRE_TICKET_REVISION', "
            "'HOLD_FOR_AUDIT', 'CANCEL_CASE')",
            name="dispute_decision_valid",
        ),
        Index("ix_dispute_reviews_case", "reconciliation_case_id", "reviewed_at"),
    )


class FarmerSettlementAllocationModel(Base):
    """Multi-farmer proportional settlement simulation / pending SOP allocation (DBD §13.5)."""

    __tablename__ = "farmer_settlement_allocations"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    reconciliation_case_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("reconciliation_cases.id"), nullable=False
    )
    receipt_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tbs_receipts.id"), nullable=False
    )
    farmer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False
    )
    allocation_basis_weight_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    agreed_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 3), nullable=True)
    allocation_policy_version_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("system_rule_versions.id"), nullable=False
    )
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    deduction_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(25), nullable=False)
    policy_classification: Mapped[str] = mapped_column(String(25), nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    reconciliation_case: Mapped[ReconciliationCaseModel] = relationship(
        back_populates="farmer_allocations"
    )

    __table_args__ = (
        CheckConstraint("allocation_basis_weight_kg >= 0", name="alloc_basis_non_negative"),
        CheckConstraint(
            "agreed_weight_kg IS NULL OR agreed_weight_kg >= 0",
            name="alloc_agreed_non_negative",
        ),
        CheckConstraint("gross_amount >= 0", name="alloc_gross_non_negative"),
        CheckConstraint("deduction_amount >= 0", name="alloc_deduction_non_negative"),
        CheckConstraint("net_amount >= 0", name="alloc_net_non_negative"),
        CheckConstraint(
            "status IN ('SIMULATED', 'PENDING_SOP_LOCKED', 'APPROVED', 'SETTLED')",
            name="alloc_status_valid",
        ),
        CheckConstraint(
            "policy_classification IN ('CONFIRMED', 'SIMULATION_ONLY', 'PENDING_SOP', 'FUTURE')",
            name="alloc_policy_class_valid",
        ),
        Index("ix_farmer_allocations_case_farmer", "reconciliation_case_id", "farmer_id"),
    )
