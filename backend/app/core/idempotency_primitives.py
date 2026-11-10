"""Framework-agnostic idempotency primitives shared across Clean Architecture layers."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID

from app.core.exceptions import AppError, ErrorCode

_IDEMPOTENCY_KEY_RE = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")


@dataclass(frozen=True, slots=True)
class IdempotencyReservation:
    """Outcome of claiming or replaying a durable idempotency record."""

    record_id: UUID
    is_replay: bool
    response_reference: UUID | None = None
    response_payload: dict[str, Any] | None = None


class IdempotencySlotPort(Protocol):
    """Port enabling application services to claim and release idempotency slots."""

    async def reserve(
        self,
        *,
        actor_id: UUID,
        operation_key: str,
        idempotency_key: str,
        request_hash: str,
        ttl_hours: int = 24,
    ) -> IdempotencyReservation: ...

    async def release_on_error(self, *, record_id: UUID) -> None: ...


def validate_idempotency_key(raw_key: str | None) -> str:
    """Validate mandatory Idempotency-Key header against canonical OpenAPI pattern."""
    if raw_key is None or not raw_key.strip():
        raise AppError(
            ErrorCode.VAL_REQUIRED_FIELD,
            "Header Idempotency-Key wajib disertakan untuk operasi mutasi kritis ini.",
            details=[
                {
                    "field": "Idempotency-Key",
                    "reason": "Header Idempotency-Key wajib diisi.",
                    "code": ErrorCode.VAL_REQUIRED_FIELD.value,
                }
            ],
        )
    cleaned = raw_key.strip()
    if not _IDEMPOTENCY_KEY_RE.match(cleaned):
        raise AppError(
            ErrorCode.VAL_INVALID_FORMAT,
            "Format header Idempotency-Key tidak valid (8-128 karakter [A-Za-z0-9._:-]).",
            details=[
                {
                    "field": "Idempotency-Key",
                    "reason": "Gunakan 8-128 karakter [A-Za-z0-9._:-].",
                    "code": ErrorCode.VAL_INVALID_FORMAT.value,
                }
            ],
        )
    return cleaned


def compute_request_hash(payload: dict[str, Any]) -> str:
    """Compute canonical SHA-256 digest of request parameters and JSON body."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
