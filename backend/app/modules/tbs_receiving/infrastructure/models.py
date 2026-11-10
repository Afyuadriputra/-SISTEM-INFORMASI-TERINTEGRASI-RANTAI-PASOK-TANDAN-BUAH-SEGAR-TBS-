"""SQLAlchemy 2 ORM models for TBS Receiving, Weighing Revisions, and Grading (DBD §9)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
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


class TbsReceiptModel(Base):
    """Canonical farmer FFB/TBS cooperative intake header (DBD §9.1)."""

    __tablename__ = "tbs_receipts"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    receipt_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    farmer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False
    )
    farm_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("farms.id"), nullable=False
    )
    cooperative_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("cooperatives.id"), nullable=False
    )
    harvest_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DRAFT")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    weighing_revisions: Mapped[list[ReceiptWeighingRevisionModel]] = relationship(
        back_populates="receipt",
        order_by="ReceiptWeighingRevisionModel.revision_number",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('DRAFT', 'VALIDATED', 'ALLOCATED', 'SHIPPED', 'CLOSED', 'CANCELLED')",
            name="tbs_receipt_status_valid",
        ),
        CheckConstraint("version >= 1", name="tbs_receipt_version_positive"),
        Index("ix_tbs_receipts_coop_received", "cooperative_id", "received_at"),
        Index("ix_tbs_receipts_farmer_received", "farmer_id", "received_at"),
        Index("ix_tbs_receipts_status_coop", "status", "cooperative_id"),
    )


class ReceiptWeighingRevisionModel(Base):
    """Immutable versioned gross/tare/net weighing revisions (DBD §9.2)."""

    __tablename__ = "receipt_weighing_revisions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    receipt_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tbs_receipts.id"), nullable=False
    )
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    gross_weight_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    tare_weight_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    net_weight_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    weighed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    weighed_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    correction_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    receipt: Mapped[TbsReceiptModel] = relationship(back_populates="weighing_revisions")
    grading_items: Mapped[list[ReceiptGradingItemModel]] = relationship(
        back_populates="weighing_revision",
        order_by="ReceiptGradingItemModel.created_at",
    )

    __table_args__ = (
        CheckConstraint("revision_number >= 1", name="weighing_revision_number_positive"),
        CheckConstraint("gross_weight_kg > 0", name="weighing_gross_positive"),
        CheckConstraint("tare_weight_kg >= 0", name="weighing_tare_non_negative"),
        CheckConstraint("tare_weight_kg <= gross_weight_kg", name="weighing_tare_lte_gross"),
        CheckConstraint(
            "net_weight_kg = gross_weight_kg - tare_weight_kg",
            name="weighing_net_equals_gross_minus_tare",
        ),
        UniqueConstraint(
            "receipt_id",
            "revision_number",
            name="uq_receipt_weighing_revisions_receipt_rev",
        ),
        Index(
            "uq_receipt_weighing_revisions_current",
            "receipt_id",
            unique=True,
            postgresql_where=text("is_current IS TRUE"),
        ),
    )


class ReceiptGradingItemModel(Base):
    """Separate simulated grading deductions bound to a specific weighing revision (DBD §9.3)."""

    __tablename__ = "receipt_grading_items"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    weighing_revision_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("receipt_weighing_revisions.id"), nullable=False
    )
    grading_category: Mapped[str] = mapped_column(String(120), nullable=False)
    measurement_value: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    deduction_type: Mapped[str] = mapped_column(String(25), nullable=False)
    deduction_value: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    deduction_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 3), nullable=True)
    deduction_amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 2), nullable=True)
    calculation_basis: Mapped[str] = mapped_column(String(60), nullable=False)
    is_simulation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    weighing_revision: Mapped[ReceiptWeighingRevisionModel] = relationship(
        back_populates="grading_items"
    )

    __table_args__ = (
        CheckConstraint("measurement_value >= 0", name="grading_measurement_non_negative"),
        CheckConstraint(
            "deduction_type IN ('WEIGHT_PERCENT', 'WEIGHT_KG', 'VALUE_AMOUNT')",
            name="grading_deduction_type_valid",
        ),
        CheckConstraint("deduction_value >= 0", name="grading_deduction_value_non_negative"),
        CheckConstraint(
            "deduction_weight_kg IS NULL OR deduction_weight_kg >= 0",
            name="grading_deduction_weight_non_negative",
        ),
        CheckConstraint(
            "deduction_amount IS NULL OR deduction_amount >= 0",
            name="grading_deduction_amount_non_negative",
        ),
        UniqueConstraint(
            "weighing_revision_id",
            "grading_category",
            name="uq_receipt_grading_items_revision_category",
        ),
    )
