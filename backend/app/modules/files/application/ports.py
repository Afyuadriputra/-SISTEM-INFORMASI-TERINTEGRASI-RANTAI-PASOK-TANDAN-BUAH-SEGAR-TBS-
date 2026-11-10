"""Ports for evidence file binary storage and PostgreSQL metadata persistence."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.modules.files.domain.entities import FileAssetEntity, FileClassification


class FileStoragePort(Protocol):
    """Non-public binary storage backend (path traversal safe)."""

    async def save_bytes(self, *, storage_key: str, content: bytes) -> None: ...

    async def read_bytes(self, *, storage_key: str) -> bytes: ...

    async def delete_best_effort(self, *, storage_key: str) -> None: ...


class FilesRepositoryPort(Protocol):
    """PostgreSQL metadata & authorization lookup contract for file_assets."""

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
    ) -> FileAssetEntity: ...

    async def get_asset_by_id(self, file_id: UUID) -> FileAssetEntity | None: ...

    async def can_mill_operator_access_file(
        self, *, file_id: UUID, actor_id: UUID, allowed_mill_ids: set[UUID]
    ) -> bool: ...
