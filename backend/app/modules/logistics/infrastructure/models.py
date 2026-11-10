"""SQLAlchemy 2 ORM models for delivery_orders, delivery_order_lines, delivery_status_events."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DeliveryOrderModel(Base):
    """Consolidated electronic Delivery Order (e-DO) header (DBD §11.1)."""

    __tablename__ = "delivery_orders"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    delivery_order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    cooperative_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("cooperatives.id"), nullable=False
    )
    mill_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("mills.id"), nullable=False
    )
    contract_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("trade_contracts.id"), nullable=False
    )
    vehicle_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False
    )
    driver_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("drivers.id"), nullable=False
    )
    total_origin_weight_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DRAFT")
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    departed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    arrived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    qr_verification_token: Mapped[str | None] = mapped_column(
        String(80), unique=True, nullable=True
    )
    qr_reference_hash: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    created_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    lines: Mapped[list[DeliveryOrderLineModel]] = relationship(
        back_populates="delivery_order", order_by="DeliveryOrderLineModel.created_at"
    )
    status_events: Mapped[list[DeliveryStatusEventModel]] = relationship(
        back_populates="delivery_order", order_by="DeliveryStatusEventModel.event_time"
    )

    __table_args__ = (
        CheckConstraint("total_origin_weight_kg > 0", name="do_total_origin_positive"),
        CheckConstraint(
            "status IN "
            "('DRAFT', 'READY', 'IN_TRANSIT', 'ARRIVED', 'RECEIVED', 'COMPLETED', 'CANCELLED')",
            name="do_status_valid",
        ),
        CheckConstraint("version >= 1", name="do_version_positive"),
        Index("ix_delivery_orders_coop_status", "cooperative_id", "status"),
        Index("ix_delivery_orders_mill_status", "mill_id", "status"),
    )


class DeliveryOrderLineModel(Base):
    """Receipt allocation line with partial unique index blocking double allocation (DBD §11.2)."""

    __tablename__ = "delivery_order_lines"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    delivery_order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("delivery_orders.id"), nullable=False
    )
    receipt_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tbs_receipts.id"), nullable=False
    )
    origin_weight_snapshot_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    allocation_status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    delivery_order: Mapped[DeliveryOrderModel] = relationship(back_populates="lines")

    __table_args__ = (
        CheckConstraint("origin_weight_snapshot_kg > 0", name="do_line_weight_positive"),
        CheckConstraint(
            "allocation_status IN ('ACTIVE', 'RELEASED')",
            name="do_line_allocation_status_valid",
        ),
        Index("ix_delivery_order_lines_do_id", "delivery_order_id"),
        Index(
            "ux_active_receipt_allocation",
            "receipt_id",
            unique=True,
            postgresql_where=text("allocation_status = 'ACTIVE'"),
        ),
    )


class DeliveryStatusEventModel(Base):
    """Append-only SM-05 delivery order status transition ledger (DBD §11.4)."""

    __tablename__ = "delivery_status_events"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    delivery_order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("delivery_orders.id"), nullable=False
    )
    previous_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    new_status: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)

    delivery_order: Mapped[DeliveryOrderModel] = relationship(back_populates="status_events")

    __table_args__ = (
        Index("ix_delivery_status_events_do_time", "delivery_order_id", "event_time"),
    )
