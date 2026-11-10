"""FastAPI endpoints for Authentication (/api/v1/auth/*) and Admin Users (/api/v1/admin/users*)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response, status

from app.core.config import Settings
from app.core.logging import request_id_ctx
from app.modules.identity_access.application.use_cases import IdentityAccessService
from app.modules.identity_access.domain.entities import AuthenticatedPrincipal, RoleCode
from app.modules.identity_access.presentation.dependencies import (
    extract_client_ip,
    extract_session_cookie,
    get_app_settings,
    get_identity_service,
    require_access,
)
from app.modules.identity_access.presentation.schemas import (
    AdminUserEnvelope,
    AdminUserListEnvelope,
    AuthUserEnvelope,
    CreateUserRequest,
    CsrfEnvelope,
    CsrfTokenData,
    LoginRequest,
    LogoutData,
    LogoutEnvelope,
    UpdateUserAccessRequest,
    admin_record_to_dto,
    build_pagination_meta,
    principal_to_dto,
)

auth_router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
admin_users_router = APIRouter(prefix="/api/v1/admin/users", tags=["Administration & Audit"])


@auth_router.get("/csrf", response_model=CsrfEnvelope)
async def get_csrf_token(
    request: Request,
    identity_service: Annotated[IdentityAccessService, Depends(get_identity_service)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> CsrfEnvelope:
    """Issue session-bound (or pre-auth) CSRF token (`getCsrfToken`)."""
    raw_token = extract_session_cookie(request, settings)
    csrf_token = await identity_service.issue_csrf(raw_token)
    return CsrfEnvelope(
        data=CsrfTokenData(csrf_token=csrf_token),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@auth_router.post("/login", response_model=AuthUserEnvelope)
async def login_user(
    payload: LoginRequest,
    request: Request,
    response: Response,
    identity_service: Annotated[IdentityAccessService, Depends(get_identity_service)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> AuthUserEnvelope:
    """Authenticate internal user, rotate session ID, set HttpOnly session cookie (`loginUser`)."""
    previous_cookie = extract_session_cookie(request, settings)
    result = await identity_service.login(
        username=payload.username,
        password=payload.password,
        client_ip=extract_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
        previous_raw_token=previous_cookie,
    )
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=result.raw_session_token,
        max_age=result.ttl_seconds,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        path="/",
    )
    return AuthUserEnvelope(
        data=principal_to_dto(result.principal),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@auth_router.post("/logout", response_model=LogoutEnvelope)
async def logout_user(
    request: Request,
    response: Response,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(require_access(required_permissions=("auth.session.read",))),
    ],
    identity_service: Annotated[IdentityAccessService, Depends(get_identity_service)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> LogoutEnvelope:
    """Revoke server-side session and clear cookie (`logoutUser`)."""
    raw_token = extract_session_cookie(request, settings) or ""
    await identity_service.logout(principal=principal, raw_token=raw_token)
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE,
    )
    return LogoutEnvelope(
        data=LogoutData(),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@auth_router.get("/me", response_model=AuthUserEnvelope)
async def get_current_user(
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(require_access(required_permissions=("auth.session.read",))),
    ],
) -> AuthUserEnvelope:
    """Return active user profile, roles, and scopes (`getCurrentUser`)."""
    return AuthUserEnvelope(
        data=principal_to_dto(principal),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@admin_users_router.get("", response_model=AdminUserListEnvelope)
async def list_users(
    _principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.SYSTEM_ADMIN,),
                required_permissions=("admin.users.read",),
            )
        ),
    ],
    identity_service: Annotated[IdentityAccessService, Depends(get_identity_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    q: Annotated[str | None, Query(max_length=120)] = None,
) -> AdminUserListEnvelope:
    """List internal user accounts for SYSTEM_ADMIN without credentials (`listUsers`)."""
    rows, total = await identity_service.list_users(page=page, page_size=page_size, query=q)
    return AdminUserListEnvelope(
        data=[admin_record_to_dto(r) for r in rows],
        meta=build_pagination_meta(page, page_size, total),
        request_id=request_id_ctx.get(),
    )


@admin_users_router.post("", response_model=AdminUserEnvelope, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: CreateUserRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.SYSTEM_ADMIN,),
                required_permissions=("admin.users.write",),
            )
        ),
    ],
    identity_service: Annotated[IdentityAccessService, Depends(get_identity_service)],
) -> AdminUserEnvelope:
    """Create user account with explicit role & scope (`createUser`, BR-SYS-002)."""
    created = await identity_service.create_user(
        actor=principal,
        username=payload.username,
        email=payload.email,
        raw_password=payload.password,
        role_code=payload.role_code,
        scope_type=payload.scope_type,
        farmer_id=payload.farmer_id,
        cooperative_id=payload.cooperative_id,
        mill_id=payload.mill_id,
    )
    return AdminUserEnvelope(
        data=admin_record_to_dto(created),
        meta=None,
        request_id=request_id_ctx.get(),
    )


@admin_users_router.patch("/{user_id}", response_model=AdminUserEnvelope)
async def update_user_access(
    user_id: UUID,
    payload: UpdateUserAccessRequest,
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(
            require_access(
                allowed_roles=(RoleCode.SYSTEM_ADMIN,),
                required_permissions=("admin.users.write",),
            )
        ),
    ],
    identity_service: Annotated[IdentityAccessService, Depends(get_identity_service)],
) -> AdminUserEnvelope:
    """Update role/scope/status and revoke active sessions immediately (`updateUserAccess`)."""
    updated = await identity_service.update_user_access(
        actor=principal,
        target_user_id=user_id,
        status=payload.status,
        role_code=payload.role_code,
        scope_type=payload.scope_type,
        farmer_id=payload.farmer_id,
        cooperative_id=payload.cooperative_id,
        mill_id=payload.mill_id,
        reason=payload.reason,
    )
    return AdminUserEnvelope(
        data=admin_record_to_dto(updated),
        meta=None,
        request_id=request_id_ctx.get(),
    )
