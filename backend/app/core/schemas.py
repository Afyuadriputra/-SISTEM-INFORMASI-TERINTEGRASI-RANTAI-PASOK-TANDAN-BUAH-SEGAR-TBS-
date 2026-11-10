"""Canonical OpenAPI 3.1.0 response envelopes, pagination, and health schemas."""

from __future__ import annotations

from decimal import Decimal
from math import ceil
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictContractModel(BaseModel):
    """Base response DTO rejecting undeclared fields to keep MSW/OpenAPI parity."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)


class SimpleSuccessMeta(StrictContractModel):
    data_freshness_at: str | None = None
    simulation_notice: str | None = None
    idempotency_replayed: bool | None = None


class PaginationMeta(StrictContractModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    has_next: bool
    has_prev: bool
    data_freshness_at: str | None = None
    simulation_notice: str | None = None


class ValidationErrorDetail(StrictContractModel):
    field: str
    reason: str
    code: str | None = None


class ErrorBody(StrictContractModel):
    code: str
    message: str
    details: dict[str, Any] | list[Any] | None = None


class ErrorResponse(StrictContractModel):
    success: Literal[False] = False
    error: ErrorBody
    request_id: str


class HealthDependencies(BaseModel):
    model_config = ConfigDict(extra="forbid")

    postgresql: Literal["up", "down"]
    redis: Literal["up", "down"]


class HealthStatus(StrictContractModel):
    status: Literal["ok", "degraded"]
    service: str
    checked_at: str
    dependencies: HealthDependencies | None = None


class HealthEnvelope(StrictContractModel):
    success: Literal[True] = True
    data: HealthStatus
    meta: dict[str, Any] | None = None
    request_id: str


def build_pagination_meta(
    page: int,
    page_size: int,
    total_items: int,
    *,
    data_freshness_at: str | None = None,
    simulation_notice: str | None = None,
) -> PaginationMeta:
    """Build canonical OpenAPI PaginationMeta without duplicating ceiling division."""
    total_pages = ceil(total_items / page_size) if total_items > 0 else 0
    return PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1 and total_pages > 0,
        data_freshness_at=data_freshness_at,
        simulation_notice=simulation_notice,
    )


def format_decimal(value: Decimal | None, places: int) -> str | None:
    """Serialize Decimal deterministically as fixed-scale string without float coercion."""
    if value is None:
        return None
    return f"{value:.{places}f}"
