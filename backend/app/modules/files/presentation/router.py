"""FastAPI endpoints for authorized Evidence File upload & download (/api/v1/files/*)."""

from __future__ import annotations

from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Request, Response, UploadFile, status

from app.core.logging import request_id_ctx
from app.modules.files.application.use_cases import FilesService
from app.modules.files.domain.entities import FileClassification
from app.modules.files.presentation.schemas import FileAssetEnvelope, file_asset_to_dto
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.presentation.dependencies import require_access

files_router = APIRouter(prefix="/api/v1/files", tags=["Files"])


def get_files_service(request: Request) -> FilesService:
    """Resolve FilesService wired in composition root."""
    return cast(FilesService, request.app.state.files_service)


@files_router.post(
    "",
    response_model=FileAssetEnvelope,
    status_code=status.HTTP_201_CREATED,
)
async def upload_evidence_metadata(
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.MILL_OPERATOR,
                ),
                required_permissions=("files.upload",),
            )
        ),
    ],
    service: Annotated[FilesService, Depends(get_files_service)],
    classification: Annotated[FileClassification, Form()],
    file: Annotated[UploadFile, File()],
) -> FileAssetEnvelope:
    content = await file.read()
    asset = await service.upload_evidence(
        principal=principal,
        classification=classification,
        filename=file.filename,
        declared_mime=file.content_type,
        content=content,
    )
    return FileAssetEnvelope(
        data=file_asset_to_dto(asset),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@files_router.get("/{file_id}")
async def download_evidence_file(
    file_id: UUID,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(
                    RoleCode.PERUMDA_OPERATIONS,
                    RoleCode.PERUMDA_FINANCE,
                    RoleCode.MILL_OPERATOR,
                    RoleCode.DIRECTOR,
                ),
                required_permissions=("files.read",),
            )
        ),
    ],
    service: Annotated[FilesService, Depends(get_files_service)],
) -> Response:
    asset, content = await service.download_evidence(principal=principal, file_id=file_id)
    return Response(
        content=content,
        media_type=asset.mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{asset.original_filename}"',
            "X-Content-Type-Options": "nosniff",
        },
    )
