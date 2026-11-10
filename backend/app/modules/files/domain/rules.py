"""Pure MIME magic-byte inspection, size guard, and filename sanitization (TRD §13.6)."""

from __future__ import annotations

import hashlib
import ntpath
import posixpath
import re

from app.core.exceptions import AppError, ErrorCode

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MiB per OpenAPI FileAsset schema

_ALLOWED_MIME_TYPES: dict[str, tuple[str, ...]] = {
    "application/pdf": (".pdf",),
    "image/jpeg": (".jpg", ".jpeg"),
    "image/png": (".png",),
}
_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def detect_verified_mime(content: bytes, declared_mime: str | None) -> str:
    """Verify binary magic signature independently from client headers."""
    if not content or len(content) > MAX_UPLOAD_BYTES:
        raise AppError(
            ErrorCode.VAL_INVALID_FORMAT,
            details=[
                {
                    "field": "file",
                    "reason": "Ukuran berkas harus antara 1 byte dan 10 MiB.",
                    "code": ErrorCode.VAL_INVALID_FORMAT.value,
                }
            ],
        )

    detected: str | None = None
    if content.startswith(b"%PDF-"):
        detected = "application/pdf"
    elif content.startswith(b"\xff\xd8\xff"):
        detected = "image/jpeg"
    elif content.startswith(b"\x89PNG\r\n\x1a\n"):
        detected = "image/png"

    if detected is None or detected not in _ALLOWED_MIME_TYPES:
        raise AppError(
            ErrorCode.VAL_INVALID_FORMAT,
            details=[
                {
                    "field": "file",
                    "reason": "Hanya PDF, JPEG, dan PNG valid yang diizinkan.",
                    "code": ErrorCode.VAL_INVALID_FORMAT.value,
                }
            ],
        )
    if declared_mime and declared_mime.strip().lower() not in (
        detected,
        "application/octet-stream",
    ):
        if detected == "image/jpeg" and declared_mime.strip().lower() == "image/jpg":
            return detected
        raise AppError(
            ErrorCode.VAL_INVALID_FORMAT,
            details=[
                {
                    "field": "file",
                    "reason": "Tipe konten berkas tidak cocok dengan tanda tangan biner berkas.",
                    "code": ErrorCode.VAL_INVALID_FORMAT.value,
                }
            ],
        )
    return detected


def sanitize_filename(raw_name: str | None) -> str:
    """Strip directory traversal tokens and normalize safe basename."""
    base = posixpath.basename(ntpath.basename((raw_name or "evidence.bin").strip()))
    cleaned = _SAFE_NAME_RE.sub("_", base).strip("._")
    if not cleaned:
        return "evidence.bin"
    return cleaned[:120]


def compute_sha256_hex(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def safe_extension_for_mime(mime_type: str) -> str:
    return _ALLOWED_MIME_TYPES[mime_type][0]
