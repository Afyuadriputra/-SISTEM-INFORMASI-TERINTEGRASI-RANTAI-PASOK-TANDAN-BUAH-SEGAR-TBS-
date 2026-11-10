"""Versioned business policy & tolerance rule catalog backed by system_rule_versions (DBD §16.5)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid5

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

_RULE_NAMESPACE = UUID("d9a2c4f0-8c3e-4b2a-9a10-000000000001")

RULE_RECONCILIATION_TOLERANCE_ID = UUID("90000000-0000-4000-8000-000000000001")
RULE_BUSINESS_MODEL_POLICY_ID = UUID("90000000-0000-4000-8000-000000000002")
RULE_FARMER_ALLOCATION_POLICY_ID = UUID("90000000-0000-4000-8000-000000000003")


def deterministic_rule_id(rule_code: str, version_number: int) -> UUID:
    """Return canonical UUID for known baseline system rules or deterministic UUIDv5."""
    canonical = {
        ("RECONCILIATION_TOLERANCE", 1): RULE_RECONCILIATION_TOLERANCE_ID,
        ("BUSINESS_MODEL_POLICY", 1): RULE_BUSINESS_MODEL_POLICY_ID,
        ("FARMER_ALLOCATION_POLICY", 1): RULE_FARMER_ALLOCATION_POLICY_ID,
    }
    return canonical.get((rule_code, version_number)) or uuid5(
        _RULE_NAMESPACE, f"{rule_code}:v{version_number}"
    )


class SystemRuleVersionModel(Base):
    """Stores auditable rule versions for tolerances, business model SOP, and allocations."""

    __tablename__ = "system_rule_versions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    rule_code: Mapped[str] = mapped_column(String(80), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rule_config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    approval_status: Mapped[str] = mapped_column(String(30), nullable=False)
    approved_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        CheckConstraint("version_number >= 1", name="system_rule_version_positive"),
        CheckConstraint(
            "approval_status IN "
            "('DRAFT', 'SIMULATION_ONLY', 'PENDING_SOP', 'APPROVED', 'SUPERSEDED')",
            name="system_rule_approval_status_valid",
        ),
        UniqueConstraint(
            "rule_code", "version_number", name="uq_system_rule_versions_code_version"
        ),
        Index("ix_system_rule_versions_code_effective", "rule_code", "effective_from"),
    )


async def seed_baseline_system_rules(session: AsyncSession) -> None:
    """Idempotently seed canonical baseline rules representing PENDING_SOP / SIMULATION_ONLY."""
    now = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
    seeds = (
        (
            RULE_RECONCILIATION_TOLERANCE_ID,
            "RECONCILIATION_TOLERANCE",
            1,
            {
                "tolerance_percent": "1.5000",
                "negative_difference_holds": True,
                "policy_classification": "SIMULATION_ONLY",
                "sop_ref": "BSD-DEC-007",
            },
            "SIMULATION_ONLY",
        ),
        (
            RULE_BUSINESS_MODEL_POLICY_ID,
            "BUSINESS_MODEL_POLICY",
            1,
            {
                "default_business_model_code": "UNCONFIRMED",
                "default_perumda_role": "UNCONFIRMED",
                "policy_classification": "PENDING_SOP",
                "sop_ref": "BSD-DEC-001",
            },
            "PENDING_SOP",
        ),
        (
            RULE_FARMER_ALLOCATION_POLICY_ID,
            "FARMER_ALLOCATION_POLICY",
            1,
            {
                "allocation_basis": "UNCONFIRMED",
                "default_simulation_basis": "PROPORTIONAL_ORIGIN_WEIGHT",
                "policy_classification": "PENDING_SOP",
                "sop_ref": "BSD-DEC-013",
            },
            "PENDING_SOP",
        ),
    )
    for rid, code, ver, cfg, status in seeds:
        existing = await session.get(SystemRuleVersionModel, rid)
        if existing is None:
            session.add(
                SystemRuleVersionModel(
                    id=rid,
                    rule_code=code,
                    version_number=ver,
                    effective_from=now,
                    effective_until=None,
                    rule_config=cfg,
                    approval_status=status,
                    approved_by=None,
                    created_at=now,
                )
            )
    await session.flush()
