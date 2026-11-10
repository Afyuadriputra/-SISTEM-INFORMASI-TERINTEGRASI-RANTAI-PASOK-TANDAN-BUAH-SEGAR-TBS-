"""In-process non-transactional CCTV Digital observability tracker (TRD §14, AFD ADM)."""

from __future__ import annotations

from collections import deque
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import Lock

last_error_code_ctx: ContextVar[str | None] = ContextVar("last_error_code", default=None)

_MAX_CORRELATIONS = 200
_WINDOW = timedelta(hours=24)


@dataclass(frozen=True, slots=True)
class ServerErrorCorrelation:
    request_id: str
    trace_id: str
    route: str
    status_code: int
    error_code: str
    module: str
    occurred_at: datetime


def derive_module_from_route(route: str) -> str:
    """Derive canonical domain module label from API path without exposing PII."""
    parts = [p for p in route.strip("/").split("/") if p]
    if parts and parts[0] == "health":
        return "infrastructure"
    if len(parts) >= 3 and parts[0] == "api" and parts[1] == "v1":
        seg = parts[2]
        if seg == "admin" and len(parts) >= 4:
            return f"admin.{parts[3]}"
        return seg
    return "core"


class ObservabilityTracker:
    """Thread-safe bounded 24h rolling tracker for HTTP request count & 5xx error correlations."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._request_times: deque[datetime] = deque()
        self._error_events: deque[ServerErrorCorrelation] = deque(maxlen=_MAX_CORRELATIONS)

    def _prune(self, now: datetime) -> None:
        cutoff = now - _WINDOW
        while self._request_times and self._request_times[0] < cutoff:
            self._request_times.popleft()
        while self._error_events and self._error_events[0].occurred_at < cutoff:
            self._error_events.popleft()

    def record_completion(
        self,
        *,
        request_id: str,
        trace_id: str,
        route: str,
        status_code: int,
        error_code: str | None,
        occurred_at: datetime | None = None,
    ) -> None:
        now = occurred_at or datetime.now(UTC)
        with self._lock:
            self._prune(now)
            self._request_times.append(now)
            if status_code >= 500:
                self._error_events.append(
                    ServerErrorCorrelation(
                        request_id=request_id,
                        trace_id=trace_id,
                        route=route,
                        status_code=status_code,
                        error_code=error_code or "SYS_INTERNAL_ERROR",
                        module=derive_module_from_route(route),
                        occurred_at=now,
                    )
                )

    def snapshot_24h(self) -> tuple[int, int, list[ServerErrorCorrelation]]:
        now = datetime.now(UTC)
        with self._lock:
            self._prune(now)
            total = len(self._request_times)
            errors = list(reversed(self._error_events))
            return total, len(errors), errors[:20]
