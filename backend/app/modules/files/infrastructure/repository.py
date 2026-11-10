"""PostgreSQL repository implementation for FileAsset metadata & access control."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.audit import AuditRecordInput, append_audit_event
from app.modules.files.domain.entities import FileAssetEntity, FileClassification
from app.modules.files.infrastructure.models import FileAssetModel


def _to_entity(row: FileAssetModel) -> FileAssetEntity:
    return FileAssetEntity(
        id=row.id,
        storage_provider=row.storage_provider,
        storage_key=row.storage_key,
        original_filename=row.original_filename,
        mime_type=row.mime_type,
        size_bytes=row.size_bytes,
        checksum=row.checksum,
        classification=FileClassification(row.classification),
        uploaded_by=row.uploaded_by,
        created_at=row.created_at,
    )


class SqlAlchemyFilesRepository:
    """PostgreSQL implementation of FilesRepositoryPort."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create_asset(
        self,
        *,
        asset_id: UUID,
        storage_provider: str,
        storage_key: str,
        original_filename: str,
        mime_type: str,
        size_bytes: int,
        checksum: str,
        classification: FileClassification,
        uploaded_by: UUID,
    ) -> FileAssetEntity:
        now = datetime.now(UTC)
        async with self._session_factory() as session:
            async with session.begin():
                model = FileAssetModel(
                    id=asset_id,
                    storage_provider=storage_provider,
                    storage_key=storage_key,
                    original_filename=original_filename,
                    mime_type=mime_type,
                    size_bytes=size_bytes,
                    checksum=checksum,
                    classification=classification.value,
                    uploaded_by=uploaded_by,
                    created_at=now,
                )
                session.add(model)
                append_audit_event(
                    session,
                    AuditRecordInput(
                        actor_id=uploaded_by,
                        event_type="FILE_ASSET_UPLOADED",
                        module="files",
                        resource_type="file_assets",
                        resource_id=str(asset_id),
                        previous_state=None,
                        new_state={
                            "classification": classification.value,
                            "mime_type": mime_type,
                            "size_bytes": size_bytes,
                            "checksum": checksum,
                        },
                        reason=None,
                    ),
                )
                return _to_entity(model)

    async def get_asset_by_id(self, file_id: UUID) -> FileAssetEntity | None:
        async with self._session_factory() as session:
            row = await session.get(FileAssetModel, file_id)
            return _to_entity(row) if row is not None else None

    async def can_mill_operator_access_file(
        self, *, file_id: UUID, actor_id: UUID, allowed_mill_ids: set[UUID]
    ) -> bool:
        from app.modules.mill_weighing.infrastructure.models import MillWeighingTicketModel

        async with self._session_factory() as session:
            row = await session.get(FileAssetModel, file_id)
            if row is None:
                return False
            if row.uploaded_by == actor_id:
                return True
            if not allowed_mill_ids:
                return False
            ticket = (
                await session.execute(
                    select(MillWeighingTicketModel.id).where(
                        MillWeighingTicketModel.proof_file_id == file_id,
                        MillWeighingTicketModel.mill_id.in_(allowed_mill_ids),
                    )
                )
            ).scalar_one_or_none()
            return ticket is not None
