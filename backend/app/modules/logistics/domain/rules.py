"""Pure domain invariants for e-DO SM-05 state machine, QR hashing, and cancellation guards."""

from __future__ import annotations

import hashlib
import secrets

from app.core.exceptions import AppError, ErrorCode
from app.modules.logistics.domain.entities import DeliveryOrderStatus


def generate_edo_qr_token_and_hash(*, delivery_order_number: str) -> tuple[str, str]:
    """Generate non-guessable e-DO verification token + SHA-256 digest stored in DB (DBD §11.5)."""
    suffix = secrets.token_hex(4).upper()
    token = f"{delivery_order_number}-{suffix}"
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return token, digest


def assert_can_issue_edo(
    *, current_status: DeliveryOrderStatus, expected_version: int, actual_version: int
) -> None:
    if actual_version != expected_version:
        raise AppError(
            ErrorCode.LOG_STALE_RECORD_VERSION,
            details={"current_version": actual_version},
        )
    if current_status != DeliveryOrderStatus.DRAFT:
        raise AppError(
            ErrorCode.LOG_INVALID_STATE_TRANSITION,
            details={
                "current_status": current_status.value,
                "requested_status": DeliveryOrderStatus.READY.value,
            },
        )


def assert_can_transition_edo(
    *,
    current_status: DeliveryOrderStatus,
    target_status: DeliveryOrderStatus,
    expected_version: int,
    actual_version: int,
    has_global_ops: bool,
) -> None:
    """Validate SM-05 transitions READY->IN_TRANSIT (Coop/Ops) and RECEIVED->COMPLETED (Ops)."""
    if actual_version != expected_version:
        raise AppError(
            ErrorCode.LOG_STALE_RECORD_VERSION,
            details={"current_version": actual_version},
        )

    allowed = (
        (DeliveryOrderStatus.READY, DeliveryOrderStatus.IN_TRANSIT),
        (DeliveryOrderStatus.RECEIVED, DeliveryOrderStatus.COMPLETED),
    )
    if (current_status, target_status) not in allowed:
        raise AppError(
            ErrorCode.LOG_INVALID_STATE_TRANSITION,
            details={
                "current_status": current_status.value,
                "requested_status": target_status.value,
            },
        )

    if target_status == DeliveryOrderStatus.COMPLETED and not has_global_ops:
        raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)


def assert_can_cancel_edo(
    *,
    current_status: DeliveryOrderStatus,
    expected_version: int,
    actual_version: int,
    has_global_ops: bool,
) -> None:
    """Block post-arrival cancellation; allow pre-transit by Coop and pre-arrival by Ops."""
    if actual_version != expected_version:
        raise AppError(
            ErrorCode.LOG_STALE_RECORD_VERSION,
            details={"current_version": actual_version},
        )
    if current_status in (
        DeliveryOrderStatus.ARRIVED,
        DeliveryOrderStatus.RECEIVED,
        DeliveryOrderStatus.COMPLETED,
        DeliveryOrderStatus.CANCELLED,
    ):
        raise AppError(
            ErrorCode.LOG_CANCELLATION_FORBIDDEN,
            details={"current_status": current_status.value},
        )
    if current_status == DeliveryOrderStatus.IN_TRANSIT and not has_global_ops:
        raise AppError(ErrorCode.AUTH_SCOPE_FORBIDDEN)
