"""Unit tests guaranteeing `seed_demo.py` isolation, CLI reset guards, and actor specs."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from app.modules.identity_access.domain.entities import RoleCode

_SEED_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "seed_demo.py"
_SPEC = importlib.util.spec_from_file_location("demo_seed_module", _SEED_SCRIPT_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_SEED_MOD = importlib.util.module_from_spec(_SPEC)
sys.modules["demo_seed_module"] = _SEED_MOD
_SPEC.loader.exec_module(_SEED_MOD)


def _write_env(tmp_path: Path, db_name: str, redis_db: str, extra: str = "") -> Path:
    env_file = tmp_path / ".env.demo"
    env_file.write_text(
        "\n".join(
            [
                f"DATABASE_URL=postgresql+psycopg://agroniaga_demo:localpass123@127.0.0.1:15432/{db_name}",
                f"REDIS_URL=redis://127.0.0.1:6379/{redis_db}",
                "SESSION_COOKIE_NAME=ts_agroniaga_demo_session",
                "SESSION_SECRET=test-demo-session-secret-0123456789abcdef0123456789",
                extra,
            ]
        ),
        encoding="utf-8",
    )
    return env_file


def test_load_isolated_demo_settings_rejects_non_demo_db_and_redis(tmp_path: Path) -> None:
    for bad_db in ("agroniaga_dev", "agroniaga_test", "postgres"):
        env_file = _write_env(tmp_path, bad_db, "2")
        with pytest.raises(SystemExit, match="agroniaga_demo"):
            _SEED_MOD.load_isolated_demo_settings(env_file)

    for bad_redis in ("0", "1", "3"):
        env_file = _write_env(tmp_path, "agroniaga_demo", bad_redis)
        with pytest.raises(SystemExit, match="/2"):
            _SEED_MOD.load_isolated_demo_settings(env_file)


def test_load_isolated_demo_settings_accepts_only_demo_and_strips_test_vars(tmp_path: Path) -> None:
    env_file = _write_env(
        tmp_path,
        "agroniaga_demo",
        "2",
        extra="TEST_DATABASE_URL=postgresql+psycopg://x:y@127.0.0.1:15432/agroniaga_test\n"
        "TEST_REDIS_URL=redis://127.0.0.1:6379/1",
    )
    cfg = _SEED_MOD.load_isolated_demo_settings(env_file)
    assert cfg.DATABASE_URL.get_secret_value().endswith("/agroniaga_demo")
    assert cfg.REDIS_URL.get_secret_value().endswith("/2")
    assert cfg.SESSION_COOKIE_NAME == "ts_agroniaga_demo_session"


def test_actor_specs_cover_all_seven_roles_and_reproducible_ids() -> None:
    roles_covered = {spec.role for spec in _SEED_MOD.ACTOR_SPECS}
    assert roles_covered == set(RoleCode)
    assert len({spec.username for spec in _SEED_MOD.ACTOR_SPECS}) == len(_SEED_MOD.ACTOR_SPECS)
    assert _SEED_MOD.demo_uuid("demo-check-1") == _SEED_MOD.demo_uuid("demo-check-1")
    assert _SEED_MOD.demo_uuid("demo-check-1") != _SEED_MOD.demo_uuid("demo-check-2")


def test_reset_guard_refuses_wrong_confirm_database(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_file = _write_env(tmp_path, "agroniaga_demo", "2")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "seed_demo.py",
            "--env-file",
            str(env_file),
            "--reset-demo",
            "--confirm-reset",
            "agroniaga_dev",
            "--yes",
        ],
    )
    with pytest.raises(SystemExit, match="agroniaga_demo"):
        _SEED_MOD.main()
