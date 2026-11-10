"""Use cases for authorized evidence file upload and download."""

from __future__ import annotations

from uuid import UUID, uuid4

from app.core.exceptions import AppError, ErrorCode
from app.modules.files.application.ports import FilesRepositoryPort, FileStoragePort
from app.modules.files.domain.entities import FileAssetEntity, FileClassification
from app.modules.files.domain.rules import (
    compute_sha256_hex,
    detect_verified_mime,
    safe_extension_for_mime,
    sanitize_filename,
)
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.domain.rules import allowed_mill_ids, has_global_scope


class FilesService:
    """Manages non-public evidence file upload validation and authorized download."""

    def __init__(self, *, repo: FilesRepositoryPort, storage: FileStoragePort) -> None:
        self._repo = repo
        self._storage = storage

    async def upload_evidence(
        self,
        *,
        principal: AuthenticatedPrincipal,
        classification: FileClassification,
        filename: str | None,
        declared_mime: str | None,
        content: bytes,
    ) -> FileAssetEntity:
        mime_type = detect_verified_mime(content, declared_mime)
        safe_name = sanitize_filename(filename)
        checksum = compute_sha256_hex(content)
        asset_id = uuid4()
        ext = safe_extension_for_mime(mime_type)
        storage_key = f"{classification.value.lower()}/{asset_id}{ext}"

        await self._storage.save_bytes(storage_key=storage_key, content=content)
        try:
            return await self._repo.create_asset(
                asset_id=asset_id,
                storage_provider="LOCAL_DISK",
                storage_key=storage_key,
                original_filename=safe_name,
                mime_type=mime_type,
                size_bytes=len(content),
                checksum=checksum,
                classification=classification,
                uploaded_by=principal.user_id,
            )
        except Exception:
            await self._storage.delete_best_effort(storage_key=storage_key)
            raise

    async def download_evidence(
        self,
        *,
        principal: AuthenticatedPrincipal,
        file_id: UUID,
    ) -> tuple[FileAssetEntity, bytes]:
        asset = await self._repo.get_asset_by_id(file_id)
        if asset is None:
            raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)

        if not has_global_scope(principal):
            if RoleCode.MILL_OPERATOR in principal.roles:
                m_ids = allowed_mill_ids(principal)
                allowed = await self._repo.can_mill_operator_access_file(
                    file_id=file_id,
                    actor_id=principal.user_id,
                    allowed_mill_ids=m_ids,
                )
                if not allowed:
                    raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)
            else:
                raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)

        content = await self._storage.read_bytes(storage_key=asset.storage_key)
        return asset, content
