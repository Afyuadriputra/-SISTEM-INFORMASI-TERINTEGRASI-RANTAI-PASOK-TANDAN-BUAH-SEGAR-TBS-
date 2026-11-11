"""Strict Pydantic request/response schemas aligned 1:1 with Master Data OpenAPI."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from app.core.logging import format_utc_iso
from app.core.schemas import (
    PaginationMeta,
    SimpleSuccessMeta,
    StrictContractModel,
    format_decimal,
)
from app.modules.master_data.domain.entities import (
    CooperativeEntity,
    DriverEntity,
    EntityStatus,
    FarmEntity,
    FarmerEntity,
    MillCompanyEntity,
    MillEntity,
    VehicleEntity,
    VerificationStatus,
)


class FarmerDto(StrictContractModel):
    id: UUID
    party_id: UUID
    farmer_code: str
    full_name: str
    contact_phone: str
    cooperative_id: UUID
    membership_number: str | None
    status: EntityStatus
    version: int = Field(ge=1)
    created_at: str
    updated_at: str


class FarmerEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: FarmerDto
    meta: dict[str, Any] | None = None
    request_id: str


class FarmerListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[FarmerDto]
    meta: PaginationMeta
    request_id: str


class CreateFarmerRequest(StrictContractModel):
    farmer_code: str = Field(min_length=3, max_length=40)
    full_name: str = Field(min_length=2, max_length=150)
    contact_phone: str = Field(min_length=8, max_length=30)
    cooperative_id: UUID
    membership_number: str | None = Field(default=None, max_length=60)


class UpdateFarmerRequest(StrictContractModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    contact_phone: str | None = Field(default=None, min_length=8, max_length=30)
    status: EntityStatus | None = None
    reason: str | None = Field(default=None, max_length=500)
    version: int = Field(ge=1)


class FarmDto(StrictContractModel):
    id: UUID
    farmer_id: UUID
    farm_code: str
    farm_name: str
    area_hectares: str
    planting_year: int | None
    stdb_number: str | None
    village: str
    district: str
    latitude: str | None
    longitude: str | None
    verification_status: VerificationStatus
    is_public_location: Literal[False] = False
    version: int = Field(ge=1)
    created_at: str
    updated_at: str


class FarmEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: FarmDto
    meta: dict[str, Any] | None = None
    request_id: str


class FarmListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[FarmDto]
    meta: PaginationMeta
    request_id: str


class CreateFarmRequest(StrictContractModel):
    farmer_id: UUID
    farm_code: str = Field(min_length=3, max_length=40)
    farm_name: str = Field(min_length=2, max_length=150)
    area_hectares: str
    planting_year: int | None = Field(default=None, ge=1970, le=2035)
    stdb_number: str | None = Field(default=None, max_length=100)
    village: str = Field(min_length=2, max_length=100)
    district: str = Field(min_length=2, max_length=100)
    latitude: str | None = None
    longitude: str | None = None


class UpdateFarmRequest(StrictContractModel):
    farm_name: str | None = Field(default=None, min_length=2, max_length=150)
    area_hectares: str | None = None
    planting_year: int | None = Field(default=None, ge=1970, le=2035)
    stdb_number: str | None = Field(default=None, max_length=100)
    village: str | None = Field(default=None, min_length=2, max_length=100)
    district: str | None = Field(default=None, min_length=2, max_length=100)
    latitude: str | None = None
    longitude: str | None = None
    version: int = Field(ge=1)


class CooperativeDto(StrictContractModel):
    id: UUID
    party_id: UUID
    cooperative_code: str
    cooperative_name: str
    address: str
    contact_phone: str
    status: EntityStatus


class CooperativeListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[CooperativeDto]
    meta: PaginationMeta
    request_id: str


class MillCompanyDto(StrictContractModel):
    id: UUID
    party_id: UUID
    company_code: str
    company_name: str
    contact_phone: str
    address: str
    status: EntityStatus
    created_at: str


class MillCompanyEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: MillCompanyDto
    meta: dict[str, Any] | None = None
    request_id: str


class MillCompanyListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[MillCompanyDto]
    meta: PaginationMeta
    request_id: str


class CreateMillCompanyRequest(StrictContractModel):
    company_code: str = Field(min_length=3, max_length=40)
    company_name: str = Field(min_length=2, max_length=180)
    contact_phone: str = Field(min_length=8, max_length=30)
    address: str = Field(min_length=5, max_length=300)


class MillDto(StrictContractModel):
    id: UUID
    mill_company_id: UUID
    company_name: str
    mill_code: str
    mill_name: str
    address: str
    district: str
    regency: str
    province: str
    latitude: str | None
    longitude: str | None
    has_verified_coordinates: bool
    contact_phone: str | None
    partnership_status: EntityStatus
    is_public: bool
    location_verified_at: str | None
    version: int = Field(ge=1)
    created_at: str
    updated_at: str


class MillEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: MillDto
    meta: SimpleSuccessMeta
    request_id: str


class MillListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[MillDto]
    meta: PaginationMeta
    request_id: str


class CreateMillRequest(StrictContractModel):
    mill_company_id: UUID
    mill_code: str = Field(min_length=3, max_length=40)
    mill_name: str = Field(min_length=2, max_length=180)
    address: str = Field(min_length=5, max_length=300)
    district: str = Field(min_length=2, max_length=100)
    regency: str = Field(min_length=2, max_length=100)
    province: str = Field(min_length=2, max_length=100)
    latitude: str | None = None
    longitude: str | None = None
    contact_phone: str | None = Field(default=None, max_length=30)
    partnership_status: EntityStatus
    is_public: bool


class UpdateMillRequest(StrictContractModel):
    mill_name: str | None = Field(default=None, min_length=2, max_length=180)
    address: str | None = Field(default=None, min_length=5, max_length=300)
    district: str | None = Field(default=None, min_length=2, max_length=100)
    regency: str | None = Field(default=None, min_length=2, max_length=100)
    latitude: str | None = None
    longitude: str | None = None
    contact_phone: str | None = Field(default=None, max_length=30)
    partnership_status: EntityStatus | None = None
    is_public: bool | None = None
    version: int = Field(ge=1)


class VehicleDto(StrictContractModel):
    id: UUID
    plate_number: str
    vehicle_type: str
    nominal_capacity_kg: str | None
    status: EntityStatus


class VehicleEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: VehicleDto
    meta: dict[str, Any] | None = None
    request_id: str


class VehicleListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[VehicleDto]
    meta: PaginationMeta
    request_id: str


class CreateVehicleRequest(StrictContractModel):
    plate_number: str = Field(min_length=3, max_length=25)
    vehicle_type: str = Field(min_length=2, max_length=80)
    nominal_capacity_kg: str | None = None


class DriverDto(StrictContractModel):
    id: UUID
    full_name: str
    contact_phone: str
    driver_reference: str | None
    status: EntityStatus


class DriverEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: DriverDto
    meta: dict[str, Any] | None = None
    request_id: str


class DriverListEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: list[DriverDto]
    meta: PaginationMeta
    request_id: str


class CreateDriverRequest(StrictContractModel):
    full_name: str = Field(min_length=2, max_length=150)
    contact_phone: str = Field(min_length=8, max_length=30)
    driver_reference: str | None = Field(default=None, max_length=60)


def farmer_to_dto(e: FarmerEntity) -> FarmerDto:
    return FarmerDto(
        id=e.id,
        party_id=e.party_id,
        farmer_code=e.farmer_code,
        full_name=e.full_name,
        contact_phone=e.contact_phone,
        cooperative_id=e.cooperative_id,
        membership_number=e.membership_number,
        status=e.status,
        version=e.version,
        created_at=format_utc_iso(e.created_at) or "",
        updated_at=format_utc_iso(e.updated_at) or "",
    )


def farm_to_dto(e: FarmEntity) -> FarmDto:
    return FarmDto(
        id=e.id,
        farmer_id=e.farmer_id,
        farm_code=e.farm_code,
        farm_name=e.farm_name,
        area_hectares=format_decimal(e.area_hectares, 4) or "0.0000",
        planting_year=e.planting_year,
        stdb_number=e.stdb_number,
        village=e.village,
        district=e.district,
        latitude=format_decimal(e.latitude, 6),
        longitude=format_decimal(e.longitude, 6),
        verification_status=e.verification_status,
        is_public_location=False,
        version=e.version,
        created_at=format_utc_iso(e.created_at) or "",
        updated_at=format_utc_iso(e.updated_at) or "",
    )


def cooperative_to_dto(e: CooperativeEntity) -> CooperativeDto:
    return CooperativeDto(
        id=e.id,
        party_id=e.party_id,
        cooperative_code=e.cooperative_code,
        cooperative_name=e.cooperative_name,
        address=e.address,
        contact_phone=e.contact_phone,
        status=e.status,
    )


def mill_company_to_dto(e: MillCompanyEntity) -> MillCompanyDto:
    return MillCompanyDto(
        id=e.id,
        party_id=e.party_id,
        company_code=e.company_code,
        company_name=e.company_name,
        contact_phone=e.contact_phone,
        address=e.address,
        status=e.status,
        created_at=format_utc_iso(e.created_at) or "",
    )


def mill_to_dto(e: MillEntity) -> MillDto:
    return MillDto(
        id=e.id,
        mill_company_id=e.mill_company_id,
        company_name=e.company_name,
        mill_code=e.mill_code,
        mill_name=e.mill_name,
        address=e.address,
        district=e.district,
        regency=e.regency,
        province=e.province,
        latitude=format_decimal(e.latitude, 6),
        longitude=format_decimal(e.longitude, 6),
        has_verified_coordinates=e.has_verified_coordinates,
        contact_phone=e.contact_phone,
        partnership_status=e.partnership_status,
        is_public=e.is_public,
        location_verified_at=format_utc_iso(e.location_verified_at),
        version=e.version,
        created_at=format_utc_iso(e.created_at) or "",
        updated_at=format_utc_iso(e.updated_at) or "",
    )


def vehicle_to_dto(e: VehicleEntity) -> VehicleDto:
    return VehicleDto(
        id=e.id,
        plate_number=e.plate_number,
        vehicle_type=e.vehicle_type,
        nominal_capacity_kg=format_decimal(e.nominal_capacity_kg, 3),
        status=e.status,
    )


def driver_to_dto(e: DriverEntity) -> DriverDto:
    return DriverDto(
        id=e.id,
        full_name=e.full_name,
        contact_phone=e.contact_phone,
        driver_reference=e.driver_reference,
        status=e.status,
    )
