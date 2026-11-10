"""Shared append-only audit event ORM model and sanitized writer (DBD §16.2)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.logging import redact_mapping, request_id_ctx


class AuditEventModel(Base):
    """Append-only business and security audit log stored in PostgreSQL."""

    __tablename__ = "audit_events"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    actor_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(80), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(100), nullable=False)
    previous_state: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    new_state: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_id: Mapped[str] = mapped_column(String(80), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        Index("ix_audit_events_resource_lookup", "resource_type", "resource_id", "occurred_at"),
        Index("ix_audit_events_module_occurred", "module", "occurred_at"),
        Index("ix_audit_events_request_id", "request_id"),
    )


@dataclass(frozen=True, slots=True)
class AuditRecordInput:
    """Domain-neutral input structure for recording an immutable audit event."""

    actor_id: UUID | None
    event_type: str
    module: str
    resource_type: str
    resource_id: str
    previous_state: dict[str, Any] | None = None
    new_state: dict[str, Any] | None = None
    reason: str | None = None
    request_id: str | None = None
    occurred_at: datetime | None = None


def append_audit_event(session: AsyncSession, record: AuditRecordInput) -> AuditEventModel:
    """Stage an immutable, redacted audit event row on the active transaction session."""
    model = AuditEventModel(
        id=uuid4(),
        actor_id=record.actor_id,
        event_type=record.event_type,
        module=record.module,
        resource_type=record.resource_type,
        resource_id=record.resource_id,
        previous_state=redact_mapping(record.previous_state)
        if record.previous_state is not None
        else None,
        new_state=redact_mapping(record.new_state) if record.new_state is not None else None,
        reason=record.reason,
        request_id=record.request_id or request_id_ctx.get(),
        occurred_at=record.occurred_at or datetime.now(UTC),
    )
    session.add(model)
    return model
