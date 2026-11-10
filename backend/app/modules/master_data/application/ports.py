"""Persistence and cache-invalidation ports for Master Data (ADR-002)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from app.modules.master_data.domain.entities import (
    CooperativeEntity,
    DriverEntity,
    EntityStatus,
    FarmEntity,
    FarmerEntity,
    MillCompanyEntity,
    MillEntity,
    VehicleEntity,
)


class MasterDataRepositoryPort(Protocol):
    """Async PostgreSQL persistence contract for Master Data."""

    async def get_cooperative_by_id(self, cooperative_id: UUID) -> CooperativeEntity | None: ...

    async def list_cooperatives(
        self,
        *,
        allowed_coop_ids: set[UUID] | None,
        page: int,
        page_size: int,
    ) -> tuple[list[CooperativeEntity], int]: ...

    async def get_farmer_by_id(self, farmer_id: UUID) -> FarmerEntity | None: ...

    async def list_farmers(
        self,
        *,
        allowed_farmer_ids: set[UUID] | None,
        allowed_coop_ids: set[UUID] | None,
        page: int,
        page_size: int,
        query: str | None,
        status: EntityStatus | None,
    ) -> tuple[list[FarmerEntity], int]: ...

    async def create_farmer(
        self,
        *,
        farmer_code: str,
        full_name: str,
        contact_phone: str,
        cooperative_id: UUID,
        membership_number: str | None,
        actor_id: UUID,
        now: datetime,
    ) -> FarmerEntity: ...

    async def update_farmer(
        self,
        *,
        farmer_id: UUID,
        expected_version: int,
        full_name: str | None,
        contact_phone: str | None,
        status: EntityStatus | None,
        reason: str | None,
        actor_id: UUID,
        now: datetime,
    ) -> FarmerEntity: ...

    async def get_farm_by_id(self, farm_id: UUID) -> FarmEntity | None: ...

    async def list_farms(
        self,
        *,
        allowed_farmer_ids: set[UUID] | None,
        allowed_coop_ids: set[UUID] | None,
        farmer_id_filter: UUID | None,
        page: int,
        page_size: int,
    ) -> tuple[list[FarmEntity], int]: ...

    async def create_farm(
        self,
        *,
        farmer_id: UUID,
        farm_code: str,
        farm_name: str,
        area_hectares: Decimal,
        planting_year: int | None,
        stdb_number: str | None,
        village: str,
        district: str,
        latitude: Decimal | None,
        longitude: Decimal | None,
        actor_id: UUID,
        now: datetime,
    ) -> FarmEntity: ...

    async def update_farm(
        self,
        *,
        farm_id: UUID,
        expected_version: int,
        farm_name: str | None,
        area_hectares: Decimal | None,
        planting_year: int | None,
        update_planting_year: bool,
        stdb_number: str | None,
        update_stdb_number: bool,
        village: str | None,
        district: str | None,
        latitude: Decimal | None,
        longitude: Decimal | None,
        update_coordinates: bool,
        actor_id: UUID,
        now: datetime,
    ) -> FarmEntity: ...

    async def list_mill_companies(
        self, *, page: int, page_size: int
    ) -> tuple[list[MillCompanyEntity], int]: ...

    async def create_mill_company(
        self,
        *,
        company_code: str,
        company_name: str,
        contact_phone: str,
        address: str,
        actor_id: UUID,
        now: datetime,
    ) -> MillCompanyEntity: ...

    async def get_mill_by_id(self, mill_id: UUID) -> MillEntity | None: ...

    async def list_mills(
        self,
        *,
        allowed_mill_ids: set[UUID] | None,
        page: int,
        page_size: int,
        query: str | None,
    ) -> tuple[list[MillEntity], int]: ...

    async def create_mill(
        self,
        *,
        mill_company_id: UUID,
        mill_code: str,
        mill_name: str,
        address: str,
        district: str,
        regency: str,
        province: str,
        latitude: Decimal | None,
        longitude: Decimal | None,
        contact_phone: str | None,
        partnership_status: EntityStatus,
        is_public: bool,
        actor_id: UUID,
        now: datetime,
    ) -> MillEntity: ...

    async def update_mill(
        self,
        *,
        mill_id: UUID,
        expected_version: int,
        mill_name: str | None,
        address: str | None,
        district: str | None,
        regency: str | None,
        latitude: Decimal | None,
        longitude: Decimal | None,
        update_coordinates: bool,
        contact_phone: str | None,
        update_contact_phone: bool,
        partnership_status: EntityStatus | None,
        is_public: bool | None,
        actor_id: UUID,
        now: datetime,
    ) -> MillEntity: ...

    async def list_vehicles(
        self, *, page: int, page_size: int
    ) -> tuple[list[VehicleEntity], int]: ...

    async def create_vehicle(
        self,
        *,
        plate_number: str,
        vehicle_type: str,
        nominal_capacity_kg: Decimal | None,
        actor_id: UUID,
        now: datetime,
    ) -> VehicleEntity: ...

    async def list_drivers(
        self, *, page: int, page_size: int
    ) -> tuple[list[DriverEntity], int]: ...

    async def create_driver(
        self,
        *,
        full_name: str,
        contact_phone: str,
        driver_reference: str | None,
        actor_id: UUID,
        now: datetime,
    ) -> DriverEntity: ...


class PublicDirectoryCacheInvalidatorPort(Protocol):
    """Post-commit Redis cache invalidation contract for public mill profiles."""

    async def invalidate_public_mills(self, mill_id: UUID | None = None) -> None: ...
