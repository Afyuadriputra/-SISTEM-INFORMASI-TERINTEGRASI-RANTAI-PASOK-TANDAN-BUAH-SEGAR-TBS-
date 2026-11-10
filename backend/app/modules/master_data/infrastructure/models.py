"""SQLAlchemy 2 ORM models for Master Data tables (DBD §7.1-7.10)."""

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
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PartyModel(Base):
    __tablename__ = "parties"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    party_type: Mapped[str] = mapped_column(String(30), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        CheckConstraint(
            "party_type IN ('PERUMDA', 'FARMER', 'COOPERATIVE', 'MILL_COMPANY')",
            name="party_type_valid",
        ),
        CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name="party_status_valid"),
    )


class CooperativeModel(Base):
    __tablename__ = "cooperatives"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    party_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("parties.id"), unique=True, nullable=False
    )
    cooperative_code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    cooperative_name: Mapped[str] = mapped_column(String(180), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name="cooperative_status_valid"),
    )


class FarmerModel(Base):
    __tablename__ = "farmers"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    party_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("parties.id"), unique=True, nullable=False
    )
    farmer_code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    identity_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    memberships: Mapped[list[CooperativeMembershipModel]] = relationship(back_populates="farmer")

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name="farmer_status_valid"),
        CheckConstraint("version >= 1", name="farmer_version_positive"),
        Index("ix_farmers_farmer_code", "farmer_code"),
    )


class CooperativeMembershipModel(Base):
    __tablename__ = "cooperative_memberships"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    cooperative_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("cooperatives.id"), nullable=False
    )
    farmer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False
    )
    membership_number: Mapped[str | None] = mapped_column(String(60), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")

    farmer: Mapped[FarmerModel] = relationship(back_populates="memberships")

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name="membership_status_valid"),
        Index("ix_cooperative_memberships_coop_farmer", "cooperative_id", "farmer_id"),
        Index(
            "uq_cooperative_memberships_active_farmer",
            "farmer_id",
            unique=True,
            postgresql_where=text("status = 'ACTIVE' AND ended_at IS NULL"),
        ),
    )


class FarmModel(Base):
    __tablename__ = "farms"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    farmer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False
    )
    farm_code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    farm_name: Mapped[str] = mapped_column(String(150), nullable=False)
    area_hectares: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    planting_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stdb_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    village: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    verification_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="UNVERIFIED"
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    farmer: Mapped[FarmerModel] = relationship()

    __table_args__ = (
        CheckConstraint("area_hectares > 0", name="farm_area_positive"),
        CheckConstraint(
            "planting_year IS NULL OR (planting_year BETWEEN 1970 AND 2035)",
            name="farm_planting_year_range",
        ),
        CheckConstraint(
            "(latitude IS NULL AND longitude IS NULL) OR "
            "(latitude IS NOT NULL AND longitude IS NOT NULL)",
            name="farm_paired_coordinates",
        ),
        CheckConstraint(
            "latitude IS NULL OR (latitude >= -90 AND latitude <= 90)", name="farm_lat_range"
        ),
        CheckConstraint(
            "longitude IS NULL OR (longitude >= -180 AND longitude <= 180)", name="farm_lng_range"
        ),
        CheckConstraint(
            "verification_status IN ('UNVERIFIED', 'VERIFIED')", name="farm_verification_valid"
        ),
        CheckConstraint("version >= 1", name="farm_version_positive"),
        Index("ix_farms_farmer_id", "farmer_id"),
    )


class MillCompanyModel(Base):
    __tablename__ = "mill_companies"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    party_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("parties.id"), unique=True, nullable=False
    )
    company_code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    company_name: Mapped[str] = mapped_column(String(180), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name="mill_company_status_valid"),
    )


class MillModel(Base):
    __tablename__ = "mills"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    mill_company_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("mill_companies.id"), nullable=False
    )
    mill_code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    mill_name: Mapped[str] = mapped_column(String(180), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    regency: Mapped[str] = mapped_column(String(100), nullable=False)
    province: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    partnership_status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    location_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    mill_company: Mapped[MillCompanyModel] = relationship()

    __table_args__ = (
        CheckConstraint(
            "(latitude IS NULL AND longitude IS NULL) OR "
            "(latitude IS NOT NULL AND longitude IS NOT NULL)",
            name="mill_paired_coordinates",
        ),
        CheckConstraint(
            "latitude IS NULL OR (latitude >= -90 AND latitude <= 90)", name="mill_lat_range"
        ),
        CheckConstraint(
            "longitude IS NULL OR (longitude >= -180 AND longitude <= 180)", name="mill_lng_range"
        ),
        CheckConstraint(
            "partnership_status IN ('ACTIVE', 'INACTIVE')", name="mill_partnership_status_valid"
        ),
        CheckConstraint("version >= 1", name="mill_version_positive"),
        Index("ix_mills_code_regency", "mill_code", "regency"),
        Index("ix_mills_public_partnership", "is_public", "partnership_status"),
    )


class PerumdaOfficeModel(Base):
    __tablename__ = "perumda_offices"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    party_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("parties.id"), nullable=True
    )
    office_name: Mapped[str] = mapped_column(String(180), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    public_contact: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        CheckConstraint(
            "(latitude IS NULL AND longitude IS NULL) OR "
            "(latitude IS NOT NULL AND longitude IS NOT NULL)",
            name="office_paired_coordinates",
        ),
    )


class VehicleModel(Base):
    __tablename__ = "vehicles"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    plate_number: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(80), nullable=False)
    nominal_capacity_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 3), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        CheckConstraint(
            "nominal_capacity_kg IS NULL OR nominal_capacity_kg > 0",
            name="vehicle_capacity_positive",
        ),
        CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name="vehicle_status_valid"),
    )


class DriverModel(Base):
    __tablename__ = "drivers"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    driver_reference: Mapped[str | None] = mapped_column(String(60), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name="driver_status_valid"),
    )
