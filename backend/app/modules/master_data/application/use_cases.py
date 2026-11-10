"""Master Data use cases with strict scope isolation, optimistic locks, and cache safety."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.core.exceptions import AppError, ErrorCode
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.domain.rules import (
    allowed_cooperative_ids,
    allowed_farmer_ids,
    allowed_mill_ids,
    assert_cooperative_scope,
    assert_farmer_scope,
    assert_mill_scope,
    has_global_scope,
)
from app.modules.master_data.application.ports import (
    MasterDataRepositoryPort,
    PublicDirectoryCacheInvalidatorPort,
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
)
from app.modules.master_data.domain.rules import (
    normalize_plate_number,
    parse_area_hectares,
    parse_coordinate_pair,
    parse_nominal_capacity_kg,
)


def _scope_filters_for_farmer_data(
    principal: AuthenticatedPrincipal,
) -> tuple[set[UUID] | None, set[UUID] | None]:
    if has_global_scope(principal):
        return None, None
    if RoleCode.FARMER in principal.roles:
        return allowed_farmer_ids(principal), None
    if RoleCode.COOPERATIVE_OPERATOR in principal.roles:
        return None, allowed_cooperative_ids(principal)
    raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)


class MasterDataService:
    """Orchestrates CRUD, coordinate validation, versioning, and scope checks on Master Data."""

    def __init__(
        self,
        *,
        repo: MasterDataRepositoryPort,
        cache_invalidator: PublicDirectoryCacheInvalidatorPort,
    ) -> None:
        self._repo = repo
        self._cache = cache_invalidator

    async def list_farmers(
        self,
        *,
        principal: AuthenticatedPrincipal,
        page: int,
        page_size: int,
        query: str | None,
        status: EntityStatus | None,
    ) -> tuple[list[FarmerEntity], int]:
        f_ids, c_ids = _scope_filters_for_farmer_data(principal)
        return await self._repo.list_farmers(
            allowed_farmer_ids=f_ids,
            allowed_coop_ids=c_ids,
            page=page,
            page_size=page_size,
            query=query,
            status=status,
        )

    async def create_farmer(
        self,
        *,
        principal: AuthenticatedPrincipal,
        farmer_code: str,
        full_name: str,
        contact_phone: str,
        cooperative_id: UUID,
        membership_number: str | None,
    ) -> FarmerEntity:
        if not has_global_scope(principal):
            assert_cooperative_scope(principal, cooperative_id)
        coop = await self._repo.get_cooperative_by_id(cooperative_id)
        if coop is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND, "Koperasi tujuan tidak ditemukan.")
        return await self._repo.create_farmer(
            farmer_code=farmer_code.strip(),
            full_name=full_name.strip(),
            contact_phone=contact_phone.strip(),
            cooperative_id=cooperative_id,
            membership_number=membership_number.strip() if membership_number else None,
            actor_id=principal.user_id,
            now=datetime.now(UTC),
        )

    async def get_farmer(
        self, *, principal: AuthenticatedPrincipal, farmer_id: UUID
    ) -> FarmerEntity:
        farmer = await self._repo.get_farmer_by_id(farmer_id)
        if farmer is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        if not has_global_scope(principal):
            if RoleCode.FARMER in principal.roles:
                assert_farmer_scope(principal, farmer.id)
            else:
                assert_cooperative_scope(principal, farmer.cooperative_id)
        return farmer

    async def update_farmer(
        self,
        *,
        principal: AuthenticatedPrincipal,
        farmer_id: UUID,
        expected_version: int,
        full_name: str | None,
        contact_phone: str | None,
        status: EntityStatus | None,
        reason: str | None,
    ) -> FarmerEntity:
        existing = await self._repo.get_farmer_by_id(farmer_id)
        if existing is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        if not has_global_scope(principal):
            assert_cooperative_scope(principal, existing.cooperative_id)
        return await self._repo.update_farmer(
            farmer_id=farmer_id,
            expected_version=expected_version,
            full_name=full_name.strip() if full_name is not None else None,
            contact_phone=contact_phone.strip() if contact_phone is not None else None,
            status=status,
            reason=reason.strip() if reason is not None else None,
            actor_id=principal.user_id,
            now=datetime.now(UTC),
        )

    async def list_farms(
        self,
        *,
        principal: AuthenticatedPrincipal,
        farmer_id: UUID | None,
        page: int,
        page_size: int,
    ) -> tuple[list[FarmEntity], int]:
        f_ids, c_ids = _scope_filters_for_farmer_data(principal)
        if farmer_id is not None and not has_global_scope(principal):
            if f_ids is not None and farmer_id not in f_ids:
                raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)
            if c_ids is not None:
                farmer = await self._repo.get_farmer_by_id(farmer_id)
                if farmer is not None and farmer.cooperative_id not in c_ids:
                    raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)
        return await self._repo.list_farms(
            allowed_farmer_ids=f_ids,
            allowed_coop_ids=c_ids,
            farmer_id_filter=farmer_id,
            page=page,
            page_size=page_size,
        )

    async def create_farm(
        self,
        *,
        principal: AuthenticatedPrincipal,
        farmer_id: UUID,
        farm_code: str,
        farm_name: str,
        area_hectares_raw: str,
        planting_year: int | None,
        stdb_number: str | None,
        village: str,
        district: str,
        latitude_raw: str | None,
        longitude_raw: str | None,
    ) -> FarmEntity:
        farmer = await self._repo.get_farmer_by_id(farmer_id)
        if farmer is None:
            raise AppError(
                ErrorCode.SYS_RESOURCE_NOT_FOUND, "Petani pemilik kebun tidak ditemukan."
            )
        if not has_global_scope(principal):
            assert_cooperative_scope(principal, farmer.cooperative_id)

        area = parse_area_hectares(area_hectares_raw)
        lat, lng = parse_coordinate_pair(latitude_raw, longitude_raw)
        return await self._repo.create_farm(
            farmer_id=farmer_id,
            farm_code=farm_code.strip(),
            farm_name=farm_name.strip(),
            area_hectares=area,
            planting_year=planting_year,
            stdb_number=stdb_number.strip() if stdb_number else None,
            village=village.strip(),
            district=district.strip(),
            latitude=lat,
            longitude=lng,
            actor_id=principal.user_id,
            now=datetime.now(UTC),
        )

    async def update_farm(
        self,
        *,
        principal: AuthenticatedPrincipal,
        farm_id: UUID,
        expected_version: int,
        farm_name: str | None,
        area_hectares_raw: str | None,
        planting_year: int | None,
        update_planting_year: bool,
        stdb_number: str | None,
        update_stdb_number: bool,
        village: str | None,
        district: str | None,
        latitude_raw: str | None,
        longitude_raw: str | None,
        lat_provided: bool,
        lng_provided: bool,
    ) -> FarmEntity:
        existing = await self._repo.get_farm_by_id(farm_id)
        if existing is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        if not has_global_scope(principal):
            assert_cooperative_scope(principal, existing.cooperative_id)

        area = parse_area_hectares(area_hectares_raw) if area_hectares_raw is not None else None
        update_coords = lat_provided or lng_provided
        lat, lng = (None, None)
        if update_coords:
            if lat_provided != lng_provided:
                raise AppError(ErrorCode.VAL_INVALID_COORDINATES)
            lat, lng = parse_coordinate_pair(latitude_raw, longitude_raw)

        return await self._repo.update_farm(
            farm_id=farm_id,
            expected_version=expected_version,
            farm_name=farm_name.strip() if farm_name is not None else None,
            area_hectares=area,
            planting_year=planting_year,
            update_planting_year=update_planting_year,
            stdb_number=stdb_number.strip() if stdb_number else None,
            update_stdb_number=update_stdb_number,
            village=village.strip() if village is not None else None,
            district=district.strip() if district is not None else None,
            latitude=lat,
            longitude=lng,
            update_coordinates=update_coords,
            actor_id=principal.user_id,
            now=datetime.now(UTC),
        )

    async def list_cooperatives(
        self,
        *,
        principal: AuthenticatedPrincipal,
        page: int,
        page_size: int,
    ) -> tuple[list[CooperativeEntity], int]:
        c_ids = None if has_global_scope(principal) else allowed_cooperative_ids(principal)
        return await self._repo.list_cooperatives(
            allowed_coop_ids=c_ids, page=page, page_size=page_size
        )

    async def list_mill_companies(
        self, *, page: int, page_size: int
    ) -> tuple[list[MillCompanyEntity], int]:
        return await self._repo.list_mill_companies(page=page, page_size=page_size)

    async def create_mill_company(
        self,
        *,
        principal: AuthenticatedPrincipal,
        company_code: str,
        company_name: str,
        contact_phone: str,
        address: str,
    ) -> MillCompanyEntity:
        return await self._repo.create_mill_company(
            company_code=company_code.strip(),
            company_name=company_name.strip(),
            contact_phone=contact_phone.strip(),
            address=address.strip(),
            actor_id=principal.user_id,
            now=datetime.now(UTC),
        )

    async def list_mills(
        self,
        *,
        principal: AuthenticatedPrincipal,
        page: int,
        page_size: int,
        query: str | None,
    ) -> tuple[list[MillEntity], int]:
        m_ids = (
            allowed_mill_ids(principal)
            if (RoleCode.MILL_OPERATOR in principal.roles and not has_global_scope(principal))
            else None
        )
        return await self._repo.list_mills(
            allowed_mill_ids=m_ids, page=page, page_size=page_size, query=query
        )

    async def get_mill(self, *, principal: AuthenticatedPrincipal, mill_id: UUID) -> MillEntity:
        mill = await self._repo.get_mill_by_id(mill_id)
        if mill is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        if RoleCode.MILL_OPERATOR in principal.roles and not has_global_scope(principal):
            assert_mill_scope(principal, mill.id)
        return mill

    async def create_mill(
        self,
        *,
        principal: AuthenticatedPrincipal,
        mill_company_id: UUID,
        mill_code: str,
        mill_name: str,
        address: str,
        district: str,
        regency: str,
        province: str,
        latitude_raw: str | None,
        longitude_raw: str | None,
        contact_phone: str | None,
        partnership_status: EntityStatus,
        is_public: bool,
    ) -> MillEntity:
        lat, lng = parse_coordinate_pair(latitude_raw, longitude_raw)
        created = await self._repo.create_mill(
            mill_company_id=mill_company_id,
            mill_code=mill_code.strip(),
            mill_name=mill_name.strip(),
            address=address.strip(),
            district=district.strip(),
            regency=regency.strip(),
            province=province.strip(),
            latitude=lat,
            longitude=lng,
            contact_phone=contact_phone.strip() if contact_phone else None,
            partnership_status=partnership_status,
            is_public=is_public,
            actor_id=principal.user_id,
            now=datetime.now(UTC),
        )
        if created.is_public:
            await self._cache.invalidate_public_mills(created.id)
        return created

    async def update_mill(
        self,
        *,
        principal: AuthenticatedPrincipal,
        mill_id: UUID,
        expected_version: int,
        mill_name: str | None,
        address: str | None,
        district: str | None,
        regency: str | None,
        latitude_raw: str | None,
        longitude_raw: str | None,
        lat_provided: bool,
        lng_provided: bool,
        contact_phone: str | None,
        contact_phone_provided: bool,
        partnership_status: EntityStatus | None,
        is_public: bool | None,
    ) -> MillEntity:
        update_coords = lat_provided or lng_provided
        lat, lng = (None, None)
        if update_coords:
            if lat_provided != lng_provided:
                raise AppError(ErrorCode.VAL_INVALID_COORDINATES)
            lat, lng = parse_coordinate_pair(latitude_raw, longitude_raw)

        updated = await self._repo.update_mill(
            mill_id=mill_id,
            expected_version=expected_version,
            mill_name=mill_name.strip() if mill_name is not None else None,
            address=address.strip() if address is not None else None,
            district=district.strip() if district is not None else None,
            regency=regency.strip() if regency is not None else None,
            latitude=lat,
            longitude=lng,
            update_coordinates=update_coords,
            contact_phone=contact_phone.strip() if contact_phone else None,
            update_contact_phone=contact_phone_provided,
            partnership_status=partnership_status,
            is_public=is_public,
            actor_id=principal.user_id,
            now=datetime.now(UTC),
        )
        # Invalidate public directory cache whenever a public mill changes or visibility toggles.
        await self._cache.invalidate_public_mills(updated.id)
        return updated

    async def list_vehicles(self, *, page: int, page_size: int) -> tuple[list[VehicleEntity], int]:
        return await self._repo.list_vehicles(page=page, page_size=page_size)

    async def create_vehicle(
        self,
        *,
        principal: AuthenticatedPrincipal,
        plate_number: str,
        vehicle_type: str,
        nominal_capacity_kg_raw: str | None,
    ) -> VehicleEntity:
        normalized_plate = normalize_plate_number(plate_number)
        capacity = parse_nominal_capacity_kg(nominal_capacity_kg_raw)
        return await self._repo.create_vehicle(
            plate_number=normalized_plate,
            vehicle_type=vehicle_type.strip(),
            nominal_capacity_kg=capacity,
            actor_id=principal.user_id,
            now=datetime.now(UTC),
        )

    async def list_drivers(self, *, page: int, page_size: int) -> tuple[list[DriverEntity], int]:
        return await self._repo.list_drivers(page=page, page_size=page_size)

    async def create_driver(
        self,
        *,
        principal: AuthenticatedPrincipal,
        full_name: str,
        contact_phone: str,
        driver_reference: str | None,
    ) -> DriverEntity:
        return await self._repo.create_driver(
            full_name=full_name.strip(),
            contact_phone=contact_phone.strip(),
            driver_reference=driver_reference.strip() if driver_reference else None,
            actor_id=principal.user_id,
            now=datetime.now(UTC),
        )
