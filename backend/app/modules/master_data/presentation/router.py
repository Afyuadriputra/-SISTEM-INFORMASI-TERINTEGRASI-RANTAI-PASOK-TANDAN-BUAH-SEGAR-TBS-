"""FastAPI endpoints for Master Data (farmers, farms, cooperatives, mills, vehicles, drivers)."""

from __future__ import annotations

from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status

from app.core.logging import request_id_ctx
from app.core.schemas import build_pagination_meta
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.presentation.dependencies import require_access
from app.modules.master_data.application.use_cases import MasterDataService
from app.modules.master_data.domain.entities import EntityStatus
from app.modules.master_data.presentation.schemas import (
    CooperativeListEnvelope,
    CreateDriverRequest,
    CreateFarmerRequest,
    CreateFarmRequest,
    CreateMillCompanyRequest,
    CreateMillRequest,
    CreateVehicleRequest,
    DriverEnvelope,
    DriverListEnvelope,
    FarmEnvelope,
    FarmerEnvelope,
    FarmerListEnvelope,
    FarmListEnvelope,
    MillCompanyEnvelope,
    MillCompanyListEnvelope,
    MillEnvelope,
    MillListEnvelope,
    UpdateFarmerRequest,
    UpdateFarmRequest,
    UpdateMillRequest,
    VehicleEnvelope,
    VehicleListEnvelope,
    cooperative_to_dto,
    driver_to_dto,
    farm_to_dto,
    farmer_to_dto,
    mill_company_to_dto,
    mill_to_dto,
    vehicle_to_dto,
)

master_data_router = APIRouter(prefix="/api/v1", tags=["Master Data"])


def get_master_data_service(request: Request) -> MasterDataService:
    """Resolve MasterDataService wired at the composition root."""
    return cast(MasterDataService, request.app.state.master_data_service)


