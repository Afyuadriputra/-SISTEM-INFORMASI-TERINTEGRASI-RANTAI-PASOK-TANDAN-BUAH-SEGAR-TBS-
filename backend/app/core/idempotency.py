"""Durable PostgreSQL idempotency engine for the 8 critical mutation operations (DBD §16.3)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, delete, select, update
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.exceptions import AppError, ErrorCode
from app.core.idempotency_primitives import (
    IdempotencyReservation,
    IdempotencySlotPort,
    compute_request_hash,
    validate_idempotency_key,
)

__all__ = [
    "IdempotencyRecordModel",
    "IdempotencyReservation",
    "IdempotencySlotPort",
    "SqlAlchemyIdempotencySlotAdapter",
    "complete_idempotency_slot",
    "compute_request_hash",
    "release_idempotency_slot_on_error",
    "reserve_idempotency_slot",
    "validate_idempotency_key",
]


class IdempotencyRecordModel(Base):
    """Stores durable idempotency outcomes keyed by (actor_id, operation_key, idempotency_key)."""

    __tablename__ = "idempotency_records"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    actor_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    operation_key: Mapped[str] = mapped_column(String(80), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    processing_status: Mapped[str] = mapped_column(String(20), nullable=False)
    response_reference: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    response_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "processing_status IN ('IN_PROGRESS', 'COMPLETED', 'FAILED')",
            name="idempotency_status_valid",
        ),
        Index(
            "uq_idempotency_records_actor_op_key",
            "actor_id",
            "operation_key",
            "idempotency_key",
            unique=True,
        ),
        Index("ix_idempotency_records_expires_at", "expires_at"),
    )


async def reserve_idempotency_slot(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    actor_id: UUID,
    operation_key: str,
    idempotency_key: str,
    request_hash: str,
    ttl_hours: int = 24,
) -> IdempotencyReservation:
    """Claim IN_PROGRESS slot atomically, or detect replay / payload mismatch / in-flight."""
    now = datetime.now(UTC)
    expires_at = now + timedelta(hours=ttl_hours)
    new_id = uuid4()

    async with session_factory() as session:
        async with session.begin():
            inserted = (
                await session.execute(
                    insert(IdempotencyRecordModel)
                    .values(
                        id=new_id,
                        actor_id=actor_id,
                        operation_key=operation_key,
                        idempotency_key=idempotency_key,
                        request_hash=request_hash,
                        processing_status="IN_PROGRESS",
                        response_reference=None,
                        response_payload=None,
                        created_at=now,
                        expires_at=expires_at,
                    )
                    .on_conflict_do_nothing(
                        index_elements=["actor_id", "operation_key", "idempotency_key"]
                    )
                    .returning(IdempotencyRecordModel.id)
                )
            ).scalar_one_or_none()
            if inserted is not None:
                return IdempotencyReservation(record_id=inserted, is_replay=False)

            existing = (
                await session.execute(
                    select(IdempotencyRecordModel)
                    .where(
                        IdempotencyRecordModel.actor_id == actor_id,
                        IdempotencyRecordModel.operation_key == operation_key,
                        IdempotencyRecordModel.idempotency_key == idempotency_key,
                    )
                    .with_for_update()
                )
            ).scalar_one()

            if existing.expires_at <= now or existing.processing_status == "FAILED":
                existing.request_hash = request_hash
                existing.processing_status = "IN_PROGRESS"
                existing.response_reference = None
                existing.response_payload = None
                existing.created_at = now
                existing.expires_at = expires_at
                return IdempotencyReservation(record_id=existing.id, is_replay=False)

            if existing.request_hash != request_hash:
                raise AppError(ErrorCode.IDM_KEY_CONFLICT_PAYLOAD_MISMATCH)

            if existing.processing_status == "IN_PROGRESS":
                raise AppError(ErrorCode.IDM_REQUEST_IN_PROGRESS)

            return IdempotencyReservation(
                record_id=existing.id,
                is_replay=True,
                response_reference=existing.response_reference,
                response_payload=existing.response_payload,
            )


async def complete_idempotency_slot(
    session: AsyncSession,
    *,
    record_id: UUID,
    response_reference: UUID | None = None,
    response_payload: dict[str, Any] | None = None,
) -> None:
    """Mark claimed idempotency record COMPLETED inside the committing business transaction."""
    await session.execute(
        update(IdempotencyRecordModel)
        .where(IdempotencyRecordModel.id == record_id)
        .values(
            processing_status="COMPLETED",
            response_reference=response_reference,
            response_payload=response_payload,
        )
    )


async def release_idempotency_slot_on_error(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    record_id: UUID,
) -> None:
    """Remove failed IN_PROGRESS slot so callers can correct invalid payloads or retry."""
    async with session_factory() as session:
        async with session.begin():
            await session.execute(
                delete(IdempotencyRecordModel).where(
                    IdempotencyRecordModel.id == record_id,
                    IdempotencyRecordModel.processing_status == "IN_PROGRESS",
                )
            )


class SqlAlchemyIdempotencySlotAdapter:
    """PostgreSQL-backed adapter satisfying IdempotencySlotPort."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def reserve(
        self,
        *,
        actor_id: UUID,
        operation_key: str,
        idempotency_key: str,
        request_hash: str,
        ttl_hours: int = 24,
    ) -> IdempotencyReservation:
        return await reserve_idempotency_slot(
            self._session_factory,
            actor_id=actor_id,
            operation_key=operation_key,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            ttl_hours=ttl_hours,
        )

    async def release_on_error(self, *, record_id: UUID) -> None:
        await release_idempotency_slot_on_error(self._session_factory, record_id=record_id)
