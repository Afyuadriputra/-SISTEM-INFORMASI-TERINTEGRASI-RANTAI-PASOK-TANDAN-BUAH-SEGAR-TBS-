"""Path-traversal-safe non-public local filesystem storage backend for evidence files."""

from __future__ import annotations

import asyncio
from pathlib import Path

from app.core.exceptions import AppError, ErrorCode


class LocalEvidenceStorageAdapter:
    """Stores evidence files strictly beneath configured non-public directory."""

    def __init__(self, base_dir: str) -> None:
        self._base_dir = Path(base_dir).resolve()

    def _resolve_safe_path(self, storage_key: str) -> Path:
        if ".." in storage_key or storage_key.startswith(("/", "\\")):
            raise AppError(ErrorCode.VAL_INVALID_FORMAT)
        target = (self._base_dir / storage_key).resolve()
        if not target.is_relative_to(self._base_dir):
            raise AppError(ErrorCode.VAL_INVALID_FORMAT)
        return target

    async def save_bytes(self, *, storage_key: str, content: bytes) -> None:
        target = self._resolve_safe_path(storage_key)

        def _write() -> None:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)

        await asyncio.to_thread(_write)

    async def read_bytes(self, *, storage_key: str) -> bytes:
        target = self._resolve_safe_path(storage_key)

        def _read() -> bytes:
            if not target.is_file():
                raise AppError(ErrorCode.SYS_RESOURCE_NOT_FOUND)
            return target.read_bytes()

        return await asyncio.to_thread(_read)

    async def delete_best_effort(self, *, storage_key: str) -> None:
        target = self._resolve_safe_path(storage_key)

        def _unlink() -> None:
            target.unlink(missing_ok=True)

        await asyncio.to_thread(_unlink)