@master_data_router.get("/farmers", response_model=FarmerListEnvelope)
async def list_farmers(
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.FARMER,
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("farmers.read",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    q: Annotated[str | None, Query(max_length=120)] = None,
    entity_status: Annotated[EntityStatus | None, Query(alias="status")] = None,
) -> FarmerListEnvelope:
    rows, total = await service.list_farmers(
        principal=principal, page=page, page_size=page_size, query=q, status=entity_status
    )
    return FarmerListEnvelope(
        data=[farmer_to_dto(r) for r in rows],
        meta=build_pagination_meta(page, page_size, total),
        request_id=request_id_ctx.get(),
    )


@master_data_router.post(
    "/farmers", response_model=FarmerEnvelope, status_code=status.HTTP_201_CREATED
)
async def create_farmer(
    payload: CreateFarmerRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.COOPERATIVE_OPERATOR, RoleCode.PERUMDA_OPERATIONS),
                required_permissions=("farmers.write",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
) -> FarmerEnvelope:
    created = await service.create_farmer(
        principal=principal,
        farmer_code=payload.farmer_code,
        full_name=payload.full_name,
        contact_phone=payload.contact_phone,
        cooperative_id=payload.cooperative_id,
        membership_number=payload.membership_number,
    )
    return FarmerEnvelope(
        data=farmer_to_dto(created),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@master_data_router.get("/farmers/{farmer_id}", response_model=FarmerEnvelope)
async def get_farmer(
    farmer_id: UUID,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.FARMER,
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("farmers.read",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
) -> FarmerEnvelope:
    farmer = await service.get_farmer(principal=principal, farmer_id=farmer_id)
    return FarmerEnvelope(
        data=farmer_to_dto(farmer),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@master_data_router.patch("/farmers/{farmer_id}", response_model=FarmerEnvelope)
async def update_farmer(
    farmer_id: UUID,
    payload: UpdateFarmerRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.COOPERATIVE_OPERATOR, RoleCode.PERUMDA_OPERATIONS),
                required_permissions=("farmers.write",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
) -> FarmerEnvelope:
    updated = await service.update_farmer(
        principal=principal,
        farmer_id=farmer_id,
        expected_version=payload.version,
        full_name=payload.full_name,
        contact_phone=payload.contact_phone,
        status=payload.status,
        reason=payload.reason,
    )
    return FarmerEnvelope(
        data=farmer_to_dto(updated),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@master_data_router.get("/farms", response_model=FarmListEnvelope)
async def list_farms(
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.FARMER,
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("farms.read",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    farmer_id: Annotated[UUID | None, Query()] = None,
) -> FarmListEnvelope:
    rows, total = await service.list_farms(
        principal=principal, farmer_id=farmer_id, page=page, page_size=page_size
    )
    return FarmListEnvelope(
        data=[farm_to_dto(r) for r in rows],
        meta=build_pagination_meta(page, page_size, total),
        request_id=request_id_ctx.get(),
    )


@master_data_router.post("/farms", response_model=FarmEnvelope, status_code=status.HTTP_201_CREATED)
async def create_farm(
    payload: CreateFarmRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.COOPERATIVE_OPERATOR, RoleCode.PERUMDA_OPERATIONS),
                required_permissions=("farms.write",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
) -> FarmEnvelope:
    created = await service.create_farm(
        principal=principal,
        farmer_id=payload.farmer_id,
        farm_code=payload.farm_code,
        farm_name=payload.farm_name,
        area_hectares_raw=payload.area_hectares,
        planting_year=payload.planting_year,
        stdb_number=payload.stdb_number,
        village=payload.village,
        district=payload.district,
        latitude_raw=payload.latitude,
        longitude_raw=payload.longitude,
    )
    return FarmEnvelope(
        data=farm_to_dto(created),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@master_data_router.patch("/farms/{farm_id}", response_model=FarmEnvelope)
async def update_farm(
    farm_id: UUID,
    payload: UpdateFarmRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.COOPERATIVE_OPERATOR, RoleCode.PERUMDA_OPERATIONS),
                required_permissions=("farms.write",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
) -> FarmEnvelope:
    fields = payload.model_fields_set
    updated = await service.update_farm(
        principal=principal,
        farm_id=farm_id,
        expected_version=payload.version,
        farm_name=payload.farm_name,
        area_hectares_raw=payload.area_hectares,
        planting_year=payload.planting_year,
        update_planting_year="planting_year" in fields,
        stdb_number=payload.stdb_number,
        update_stdb_number="stdb_number" in fields,
        village=payload.village,
        district=payload.district,
        latitude_raw=payload.latitude,
        longitude_raw=payload.longitude,
        lat_provided="latitude" in fields,
        lng_provided="longitude" in fields,
    )
    return FarmEnvelope(
        data=farm_to_dto(updated),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@master_data_router.get("/cooperatives", response_model=CooperativeListEnvelope)
async def list_cooperatives(
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("cooperatives.read",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> CooperativeListEnvelope:
    rows, total = await service.list_cooperatives(
        principal=principal, page=page, page_size=page_size
    )
    return CooperativeListEnvelope(
        data=[cooperative_to_dto(r) for r in rows],
        meta=build_pagination_meta(page, page_size, total),
        request_id=request_id_ctx.get(),
    )


@master_data_router.get("/mill-companies", response_model=MillCompanyListEnvelope)
async def list_mill_companies(
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS, RoleCode.DIRECTOR),
                required_permissions=("mills.read",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> MillCompanyListEnvelope:
    rows, total = await service.list_mill_companies(page=page, page_size=page_size)
    return MillCompanyListEnvelope(
        data=[mill_company_to_dto(r) for r in rows],
        meta=build_pagination_meta(page, page_size, total),
        request_id=request_id_ctx.get(),
    )


@master_data_router.post(
    "/mill-companies", response_model=MillCompanyEnvelope, status_code=status.HTTP_201_CREATED
)
async def create_mill_company(
    payload: CreateMillCompanyRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS,),
                required_permissions=("mills.write",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
) -> MillCompanyEnvelope:
    created = await service.create_mill_company(
        principal=principal,
        company_code=payload.company_code,
        company_name=payload.company_name,
        contact_phone=payload.contact_phone,
        address=payload.address,
    )
    return MillCompanyEnvelope(
        data=mill_company_to_dto(created),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@master_data_router.get("/mills", response_model=MillListEnvelope)
async def list_mills(
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.MILL_OPERATOR,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("mills.read",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    q: Annotated[str | None, Query(max_length=120)] = None,
) -> MillListEnvelope:
    rows, total = await service.list_mills(
        principal=principal, page=page, page_size=page_size, query=q
    )
    return MillListEnvelope(
        data=[mill_to_dto(r) for r in rows],
        meta=build_pagination_meta(page, page_size, total),
        request_id=request_id_ctx.get(),
    )


@master_data_router.post("/mills", response_model=MillEnvelope, status_code=status.HTTP_201_CREATED)
async def create_mill(
    payload: CreateMillRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS,),
                required_permissions=("mills.write",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
) -> MillEnvelope:
    created = await service.create_mill(
        principal=principal,
        mill_company_id=payload.mill_company_id,
        mill_code=payload.mill_code,
        mill_name=payload.mill_name,
        address=payload.address,
        district=payload.district,
        regency=payload.regency,
        province=payload.province,
        latitude_raw=payload.latitude,
        longitude_raw=payload.longitude,
        contact_phone=payload.contact_phone,
        partnership_status=payload.partnership_status,
        is_public=payload.is_public,
    )
    return MillEnvelope(
        data=mill_to_dto(created),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@master_data_router.get("/mills/{mill_id}", response_model=MillEnvelope)
async def get_mill(
    mill_id: UUID,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.MILL_OPERATOR,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("mills.read",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
) -> MillEnvelope:
    mill = await service.get_mill(principal=principal, mill_id=mill_id)
    return MillEnvelope(
        data=mill_to_dto(mill),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@master_data_router.patch("/mills/{mill_id}", response_model=MillEnvelope)
async def update_mill(
    mill_id: UUID,
    payload: UpdateMillRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.PERUMDA_OPERATIONS,),
                required_permissions=("mills.write",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
) -> MillEnvelope:
    fields = payload.model_fields_set
    updated = await service.update_mill(
        principal=principal,
        mill_id=mill_id,
        expected_version=payload.version,
        mill_name=payload.mill_name,
        address=payload.address,
        district=payload.district,
        regency=payload.regency,
        latitude_raw=payload.latitude,
        longitude_raw=payload.longitude,
        lat_provided="latitude" in fields,
        lng_provided="longitude" in fields,
        contact_phone=payload.contact_phone,
        contact_phone_provided="contact_phone" in fields,
        partnership_status=payload.partnership_status,
        is_public=payload.is_public,
    )
    return MillEnvelope(
        data=mill_to_dto(updated),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@master_data_router.get("/vehicles", response_model=VehicleListEnvelope)
async def list_vehicles(
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.COOPERATIVE_OPERATOR,
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.MILL_OPERATOR,
                ),
                required_permissions=("vehicles.read",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> VehicleListEnvelope:
    rows, total = await service.list_vehicles(page=page, page_size=page_size)
    return VehicleListEnvelope(
        data=[vehicle_to_dto(r) for r in rows],
        meta=build_pagination_meta(page, page_size, total),
        request_id=request_id_ctx.get(),
    )


@master_data_router.post(
    "/vehicles", response_model=VehicleEnvelope, status_code=status.HTTP_201_CREATED
)
async def create_vehicle(
    payload: CreateVehicleRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.COOPERATIVE_OPERATOR, RoleCode.PERUMDA_OPERATIONS),
                required_permissions=("vehicles.write",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
) -> VehicleEnvelope:
    created = await service.create_vehicle(
        principal=principal,
        plate_number=payload.plate_number,
        vehicle_type=payload.vehicle_type,
        nominal_capacity_kg_raw=payload.nominal_capacity_kg,
    )
    return VehicleEnvelope(
        data=vehicle_to_dto(created),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@master_data_router.get("/drivers", response_model=DriverListEnvelope)
async def list_drivers(
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.COOPERATIVE_OPERATOR, RoleCode.PERUMDA_OPERATIONS),
                required_permissions=("drivers.read",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> DriverListEnvelope:
    rows, total = await service.list_drivers(page=page, page_size=page_size)
    return DriverListEnvelope(
        data=[driver_to_dto(r) for r in rows],
        meta=build_pagination_meta(page, page_size, total),
        request_id=request_id_ctx.get(),
    )


@master_data_router.post(
    "/drivers", response_model=DriverEnvelope, status_code=status.HTTP_201_CREATED
)
async def create_driver(
    payload: CreateDriverRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.COOPERATIVE_OPERATOR, RoleCode.PERUMDA_OPERATIONS),
                required_permissions=("drivers.write",),
            )
        ),
    ],
    service: Annotated[MasterDataService, Depends(get_master_data_service)],
) -> DriverEnvelope:
    created = await service.create_driver(
        principal=principal,
        full_name=payload.full_name,
        contact_phone=payload.contact_phone,
        driver_reference=payload.driver_reference,
    )
    return DriverEnvelope(
        data=driver_to_dto(created),
        meta=None,
        request_id=request_id_ctx.get(),
    )
