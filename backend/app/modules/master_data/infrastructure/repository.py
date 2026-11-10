"""Async PostgreSQL repository implementation for Master Data."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import joinedload, selectinload

from app.core.audit import AuditRecordInput, append_audit_event
from app.core.exceptions import AppError, ErrorCode
from app.modules.master_data.domain.entities import (
    CooperativeEntity,
    DriverEntity,
    EntityStatus,
    FarmEntity,
    FarmerEntity,
    MillCompanyEntity,
    MillEntity,
    PartyType,
    VehicleEntity,
    VerificationStatus,
)
from app.modules.master_data.infrastructure.models import (
    CooperativeMembershipModel,
    CooperativeModel,
    DriverModel,
    FarmerModel,
    FarmModel,
    MillCompanyModel,
    MillModel,
    PartyModel,
    VehicleModel,
)


def _active_membership(memberships: list[CooperativeMembershipModel]) -> CooperativeMembershipModel:
    active = [m for m in memberships if m.status == "ACTIVE" and m.ended_at is None]
    if active:
        return active[0]
    if memberships:
        return sorted(memberships, key=lambda m: m.joined_at, reverse=True)[0]
    raise AppError(ErrorCode.SYS_INTERNAL_ERROR, "Riwayat keanggotaan petani tidak konsisten.")


def _to_farmer_entity(row: FarmerModel) -> FarmerEntity:
    membership = _active_membership(row.memberships)
    return FarmerEntity(
        id=row.id,
        party_id=row.party_id,
        farmer_code=row.farmer_code,
        full_name=row.full_name,
        contact_phone=row.contact_phone,
        cooperative_id=membership.cooperative_id,
        membership_number=membership.membership_number,
        status=EntityStatus(row.status),
        version=row.version,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_farm_entity(row: FarmModel) -> FarmEntity:
    membership = _active_membership(row.farmer.memberships)
    return FarmEntity(
        id=row.id,
        farmer_id=row.farmer_id,
        cooperative_id=membership.cooperative_id,
        farm_code=row.farm_code,
        farm_name=row.farm_name,
        area_hectares=row.area_hectares,
        planting_year=row.planting_year,
        stdb_number=row.stdb_number,
        village=row.village,
        district=row.district,
        latitude=row.latitude,
        longitude=row.longitude,
        verification_status=VerificationStatus(row.verification_status),
        version=row.version,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_cooperative_entity(row: CooperativeModel) -> CooperativeEntity:
    return CooperativeEntity(
        id=row.id,
        party_id=row.party_id,
        cooperative_code=row.cooperative_code,
        cooperative_name=row.cooperative_name,
        address=row.address,
        contact_phone=row.contact_phone,
        status=EntityStatus(row.status),
    )


def _to_mill_company_entity(row: MillCompanyModel) -> MillCompanyEntity:
    return MillCompanyEntity(
        id=row.id,
        party_id=row.party_id,
        company_code=row.company_code,
        company_name=row.company_name,
        contact_phone=row.contact_phone,
        address=row.address,
        status=EntityStatus(row.status),
        created_at=row.created_at,
    )


def _to_mill_entity(row: MillModel) -> MillEntity:
    return MillEntity(
        id=row.id,
        mill_company_id=row.mill_company_id,
        company_name=row.mill_company.company_name,
        mill_code=row.mill_code,
        mill_name=row.mill_name,
        address=row.address,
        district=row.district,
        regency=row.regency,
        province=row.province,
        latitude=row.latitude,
        longitude=row.longitude,
        contact_phone=row.contact_phone,
        partnership_status=EntityStatus(row.partnership_status),
        is_public=row.is_public,
        location_verified_at=row.location_verified_at,
        version=row.version,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _duplicate_code_error(field: str, exc: IntegrityError) -> AppError:
    return AppError(
        ErrorCode.MD_DUPLICATE_CODE,
        details={"field": field},
    )


class SqlAlchemyMasterDataRepository:
    """Async PostgreSQL Master Data adapter preventing N+1 queries and lost updates."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

    async def get_cooperative_by_id(self, cooperative_id: UUID) -> CooperativeEntity | None:
        async with self._sf() as session:
            row = (
                await session.execute(
                    select(CooperativeModel).where(CooperativeModel.id == cooperative_id)
                )
            ).scalar_one_or_none()
            return _to_cooperative_entity(row) if row is not None else None

    async def list_cooperatives(
        self,
        *,
        allowed_coop_ids: set[UUID] | None,
        page: int,
        page_size: int,
    ) -> tuple[list[CooperativeEntity], int]:
        async with self._sf() as session:
            filters: list[Any] = []
            if allowed_coop_ids is not None:
                if not allowed_coop_ids:
                    return [], 0
                filters.append(CooperativeModel.id.in_(allowed_coop_ids))
            total = int(
                (
                    await session.execute(select(func.count(CooperativeModel.id)).where(*filters))
                ).scalar_one()
            )
            stmt = (
                select(CooperativeModel)
                .where(*filters)
                .order_by(CooperativeModel.cooperative_code.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return [_to_cooperative_entity(r) for r in rows], total

    async def get_farmer_by_id(self, farmer_id: UUID) -> FarmerEntity | None:
        async with self._sf() as session:
            stmt = (
                select(FarmerModel)
                .options(selectinload(FarmerModel.memberships))
                .where(FarmerModel.id == farmer_id)
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            return _to_farmer_entity(row) if row is not None else None

    async def list_farmers(
        self,
        *,
        allowed_farmer_ids: set[UUID] | None,
        allowed_coop_ids: set[UUID] | None,
        page: int,
        page_size: int,
        query: str | None,
        status: EntityStatus | None,
    ) -> tuple[list[FarmerEntity], int]:
        async with self._sf() as session:
            filters: list[Any] = []
            if allowed_farmer_ids is not None:
                if not allowed_farmer_ids:
                    return [], 0
                filters.append(FarmerModel.id.in_(allowed_farmer_ids))
            if allowed_coop_ids is not None:
                if not allowed_coop_ids:
                    return [], 0
                coop_subq = select(CooperativeMembershipModel.farmer_id).where(
                    CooperativeMembershipModel.cooperative_id.in_(allowed_coop_ids),
                    CooperativeMembershipModel.status == "ACTIVE",
                    CooperativeMembershipModel.ended_at.is_(None),
                )
                filters.append(FarmerModel.id.in_(coop_subq))
            if query and query.strip():
                pat = f"%{query.strip()}%"
                filters.append(
                    or_(FarmerModel.farmer_code.ilike(pat), FarmerModel.full_name.ilike(pat))
                )
            if status is not None:
                filters.append(FarmerModel.status == status.value)

            total = int(
                (
                    await session.execute(select(func.count(FarmerModel.id)).where(*filters))
                ).scalar_one()
            )
            stmt = (
                select(FarmerModel)
                .options(selectinload(FarmerModel.memberships))
                .where(*filters)
                .order_by(FarmerModel.farmer_code.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return [_to_farmer_entity(r) for r in rows], total

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
    ) -> FarmerEntity:
        party_id = uuid4()
        farmer_id = uuid4()
        try:
            async with self._sf() as session:
                async with session.begin():
                    session.add(
                        PartyModel(
                            id=party_id,
                            party_type=PartyType.FARMER.value,
                            display_name=full_name,
                            status=EntityStatus.ACTIVE.value,
                            created_at=now,
                            updated_at=now,
                        )
                    )
                    await session.flush()
                    session.add(
                        FarmerModel(
                            id=farmer_id,
                            party_id=party_id,
                            farmer_code=farmer_code,
                            full_name=full_name,
                            contact_phone=contact_phone,
                            identity_reference=None,
                            status=EntityStatus.ACTIVE.value,
                            version=1,
                            created_at=now,
                            updated_at=now,
                        )
                    )
                    await session.flush()
                    session.add(
                        CooperativeMembershipModel(
                            id=uuid4(),
                            cooperative_id=cooperative_id,
                            farmer_id=farmer_id,
                            membership_number=membership_number,
                            joined_at=now,
                            ended_at=None,
                            status=EntityStatus.ACTIVE.value,
                        )
                    )
                    append_audit_event(
                        session,
                        AuditRecordInput(
                            actor_id=actor_id,
                            event_type="FARMER_CREATED",
                            module="master_data",
                            resource_type="farmers",
                            resource_id=str(farmer_id),
                            new_state={
                                "farmer_code": farmer_code,
                                "cooperative_id": str(cooperative_id),
                            },
                            occurred_at=now,
                        ),
                    )
        except IntegrityError as exc:
            raise _duplicate_code_error("farmer_code", exc) from exc

        created = await self.get_farmer_by_id(farmer_id)
        if created is None:
            raise AppError(ErrorCode.SYS_INTERNAL_ERROR)
        return created

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
    ) -> FarmerEntity:
        async with self._sf() as session:
            async with session.begin():
                row = (
                    await session.execute(
                        select(FarmerModel)
                        .options(selectinload(FarmerModel.memberships))
                        .where(FarmerModel.id == farmer_id)
                        .with_for_update()
                    )
                ).scalar_one_or_none()
                if row is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                if row.version != expected_version:
                    raise AppError(
                        ErrorCode.MD_STALE_RECORD_VERSION,
                        details={
                            "expected_version": expected_version,
                            "current_version": row.version,
                        },
                    )
                prev = {
                    "full_name": row.full_name,
                    "status": row.status,
                    "version": row.version,
                }
                if full_name is not None:
                    row.full_name = full_name
                if contact_phone is not None:
                    row.contact_phone = contact_phone
                if status is not None:
                    row.status = status.value
                row.version += 1
                row.updated_at = now
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="FARMER_UPDATED",
                        module="master_data",
                        resource_type="farmers",
                        resource_id=str(farmer_id),
                        previous_state=prev,
                        new_state={
                            "full_name": row.full_name,
                            "status": row.status,
                            "version": row.version,
                        },
                        reason=reason,
                        occurred_at=now,
                    ),
                )
        updated = await self.get_farmer_by_id(farmer_id)
        if updated is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        return updated

    async def get_farm_by_id(self, farm_id: UUID) -> FarmEntity | None:
        async with self._sf() as session:
            stmt = (
                select(FarmModel)
                .options(joinedload(FarmModel.farmer).selectinload(FarmerModel.memberships))
                .where(FarmModel.id == farm_id)
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            return _to_farm_entity(row) if row is not None else None

    async def list_farms(
        self,
        *,
        allowed_farmer_ids: set[UUID] | None,
        allowed_coop_ids: set[UUID] | None,
        farmer_id_filter: UUID | None,
        page: int,
        page_size: int,
    ) -> tuple[list[FarmEntity], int]:
        async with self._sf() as session:
            filters: list[Any] = []
            if allowed_farmer_ids is not None:
                if not allowed_farmer_ids:
                    return [], 0
                filters.append(FarmModel.farmer_id.in_(allowed_farmer_ids))
            if allowed_coop_ids is not None:
                if not allowed_coop_ids:
                    return [], 0
                coop_subq = select(CooperativeMembershipModel.farmer_id).where(
                    CooperativeMembershipModel.cooperative_id.in_(allowed_coop_ids),
                    CooperativeMembershipModel.status == "ACTIVE",
                    CooperativeMembershipModel.ended_at.is_(None),
                )
                filters.append(FarmModel.farmer_id.in_(coop_subq))
            if farmer_id_filter is not None:
                filters.append(FarmModel.farmer_id == farmer_id_filter)

            total = int(
                (
                    await session.execute(select(func.count(FarmModel.id)).where(*filters))
                ).scalar_one()
            )
            stmt = (
                select(FarmModel)
                .options(joinedload(FarmModel.farmer).selectinload(FarmerModel.memberships))
                .where(*filters)
                .order_by(FarmModel.farm_code.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return [_to_farm_entity(r) for r in rows], total

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
    ) -> FarmEntity:
        farm_id = uuid4()
        ver_status = (
            VerificationStatus.VERIFIED.value
            if latitude is not None and longitude is not None
            else VerificationStatus.UNVERIFIED.value
        )
        try:
            async with self._sf() as session:
                async with session.begin():
                    session.add(
                        FarmModel(
                            id=farm_id,
                            farmer_id=farmer_id,
                            farm_code=farm_code,
                            farm_name=farm_name,
                            area_hectares=area_hectares,
                            planting_year=planting_year,
                            stdb_number=stdb_number,
                            village=village,
                            district=district,
                            latitude=latitude,
                            longitude=longitude,
                            verification_status=ver_status,
                            version=1,
                            created_at=now,
                            updated_at=now,
                        )
                    )
                    append_audit_event(
                        session,
                        AuditRecordInput(
                            actor_id=actor_id,
                            event_type="FARM_CREATED",
                            module="master_data",
                            resource_type="farms",
                            resource_id=str(farm_id),
                            new_state={"farm_code": farm_code, "farmer_id": str(farmer_id)},
                            occurred_at=now,
                        ),
                    )
        except IntegrityError as exc:
            raise _duplicate_code_error("farm_code", exc) from exc

        created = await self.get_farm_by_id(farm_id)
        if created is None:
            raise AppError(ErrorCode.SYS_INTERNAL_ERROR)
        return created

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
    ) -> FarmEntity:
        async with self._sf() as session:
            async with session.begin():
                row = (
                    await session.execute(
                        select(FarmModel).where(FarmModel.id == farm_id).with_for_update()
                    )
                ).scalar_one_or_none()
                if row is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                if row.version != expected_version:
                    raise AppError(
                        ErrorCode.MD_STALE_RECORD_VERSION,
                        details={
                            "expected_version": expected_version,
                            "current_version": row.version,
                        },
                    )
                if farm_name is not None:
                    row.farm_name = farm_name
                if area_hectares is not None:
                    row.area_hectares = area_hectares
                if update_planting_year:
                    row.planting_year = planting_year
                if update_stdb_number:
                    row.stdb_number = stdb_number
                if village is not None:
                    row.village = village
                if district is not None:
                    row.district = district
                if update_coordinates:
                    row.latitude = latitude
                    row.longitude = longitude
                    row.verification_status = (
                        VerificationStatus.VERIFIED.value
                        if latitude is not None and longitude is not None
                        else VerificationStatus.UNVERIFIED.value
                    )
                row.version += 1
                row.updated_at = now
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="FARM_UPDATED",
                        module="master_data",
                        resource_type="farms",
                        resource_id=str(farm_id),
                        new_state={"version": row.version, "farm_name": row.farm_name},
                        occurred_at=now,
                    ),
                )
        updated = await self.get_farm_by_id(farm_id)
        if updated is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        return updated

    async def list_mill_companies(
        self, *, page: int, page_size: int
    ) -> tuple[list[MillCompanyEntity], int]:
        async with self._sf() as session:
            total = int(
                (await session.execute(select(func.count(MillCompanyModel.id)))).scalar_one()
            )
            stmt = (
                select(MillCompanyModel)
                .order_by(MillCompanyModel.company_code.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return [_to_mill_company_entity(r) for r in rows], total

    async def create_mill_company(
        self,
        *,
        company_code: str,
        company_name: str,
        contact_phone: str,
        address: str,
        actor_id: UUID,
        now: datetime,
    ) -> MillCompanyEntity:
        party_id = uuid4()
        comp_id = uuid4()
        try:
            async with self._sf() as session:
                async with session.begin():
                    session.add(
                        PartyModel(
                            id=party_id,
                            party_type=PartyType.MILL_COMPANY.value,
                            display_name=company_name,
                            status=EntityStatus.ACTIVE.value,
                            created_at=now,
                            updated_at=now,
                        )
                    )
                    await session.flush()
                    comp = MillCompanyModel(
                        id=comp_id,
                        party_id=party_id,
                        company_code=company_code,
                        company_name=company_name,
                        contact_phone=contact_phone,
                        address=address,
                        status=EntityStatus.ACTIVE.value,
                        created_at=now,
                        updated_at=now,
                    )
                    session.add(comp)
                    append_audit_event(
                        session,
                        AuditRecordInput(
                            actor_id=actor_id,
                            event_type="MILL_COMPANY_CREATED",
                            module="master_data",
                            resource_type="mill_companies",
                            resource_id=str(comp_id),
                            new_state={"company_code": company_code},
                            occurred_at=now,
                        ),
                    )
        except IntegrityError as exc:
            raise _duplicate_code_error("company_code", exc) from exc

        async with self._sf() as session:
            row = (
                await session.execute(
                    select(MillCompanyModel).where(MillCompanyModel.id == comp_id)
                )
            ).scalar_one()
            return _to_mill_company_entity(row)

    async def get_mill_by_id(self, mill_id: UUID) -> MillEntity | None:
        async with self._sf() as session:
            stmt = (
                select(MillModel)
                .options(joinedload(MillModel.mill_company))
                .where(MillModel.id == mill_id)
            )
            row = (await session.execute(stmt)).scalar_one_or_none()
            return _to_mill_entity(row) if row is not None else None

    async def list_mills(
        self,
        *,
        allowed_mill_ids: set[UUID] | None,
        page: int,
        page_size: int,
        query: str | None,
    ) -> tuple[list[MillEntity], int]:
        async with self._sf() as session:
            filters: list[Any] = []
            if allowed_mill_ids is not None:
                if not allowed_mill_ids:
                    return [], 0
                filters.append(MillModel.id.in_(allowed_mill_ids))
            if query and query.strip():
                pat = f"%{query.strip()}%"
                filters.append(
                    or_(
                        MillModel.mill_code.ilike(pat),
                        MillModel.mill_name.ilike(pat),
                        MillModel.regency.ilike(pat),
                    )
                )

            total = int(
                (
                    await session.execute(select(func.count(MillModel.id)).where(*filters))
                ).scalar_one()
            )
            stmt = (
                select(MillModel)
                .options(joinedload(MillModel.mill_company))
                .where(*filters)
                .order_by(MillModel.mill_code.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return [_to_mill_entity(r) for r in rows], total

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
    ) -> MillEntity:
        mill_id = uuid4()
        loc_verified = now if latitude is not None and longitude is not None else None
        try:
            async with self._sf() as session:
                async with session.begin():
                    comp = (
                        await session.execute(
                            select(MillCompanyModel).where(MillCompanyModel.id == mill_company_id)
                        )
                    ).scalar_one_or_none()
                    if comp is None:
                        raise AppError(
                            ErrorCode.SYS_RESOURCE_NOT_FOUND, "Perusahaan PKS tidak ditemukan."
                        )
                    session.add(
                        MillModel(
                            id=mill_id,
                            mill_company_id=mill_company_id,
                            mill_code=mill_code,
                            mill_name=mill_name,
                            address=address,
                            district=district,
                            regency=regency,
                            province=province,
                            latitude=latitude,
                            longitude=longitude,
                            contact_phone=contact_phone,
                            partnership_status=partnership_status.value,
                            is_public=is_public,
                            location_verified_at=loc_verified,
                            version=1,
                            created_at=now,
                            updated_at=now,
                        )
                    )
                    append_audit_event(
                        session,
                        AuditRecordInput(
                            actor_id=actor_id,
                            event_type="MILL_CREATED",
                            module="master_data",
                            resource_type="mills",
                            resource_id=str(mill_id),
                            new_state={"mill_code": mill_code, "is_public": is_public},
                            occurred_at=now,
                        ),
                    )
        except IntegrityError as exc:
            raise _duplicate_code_error("mill_code", exc) from exc

        created = await self.get_mill_by_id(mill_id)
        if created is None:
            raise AppError(ErrorCode.SYS_INTERNAL_ERROR)
        return created

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
    ) -> MillEntity:
        async with self._sf() as session:
            async with session.begin():
                row = (
                    await session.execute(
                        select(MillModel).where(MillModel.id == mill_id).with_for_update()
                    )
                ).scalar_one_or_none()
                if row is None:
                    raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
                if row.version != expected_version:
                    raise AppError(
                        ErrorCode.MD_STALE_RECORD_VERSION,
                        details={
                            "expected_version": expected_version,
                            "current_version": row.version,
                        },
                    )
                prev = {
                    "mill_name": row.mill_name,
                    "partnership_status": row.partnership_status,
                    "is_public": row.is_public,
                    "version": row.version,
                }
                if mill_name is not None:
                    row.mill_name = mill_name
                if address is not None:
                    row.address = address
                if district is not None:
                    row.district = district
                if regency is not None:
                    row.regency = regency
                if update_coordinates:
                    row.latitude = latitude
                    row.longitude = longitude
                    row.location_verified_at = (
                        now if latitude is not None and longitude is not None else None
                    )
                if update_contact_phone:
                    row.contact_phone = contact_phone
                if partnership_status is not None:
                    row.partnership_status = partnership_status.value
                if is_public is not None:
                    row.is_public = is_public
                row.version += 1
                row.updated_at = now
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="MILL_UPDATED",
                        module="master_data",
                        resource_type="mills",
                        resource_id=str(mill_id),
                        previous_state=prev,
                        new_state={
                            "mill_name": row.mill_name,
                            "partnership_status": row.partnership_status,
                            "is_public": row.is_public,
                            "version": row.version,
                        },
                        occurred_at=now,
                    ),
                )
        updated = await self.get_mill_by_id(mill_id)
        if updated is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
        return updated

    async def list_vehicles(self, *, page: int, page_size: int) -> tuple[list[VehicleEntity], int]:
        async with self._sf() as session:
            total = int((await session.execute(select(func.count(VehicleModel.id)))).scalar_one())
            stmt = (
                select(VehicleModel)
                .order_by(VehicleModel.plate_number.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return [
                VehicleEntity(
                    id=r.id,
                    plate_number=r.plate_number,
                    vehicle_type=r.vehicle_type,
                    nominal_capacity_kg=r.nominal_capacity_kg,
                    status=EntityStatus(r.status),
                )
                for r in rows
            ], total

    async def create_vehicle(
        self,
        *,
        plate_number: str,
        vehicle_type: str,
        nominal_capacity_kg: Decimal | None,
        actor_id: UUID,
        now: datetime,
    ) -> VehicleEntity:
        vid = uuid4()
        try:
            async with self._sf() as session:
                async with session.begin():
                    session.add(
                        VehicleModel(
                            id=vid,
                            plate_number=plate_number,
                            vehicle_type=vehicle_type,
                            nominal_capacity_kg=nominal_capacity_kg,
                            status=EntityStatus.ACTIVE.value,
                            created_at=now,
                            updated_at=now,
                        )
                    )
                    append_audit_event(
                        session,
                        AuditRecordInput(
                            actor_id=actor_id,
                            event_type="VEHICLE_CREATED",
                            module="master_data",
                            resource_type="vehicles",
                            resource_id=str(vid),
                            new_state={"plate_number": plate_number},
                            occurred_at=now,
                        ),
                    )
        except IntegrityError as exc:
            raise _duplicate_code_error("plate_number", exc) from exc

        async with self._sf() as session:
            r = (
                await session.execute(select(VehicleModel).where(VehicleModel.id == vid))
            ).scalar_one()
            return VehicleEntity(
                id=r.id,
                plate_number=r.plate_number,
                vehicle_type=r.vehicle_type,
                nominal_capacity_kg=r.nominal_capacity_kg,
                status=EntityStatus(r.status),
            )

    async def list_drivers(self, *, page: int, page_size: int) -> tuple[list[DriverEntity], int]:
        async with self._sf() as session:
            total = int((await session.execute(select(func.count(DriverModel.id)))).scalar_one())
            stmt = (
                select(DriverModel)
                .order_by(DriverModel.full_name.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return [
                DriverEntity(
                    id=r.id,
                    full_name=r.full_name,
                    contact_phone=r.contact_phone,
                    driver_reference=r.driver_reference,
                    status=EntityStatus(r.status),
                )
                for r in rows
            ], total

    async def create_driver(
        self,
        *,
        full_name: str,
        contact_phone: str,
        driver_reference: str | None,
        actor_id: UUID,
        now: datetime,
    ) -> DriverEntity:
        did = uuid4()
        async with self._sf() as session:
            async with session.begin():
                session.add(
                    DriverModel(
                        id=did,
                        full_name=full_name,
                        contact_phone=contact_phone,
                        driver_reference=driver_reference,
                        status=EntityStatus.ACTIVE.value,
                        created_at=now,
                        updated_at=now,
                    )
                )
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=actor_id,
                        event_type="DRIVER_CREATED",
                        module="master_data",
                        resource_type="drivers",
                        resource_id=str(did),
                        new_state={"driver_reference": driver_reference},
                        occurred_at=now,
                    ),
                )
        async with self._sf() as session:
            r = (
                await session.execute(select(DriverModel).where(DriverModel.id == did))
            ).scalar_one()
            return DriverEntity(
                id=r.id,
                full_name=r.full_name,
                contact_phone=r.contact_phone,
                driver_reference=r.driver_reference,
                status=EntityStatus(r.status),
            )
