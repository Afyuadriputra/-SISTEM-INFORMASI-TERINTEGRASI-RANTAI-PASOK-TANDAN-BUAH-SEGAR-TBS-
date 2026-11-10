"""Core security constants, header hardening, and correlation token helpers."""

from __future__ import annotations

import hmac
import re
from uuid import uuid4

_VALID_REQUEST_ID_RE = re.compile(r"^req_[A-Za-z0-9._-]{2,76}$")

BASE_SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}


def normalize_or_generate_request_id(incoming_header: str | None) -> str:
    """Return incoming Request ID if valid OpenAPI pattern, else mint fresh req_<hex>."""
    if incoming_header:
        candidate = incoming_header.strip()
        if _VALID_REQUEST_ID_RE.match(candidate):
            return candidate
    return f"req_{uuid4().hex[:16]}"


def generate_trace_id(incoming_trace: str | None = None) -> str:
    """Return trace correlation token."""
    if incoming_trace:
        stripped = incoming_trace.strip()
        if 6 <= len(stripped) <= 80:
            return stripped
    return f"trace_{uuid4().hex[:16]}"


def constant_time_equals(expected: str, provided: str) -> bool:
    """Compare secrets/tokens in constant time."""
    return hmac.compare_digest(expected.encode("utf-8"), provided.encode("utf-8"))
