"""HTTP exception mapping and OpenAPI ErrorResponse handlers for FastAPI."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import ERROR_CATALOG_DEFAULTS, AppError, ErrorCode
from app.core.logging import get_logger, request_id_ctx
from app.core.observability import last_error_code_ctx
from app.core.schemas import ErrorBody, ErrorResponse

logger = get_logger("app.core.errors")


def build_error_json_response(
    *,
    code: ErrorCode,
    status_code: int,
    message: str,
    details: dict[str, Any] | list[Any] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Serialize canonical ErrorResponse envelope with active X-Request-ID header."""
    if status_code >= 500:
        last_error_code_ctx.set(code.value)
    req_id = request_id_ctx.get()
    body = ErrorResponse(
        error=ErrorBody(code=code.value, message=message, details=details),
        request_id=req_id,
    )
    resp_headers = {"X-Request-ID": req_id}
    if headers:
        resp_headers.update(headers)
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(mode="json"),
        headers=resp_headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global OpenAPI-aligned error handlers without leaking internal internals."""

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "controlled_error",
            extra={
                "structured": {
                    "event": "error_occurred",
                    "error_code": exc.code.value,
                    "status_code": exc.status_code,
                    "method": request.method,
                    "route": request.url.path,
                }
            },
        )
        return build_error_json_response(
            code=exc.code,
            status_code=exc.status_code,
            message=exc.message,
            details=exc.details,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = []
        has_missing = False
        for err in exc.errors():
            loc_parts = [str(p) for p in err.get("loc", []) if p not in ("body", "query", "path")]
            field = ".".join(loc_parts) if loc_parts else "request"
            err_type = str(err.get("type", ""))
            if err_type == "missing":
                has_missing = True
            details.append(
                {
                    "field": field,
                    "reason": str(err.get("msg", "Input tidak valid.")),
                    "code": ErrorCode.VAL_REQUIRED_FIELD.value
                    if err_type == "missing"
                    else ErrorCode.VAL_INVALID_FORMAT.value,
                }
            )
        top_code = ErrorCode.VAL_REQUIRED_FIELD if has_missing else ErrorCode.VAL_INVALID_FORMAT
        _, msg = ERROR_CATALOG_DEFAULTS[top_code]
        return build_error_json_response(
            code=top_code,
            status_code=422,
            message=msg,
            details=details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        if exc.status_code == 404:
            code = ErrorCode.SYS_RESOURCE_NOT_FOUND
        elif exc.status_code == 401:
            code = ErrorCode.AUTH_REQUIRED
        elif exc.status_code == 403:
            code = ErrorCode.AUTH_ACCESS_DENIED
        elif exc.status_code == 429:
            code = ErrorCode.SYS_RATE_LIMIT_EXCEEDED
        elif exc.status_code == 503:
            code = ErrorCode.SYS_DEPENDENCY_UNAVAILABLE
        else:
            code = ErrorCode.VAL_INVALID_FORMAT
        _, msg = ERROR_CATALOG_DEFAULTS[code]
        return build_error_json_response(
            code=code,
            status_code=exc.status_code,
            message=msg,
            details=None,
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "unhandled_exception",
            extra={
                "structured": {
                    "event": "unhandled_exception",
                    "error_code": ErrorCode.SYS_INTERNAL_ERROR.value,
                    "error_class": exc.__class__.__name__,
                    "method": request.method,
                    "route": request.url.path,
                }
            },
        )
        default_status, default_msg = ERROR_CATALOG_DEFAULTS[ErrorCode.SYS_INTERNAL_ERROR]
        return build_error_json_response(
            code=ErrorCode.SYS_INTERNAL_ERROR,
            status_code=default_status,
            message=default_msg,
            details=None,
        )
