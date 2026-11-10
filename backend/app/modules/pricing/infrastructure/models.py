"""SQLAlchemy 2 ORM models for Multi-Mill TBS Pricing and Disbun References (DBD §8)."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

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
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.modules.master_data.infrastructure.models import MillModel
from app.modules.pricing.domain.rules import CANONICAL_PRICE_CATEGORIES, CANONICAL_PRICE_SOURCES


class PriceSourceModel(Base):
    __tablename__ = "price_sources"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    source_name: Mapped[str] = mapped_column(String(150), nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")

    __table_args__ = (
        CheckConstraint(
            "source_type IN ('DISBUN', 'MILL_OFFICIAL', 'MILL_DOCUMENT', 'VERIFIED_MANUAL')",
            name="price_source_type_valid",
        ),
        CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name="price_source_status_valid"),
    )


class PriceCategoryModel(Base):
    __tablename__ = "price_categories"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    category_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False, default="IDR/kg")
    quality_basis: Mapped[str] = mapped_column(Text, nullable=False)
    age_group: Mapped[str | None] = mapped_column(String(60), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class MillPriceQuoteModel(Base):
    __tablename__ = "mill_price_quotes"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    mill_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("mills.id"), nullable=False
    )
    price_category_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("price_categories.id"), nullable=False
    )
    source_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("price_sources.id"), nullable=False
    )
    price_per_kg: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(25), nullable=False, default="DRAFT")
    submitted_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    verified_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_document_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_simulation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    mill: Mapped[MillModel] = relationship()
    category: Mapped[PriceCategoryModel] = relationship()
    source: Mapped[PriceSourceModel] = relationship()
    verification_events: Mapped[list[PriceVerificationEventModel]] = relationship(
        back_populates="quote",
        order_by="PriceVerificationEventModel.created_at.asc()",
    )

    __table_args__ = (
        CheckConstraint("price_per_kg > 0", name="quote_price_positive"),
        CheckConstraint(
            "effective_until IS NULL OR effective_until > effective_from",
            name="quote_period_valid",
        ),
        CheckConstraint(
            "status IN ('DRAFT', 'PENDING_VERIFICATION', 'VERIFIED', "
            "'REJECTED', 'PUBLISHED', 'REVOKED')",
            name="quote_status_valid",
        ),
        CheckConstraint("version >= 1", name="quote_version_positive"),
        Index(
            "ix_mill_price_quotes_lookup",
            "mill_id",
            "price_category_id",
            "effective_from",
        ),
        Index("ix_mill_price_quotes_status_from", "status", "effective_from"),
    )


class PriceVerificationEventModel(Base):
    __tablename__ = "price_verification_events"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    price_quote_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("mill_price_quotes.id"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    previous_status: Mapped[str] = mapped_column(String(25), nullable=False)
    new_status: Mapped[str] = mapped_column(String(25), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    quote: Mapped[MillPriceQuoteModel] = relationship(back_populates="verification_events")

    __table_args__ = (Index("ix_price_verification_events_quote", "price_quote_id", "created_at"),)


class DisbunReferencePriceModel(Base):
    __tablename__ = "disbun_reference_prices"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    price_source_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("price_sources.id"), nullable=False
    )
    price_category_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("price_categories.id"), nullable=False
    )
    price_per_kg: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_document_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    verification_status: Mapped[str] = mapped_column(
        String(25), nullable=False, default="PUBLISHED"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    source: Mapped[PriceSourceModel] = relationship()
    category: Mapped[PriceCategoryModel] = relationship()

    __table_args__ = (
        CheckConstraint("price_per_kg > 0", name="disbun_price_positive"),
        CheckConstraint(
            "effective_until IS NULL OR effective_until > effective_from",
            name="disbun_period_valid",
        ),
        CheckConstraint(
            "verification_status IN ('VERIFIED', 'PUBLISHED')",
            name="disbun_status_valid",
        ),
        Index("ix_disbun_reference_prices_from", "effective_from"),
    )


def deterministic_source_id(source_code: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"agroniaga:price_source:{source_code}")


def deterministic_category_id(category_code: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"agroniaga:price_category:{category_code}")


async def seed_pricing_catalog(session: AsyncSession) -> None:
    """Idempotently seed canonical price sources & non-comparable price categories."""
    await session.execute(
        insert(PriceSourceModel)
        .values(
            [
                {
                    "id": deterministic_source_id(s.code),
                    "source_code": s.code,
                    "source_name": s.name,
                    "source_type": s.source_type,
                    "source_url": None,
                    "description": s.description,
                    "status": "ACTIVE",
                }
                for s in CANONICAL_PRICE_SOURCES
            ]
        )
        .on_conflict_do_nothing()
    )
    await session.execute(
        insert(PriceCategoryModel)
        .values(
            [
                {
                    "id": deterministic_category_id(c.code),
                    "category_code": c.code,
                    "name": c.name,
                    "description": c.description,
                    "unit": c.unit,
                    "quality_basis": c.quality_basis,
                    "age_group": c.age_group,
                    "is_active": True,
                }
                for c in CANONICAL_PRICE_CATEGORIES
            ]
        )
        .on_conflict_do_nothing()
    )
    await session.flush()
