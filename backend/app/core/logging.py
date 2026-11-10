"""Structured JSON logging, request correlation context, and secret/PII redaction."""

from __future__ import annotations

import json
import logging
import re
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="req_startup")
trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="trace_startup")
actor_id_ctx: ContextVar[str | None] = ContextVar("actor_id", default=None)

REDACTED = "[REDACTED]"

SENSITIVE_KEYS = frozenset(
    {
        "password",
        "password_hash",
        "secret",
        "session_token",
        "token",
        "cookie",
        "set-cookie",
        "authorization",
        "x-csrf-token",
        "csrf_token",
        "bank_account",
        "account_number",
        "dsn",
        "database_url",
        "redis_url",
    }
)

_DSN_CRED_RE = re.compile(r"(postgresql(?:\+\w+)?|rediss?)://([^:@/\s]+):([^@/\s]+)@")


def sanitize_text(value: str) -> str:
    """Redact credentials embedded inside connection strings or bearer headers."""
    cleaned = _DSN_CRED_RE.sub(r"\1://\2:[REDACTED]@", value)
    cleaned = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._-]+", r"\1[REDACTED]", cleaned)
    return cleaned


def redact_mapping(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of payload with known sensitive keys masked."""
    sanitized: dict[str, Any] = {}
    for key, val in payload.items():
        if key.lower() in SENSITIVE_KEYS:
            sanitized[key] = REDACTED
        elif isinstance(val, dict):
            sanitized[key] = redact_mapping(val)
        elif isinstance(val, str):
            sanitized[key] = sanitize_text(val)
        else:
            sanitized[key] = val
    return sanitized


def format_utc_iso(dt: datetime | None) -> str | None:
    """Format an aware UTC datetime cleanly in canonical YYYY-MM-DDTHH:MM:SSZ form."""
    if dt is None:
        return None
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_now_iso() -> str:
    """Return canonical RFC 3339 UTC timestamp string ending in 'Z' (ADR-009)."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class JsonFormatter(logging.Formatter):
    """Format log records as single-line structured JSON with correlation fields."""

    _RESERVED_RECORD_FIELDS = frozenset(
        {
            "args",
            "asctime",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "message",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
            "taskName",
        }
    )

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": utc_now_iso(),
            "level": record.levelname,
            "logger": record.name,
            "message": sanitize_text(record.getMessage()),
            "request_id": request_id_ctx.get(),
            "trace_id": trace_id_ctx.get(),
        }
        actor = actor_id_ctx.get()
        if actor is not None:
            log_obj["actor_id"] = actor

        extra_fields = getattr(record, "structured", None)
        if isinstance(extra_fields, dict):
            log_obj.update(redact_mapping(extra_fields))

        if record.exc_info:
            log_obj["exception"] = sanitize_text(self.formatException(record.exc_info))

        return json.dumps(log_obj, ensure_ascii=False, default=str)


def configure_logging(level: str = "INFO", json_output: bool = True) -> None:
    """Configure root logger for structured JSON observability (TRD §14)."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    root_logger.handlers.clear()

    handler = logging.StreamHandler()
    if json_output:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    root_logger.addHandler(handler)

    for noisy in ("uvicorn.access",):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a module-scoped standard logger."""
    return logging.getLogger(name)
