"""SQLAlchemy 2 ORM models for mill_weighing_tickets and mill_grading_items (DBD §12)."""

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


class MillWeighingTicketModel(Base):
    """Revisioned PKS weighbridge ticket tied uniquely to an e-DO at current revision."""

    __tablename__ = "mill_weighing_tickets"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    delivery_order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("delivery_orders.id"), nullable=False
    )
    mill_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("mills.id"), nullable=False
    )
    ticket_number: Mapped[str] = mapped_column(String(60), nullable=False)
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    previous_ticket_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("mill_weighing_tickets.id"), nullable=True
    )
    gross_weight_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    tare_weight_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    net_weight_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    weighed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=True
    )
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="SUBMITTED")
    proof_file_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("file_assets.id"), nullable=True
    )
    correction_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    grading_items: Mapped[list[MillGradingItemModel]] = relationship(
        back_populates="mill_ticket", order_by="MillGradingItemModel.created_at"
    )

    __table_args__ = (
        CheckConstraint("revision_number >= 1", name="mill_ticket_revision_positive"),
        CheckConstraint("gross_weight_kg > 0", name="mill_ticket_gross_positive"),
        CheckConstraint("tare_weight_kg >= 0", name="mill_ticket_tare_non_negative"),
        CheckConstraint("tare_weight_kg <= gross_weight_kg", name="mill_ticket_tare_lte_gross"),
        CheckConstraint(
            "net_weight_kg = gross_weight_kg - tare_weight_kg",
            name="mill_ticket_net_equals_gross_minus_tare",
        ),
        CheckConstraint(
            "status IN ('DRAFT', 'SUBMITTED', 'VERIFIED')",
            name="mill_ticket_status_valid",
        ),
        UniqueConstraint(
            "delivery_order_id", "revision_number", name="uq_mill_tickets_do_revision"
        ),
        Index("ix_mill_tickets_mill_status", "mill_id", "status"),
        Index(
            "ux_current_mill_ticket_per_do",
            "delivery_order_id",
            unique=True,
            postgresql_where=text("is_current IS TRUE"),
        ),
        Index(
            "uq_mill_tickets_mill_number_current",
            "mill_id",
            "ticket_number",
            unique=True,
            postgresql_where=text("is_current IS TRUE"),
        ),
    )


class MillGradingItemModel(Base):
    """PKS factory grading note tied to mill_weighing_tickets (DBD §12.3)."""

    __tablename__ = "mill_grading_items"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    mill_ticket_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("mill_weighing_tickets.id"), nullable=False
    )
    grading_category: Mapped[str] = mapped_column(String(120), nullable=False)
    deduction_type: Mapped[str] = mapped_column(String(25), nullable=False)
    deduction_value: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    calculation_basis: Mapped[str] = mapped_column(String(60), nullable=False)
    is_simulation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    mill_ticket: Mapped[MillWeighingTicketModel] = relationship(back_populates="grading_items")

    __table_args__ = (
        CheckConstraint(
            "deduction_type IN ('WEIGHT_PERCENT', 'WEIGHT_KG', 'VALUE_AMOUNT')",
            name="mill_grading_deduction_type_valid",
        ),
        CheckConstraint("deduction_value >= 0", name="mill_grading_deduction_value_non_negative"),
    )
