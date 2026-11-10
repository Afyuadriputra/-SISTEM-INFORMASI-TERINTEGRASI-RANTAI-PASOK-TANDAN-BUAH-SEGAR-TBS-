"""Pure domain entities and enums for Master Data (DBD §7)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


class PartyType(StrEnum):
    PERUMDA = "PERUMDA"
    FARMER = "FARMER"
    COOPERATIVE = "COOPERATIVE"
    MILL_COMPANY = "MILL_COMPANY"


class EntityStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class VerificationStatus(StrEnum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"


@dataclass(frozen=True, slots=True)
class FarmerEntity:
    id: UUID
    party_id: UUID
    farmer_code: str
    full_name: str
    contact_phone: str
    cooperative_id: UUID
    membership_number: str | None
    status: EntityStatus
    version: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class FarmEntity:
    id: UUID
    farmer_id: UUID
    cooperative_id: UUID
    farm_code: str
    farm_name: str
    area_hectares: Decimal
    planting_year: int | None
    stdb_number: str | None
    village: str
    district: str
    latitude: Decimal | None
    longitude: Decimal | None
    verification_status: VerificationStatus
    version: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class CooperativeEntity:
    id: UUID
    party_id: UUID
    cooperative_code: str
    cooperative_name: str
    address: str
    contact_phone: str
    status: EntityStatus


@dataclass(frozen=True, slots=True)
class MillCompanyEntity:
    id: UUID
    party_id: UUID
    company_code: str
    company_name: str
    contact_phone: str
    address: str
    status: EntityStatus
    created_at: datetime


@dataclass(frozen=True, slots=True)
class MillEntity:
    id: UUID
    mill_company_id: UUID
    company_name: str
    mill_code: str
    mill_name: str
    address: str
    district: str
    regency: str
    province: str
    latitude: Decimal | None
    longitude: Decimal | None
    contact_phone: str | None
    partnership_status: EntityStatus
    is_public: bool
    location_verified_at: datetime | None
    version: int
    created_at: datetime
    updated_at: datetime

    @property
    def has_verified_coordinates(self) -> bool:
        return self.latitude is not None and self.longitude is not None


@dataclass(frozen=True, slots=True)
class VehicleEntity:
    id: UUID
    plate_number: str
    vehicle_type: str
    nominal_capacity_kg: Decimal | None
    status: EntityStatus


@dataclass(frozen=True, slots=True)
class DriverEntity:
    id: UUID
    full_name: str
    contact_phone: str
    driver_reference: str | None
    status: EntityStatus
