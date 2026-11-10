"""Reusable FastAPI authentication, CSRF, and RBAC dependencies for all internal modules."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Annotated, cast

from fastapi import Depends, Header, Request

from app.core.config import Settings
from app.core.exceptions import AppError, ErrorCode
from app.core.logging import actor_id_ctx
from app.modules.identity_access.application.use_cases import IdentityAccessService
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.domain.rules import assert_authorized


def get_identity_service(request: Request) -> IdentityAccessService:
    """Resolve IdentityAccessService wired in the composition root."""
    return cast(IdentityAccessService, request.app.state.identity_service)


def get_app_settings(request: Request) -> Settings:
    """Resolve runtime Settings stored on app.state."""
    return cast(Settings, request.app.state.settings)


def extract_session_cookie(request: Request, settings: Settings) -> str | None:
    """Read raw session cookie value without leaking it into logs."""
    return request.cookies.get(settings.SESSION_COOKIE_NAME)


def extract_client_ip(request: Request) -> str:
    """Determine client IP cleanly without trusting spoofed headers in unproxied dev mode."""
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


def validate_mutation_origin(request: Request, settings: Settings) -> None:
    """Verify Origin/Referer against allowed origins when Origin header is present (TRD §13.3)."""
    origin = request.headers.get("Origin")
    if not origin:
        return
    clean_origin = origin.rstrip("/")
    allowed = {o.rstrip("/") for o in settings.CORS_ALLOWED_ORIGINS}
    self_origin = f"{request.url.scheme}://{request.url.netloc}".rstrip("/")
    if clean_origin not in allowed and clean_origin != self_origin:
        raise AppError(ErrorCode.AUTH_CSRF_INVALID)


async def get_current_principal(
    request: Request,
    identity_service: Annotated[IdentityAccessService, Depends(get_identity_service)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> AuthenticatedPrincipal:
    """Resolve authenticated principal from server-side HttpOnly session cookie."""
    raw_token = extract_session_cookie(request, settings)
    principal = await identity_service.resolve_session(raw_token)
    actor_id_ctx.set(str(principal.user_id))
    return principal


def require_access(
    *,
    allowed_roles: tuple[RoleCode, ...] | None = None,
    required_permissions: tuple[str, ...] = (),
) -> Callable[..., Awaitable[AuthenticatedPrincipal]]:
    """Return dependency enforcing session auth, Origin+CSRF on mutations, and server RBAC."""

    async def _dependency(
        request: Request,
        principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
        identity_service: Annotated[IdentityAccessService, Depends(get_identity_service)],
        settings: Annotated[Settings, Depends(get_app_settings)],
        x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> AuthenticatedPrincipal:
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            validate_mutation_origin(request, settings)
            identity_service.verify_csrf(csrf_header=x_csrf_token, session_id=principal.session_id)
        assert_authorized(
            principal,
            allowed_roles=allowed_roles,
            required_permissions=required_permissions,
        )
        return principal

    return _dependency
