"""Domain entities and enums for FileAsset (DBD §16.1)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class FileClassification(StrEnum):
    PRICE_EVIDENCE = "PRICE_EVIDENCE"
    MILL_TICKET_PROOF = "MILL_TICKET_PROOF"
    DISPUTE_EVIDENCE = "DISPUTE_EVIDENCE"
    PAYMENT_PROOF = "PAYMENT_PROOF"


@dataclass(frozen=True, slots=True)
class FileAssetEntity:
    id: UUID
    storage_provider: str
    storage_key: str
    original_filename: str
    mime_type: str
    size_bytes: int
    checksum: str
    classification: FileClassification
    uploaded_by: UUID
    created_at: datetime
