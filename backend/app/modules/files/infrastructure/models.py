"""SQLAlchemy 2 ORM model for file_assets metadata (DBD §16.1)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FileAssetModel(Base):
    """Non-public evidence file asset metadata referenced across modules."""

    __tablename__ = "file_assets"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    storage_provider: Mapped[str] = mapped_column(String(30), nullable=False, default="LOCAL_DISK")
    storage_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(150), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(80), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    classification: Mapped[str] = mapped_column(String(40), nullable=False)
    uploaded_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user_accounts.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        CheckConstraint(
            "mime_type IN ('application/pdf', 'image/jpeg', 'image/png')",
            name="file_asset_mime_valid",
        ),
        CheckConstraint("size_bytes >= 1 AND size_bytes <= 10485760", name="file_asset_size_range"),
        CheckConstraint(
            "classification IN "
            "('PRICE_EVIDENCE', 'MILL_TICKET_PROOF', 'DISPUTE_EVIDENCE', 'PAYMENT_PROOF')",
            name="file_asset_classification_valid",
        ),
        Index("ix_file_assets_uploaded_by", "uploaded_by", "created_at"),
    )
