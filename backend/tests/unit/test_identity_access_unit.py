"""Unit tests verifying RBAC matrix contract parity, scope invariants, and CSRF binding."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest
import yaml
from app.core.config import Settings
from app.core.exceptions import AppError, ErrorCode
from app.modules.identity_access.domain.entities import (
    AccessScopeEntity,
    AccountStatus,
    AuthenticatedPrincipal,
    RoleCode,
    ScopeType,
)
from app.modules.identity_access.domain.rules import (
    APPROVER_FORBIDDEN_PERMISSIONS,
    CANONICAL_PERMISSIONS,
    ROLE_ALLOWED_SCOPES,
    ROLE_PERMISSIONS_MAP,
    assert_authorized,
    assert_cooperative_scope,
    assert_farmer_scope,
    assert_mill_scope,
    compute_effective_permissions,
    validate_role_scope_assignment,
)
from app.modules.identity_access.infrastructure.security_adapters import HmacCsrfManager
from pydantic import SecretStr


def _make_principal(
    role: RoleCode,
    scope_type: ScopeType,
    *,
    farmer_id: UUID | None = None,
    cooperative_id: UUID | None = None,
    mill_id: UUID | None = None,
) -> AuthenticatedPrincipal:
    perms = compute_effective_permissions((role,), ROLE_PERMISSIONS_MAP[role])
    return AuthenticatedPrincipal(
        session_id=uuid4(),
        user_id=uuid4(),
        username=f"test_{role.value.lower()}",
        email=None,
        display_name=role.value,
        linked_party_id=None,
        status=AccountStatus.ACTIVE,
        roles=(role,),
        access_scopes=(
            AccessScopeEntity(
                id=uuid4(),
                scope_type=scope_type,
                farmer_id=farmer_id,
                cooperative_id=cooperative_id,
                mill_id=mill_id,
            ),
        ),
        permissions=perms,
        last_login_at=None,
        non_approver_admin=(role == RoleCode.SYSTEM_ADMIN),
    )


def test_rbac_catalog_matches_contracts_role_permissions_yaml(contracts_dir: Path) -> None:
    raw = yaml.safe_load((contracts_dir / "role-permissions.yaml").read_text(encoding="utf-8"))
    contract_perm_codes = {p["code"] for p in raw["permissions"]}
    domain_perm_codes = {p.code for p in CANONICAL_PERMISSIONS}

    assert len(contract_perm_codes) == 64
    assert domain_perm_codes == contract_perm_codes

    for role_enum in RoleCode:
        contract_role_perms = set(raw["role_grants"][role_enum.value]["permissions"])
        assert set(ROLE_PERMISSIONS_MAP[role_enum]) == contract_role_perms

        role_meta = next(r for r in raw["roles"] if r["role_code"] == role_enum.value)
        assert {s.value for s in ROLE_ALLOWED_SCOPES[role_enum]} == set(role_meta["allowed_scopes"])


def test_system_admin_never_receives_approver_permissions_br_sys_002() -> None:
    tampered_db_perms = frozenset(ROLE_PERMISSIONS_MAP[RoleCode.SYSTEM_ADMIN]) | frozenset(
        APPROVER_FORBIDDEN_PERMISSIONS
    )
    effective = compute_effective_permissions((RoleCode.SYSTEM_ADMIN,), tampered_db_perms)
    assert effective.isdisjoint(APPROVER_FORBIDDEN_PERMISSIONS)

    admin = _make_principal(RoleCode.SYSTEM_ADMIN, ScopeType.PERUMDA_GLOBAL)
    for forbidden_perm in APPROVER_FORBIDDEN_PERMISSIONS:
        with pytest.raises(AppError) as exc:
            assert_authorized(admin, required_permissions=(forbidden_perm,))
        assert exc.value.code == ErrorCode.AUTH_OPERATION_FORBIDDEN
        assert exc.value.status_code == 403


def test_scope_binding_and_cross_scope_ownership_checks() -> None:
    farmer_a, farmer_b = uuid4(), uuid4()
    coop_a, coop_b = uuid4(), uuid4()
    mill_a, mill_b = uuid4(), uuid4()

    validate_role_scope_assignment(RoleCode.FARMER, ScopeType.FARMER, farmer_a, None, None)
    with pytest.raises(AppError) as exc1:
        validate_role_scope_assignment(RoleCode.FARMER, ScopeType.FARMER, None, None, None)
    assert exc1.value.code == ErrorCode.VAL_INVALID_FORMAT

    with pytest.raises(AppError) as exc2:
        validate_role_scope_assignment(
            RoleCode.COOPERATIVE_OPERATOR, ScopeType.PERUMDA_GLOBAL, None, None, None
        )
    assert exc2.value.code == ErrorCode.VAL_INVALID_FORMAT

    farmer_principal = _make_principal(RoleCode.FARMER, ScopeType.FARMER, farmer_id=farmer_a)
    assert_farmer_scope(farmer_principal, farmer_a)
    with pytest.raises(AppError) as exc3:
        assert_farmer_scope(farmer_principal, farmer_b)
    assert exc3.value.code == ErrorCode.AUTH_SCOPE_FORBIDDEN

    coop_principal = _make_principal(
        RoleCode.COOPERATIVE_OPERATOR, ScopeType.COOPERATIVE, cooperative_id=coop_a
    )
    assert_cooperative_scope(coop_principal, coop_a)
    with pytest.raises(AppError) as exc4:
        assert_cooperative_scope(coop_principal, coop_b)
    assert exc4.value.code == ErrorCode.AUTH_SCOPE_FORBIDDEN

    mill_principal = _make_principal(RoleCode.MILL_OPERATOR, ScopeType.MILL, mill_id=mill_a)
    assert_mill_scope(mill_principal, mill_a)
    with pytest.raises(AppError) as exc5:
        assert_mill_scope(mill_principal, mill_b, error_code=ErrorCode.MILL_EDO_MILL_MISMATCH)
    assert exc5.value.code == ErrorCode.MILL_EDO_MILL_MISMATCH


def test_hmac_csrf_binds_strictly_to_session_id() -> None:
    mgr = HmacCsrfManager("unit-test-csrf-secret-key-minimum-length")
    sess_a, sess_b = uuid4(), uuid4()

    pre_auth = mgr.issue_pre_auth()
    tok_a = mgr.issue_for_session(sess_a)

    assert mgr.verify_for_session(tok_a, sess_a) is True
    assert mgr.verify_for_session(tok_a, sess_b) is False
    assert mgr.verify_for_session(pre_auth, sess_a) is False
    assert mgr.verify_for_session(None, sess_a) is False


def test_staging_production_requires_strong_secret_and_secure_cookie() -> None:
    with pytest.raises(ValueError):
        Settings(APP_ENV="production", SESSION_COOKIE_SECURE=False)
    with pytest.raises(ValueError):
        Settings(
            APP_ENV="staging",
            SESSION_SECRET=SecretStr("local-dev-session-secret-replace-before-staging-32bytes"),
            SESSION_COOKIE_SECURE=True,
        )
    prod_ok = Settings(
        APP_ENV="production",
        SESSION_SECRET=SecretStr("prod-unique-cryptographic-key-with-more-than-32-chars"),
        SESSION_COOKIE_SECURE=True,
    )
    assert prod_ok.SESSION_COOKIE_SECURE is True
