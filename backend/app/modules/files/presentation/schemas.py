"""Strict OpenAPI 3.1.0 DTOs for /api/v1/files* endpoints."""

from __future__ import annotations

from typing import Literal

from app.core.logging import format_utc_iso
from app.core.schemas import StrictContractModel
from app.modules.files.domain.entities import FileAssetEntity, FileClassification


class FileAssetDto(StrictContractModel):
    id: str
    original_filename: str
    mime_type: Literal["application/pdf", "image/jpeg", "image/png"]
    size_bytes: int
    checksum: str
    classification: FileClassification
    uploaded_by: str
    created_at: str


class FileAssetEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: FileAssetDto
    meta: None = None
    request_id: str


def file_asset_to_dto(entity: FileAssetEntity) -> FileAssetDto:
    return FileAssetDto(
        id=str(entity.id),
        original_filename=entity.original_filename,
        mime_type=entity.mime_type,  # type: ignore[arg-type]
        size_bytes=entity.size_bytes,
        checksum=entity.checksum,
        classification=entity.classification,
        uploaded_by=str(entity.uploaded_by),
        created_at=format_utc_iso(entity.created_at) or "",
    )
