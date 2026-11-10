"""HTTP observability, Request ID binding, security headers, and bounded timeout middleware."""

from __future__ import annotations

import asyncio
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.errors import build_error_json_response
from app.core.exceptions import ERROR_CATALOG_DEFAULTS, ErrorCode
from app.core.logging import actor_id_ctx, get_logger, request_id_ctx, trace_id_ctx
from app.core.observability import last_error_code_ctx
from app.core.security import (
    BASE_SECURITY_HEADERS,
    generate_trace_id,
    normalize_or_generate_request_id,
)

logger = get_logger("app.core.middleware")


class RequestContextAndAccessMiddleware(BaseHTTPMiddleware):
    """Attach X-Request-ID, enforce request timeout, emit CCTV Digital structured access logs."""

    def __init__(self, app, *, request_timeout_seconds: int = 15) -> None:
        super().__init__(app)
        self._timeout_seconds = request_timeout_seconds

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        req_id = normalize_or_generate_request_id(request.headers.get("X-Request-ID"))
        trace_id = generate_trace_id(request.headers.get("X-Trace-ID"))

        tok_req = request_id_ctx.set(req_id)
        tok_trace = trace_id_ctx.set(trace_id)
        tok_actor = actor_id_ctx.set(None)
        tok_err = last_error_code_ctx.set(None)

        started = time.perf_counter()
        status_code = 500
        try:
            async with asyncio.timeout(self._timeout_seconds):
                response = await call_next(request)
            status_code = response.status_code
        except TimeoutError:
            status_code = 504
            _, msg = ERROR_CATALOG_DEFAULTS[ErrorCode.SYS_REQUEST_TIMEOUT]
            response = build_error_json_response(
                code=ErrorCode.SYS_REQUEST_TIMEOUT,
                status_code=504,
                message=msg,
                details=None,
            )
            logger.error(
                "http_request_timeout",
                extra={
                    "structured": {
                        "event": "request_timeout",
                        "method": request.method,
                        "route": request.url.path,
                        "status_code": 504,
                        "timeout_seconds": self._timeout_seconds,
                    }
                },
            )
        finally:
            duration_ms = int((time.perf_counter() - started) * 1000)
            route_obj = request.scope.get("route")
            route_template = getattr(route_obj, "path", request.url.path)
            tracker = getattr(request.app.state, "observability", None)
            if tracker is not None:
                tracker.record_completion(
                    request_id=req_id,
                    trace_id=trace_id,
                    route=route_template,
                    status_code=status_code,
                    error_code=last_error_code_ctx.get(),
                )
            logger.info(
                "http_request_completed",
                extra={
                    "structured": {
                        "event": "http_request_completed",
                        "method": request.method,
                        "route": route_template,
                        "status_code": status_code,
                        "duration_ms": duration_ms,
                        "request_size": int(request.headers.get("content-length") or 0),
                    }
                },
            )
            request_id_ctx.reset(tok_req)
            trace_id_ctx.reset(tok_trace)
            actor_id_ctx.reset(tok_actor)
            last_error_code_ctx.reset(tok_err)

        response.headers["X-Request-ID"] = req_id
        for hdr_key, hdr_val in BASE_SECURITY_HEADERS.items():
            response.headers.setdefault(hdr_key, hdr_val)
        if not request.url.path.startswith("/api/v1/public/"):
            response.headers.setdefault("Cache-Control", "no-store")
        return response
