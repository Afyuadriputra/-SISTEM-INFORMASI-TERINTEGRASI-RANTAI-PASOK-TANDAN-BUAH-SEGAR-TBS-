"""Static AST and import-linter tests enforcing Clean Architecture boundaries (ADR-001/002)."""

from __future__ import annotations

import ast
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[2] / "app"

DOMAIN_FORBIDDEN_IMPORTS = frozenset(
    {
        "fastapi",
        "starlette",
        "sqlalchemy",
        "redis",
        "psycopg",
        "alembic",
    }
)


def _iter_imported_modules(py_file: Path) -> set[str]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    return imported


def test_core_does_not_import_modules() -> None:
    core_dir = APP_ROOT / "core"
    for py_file in core_dir.rglob("*.py"):
        imports = _iter_imported_modules(py_file)
        violations = [imp for imp in imports if imp.startswith("app.modules")]
        assert not violations, f"{py_file} illegally imports domain modules: {violations}"


def test_no_empty_placeholder_module_folders() -> None:
    modules_dir = APP_ROOT / "modules"
    if not modules_dir.exists():
        return
    for module_path in modules_dir.iterdir():
        if not module_path.is_dir() or module_path.name == "__pycache__":
            continue
        py_files = [
            f
            for f in module_path.rglob("*.py")
            if f.name != "__init__.py" and "__pycache__" not in f.parts
        ]
        assert py_files, (
            f"Empty scaffolding module directory forbidden in solo-dev structure: {module_path}"
        )


def test_active_modules_respect_four_layer_dependency_direction() -> None:
    modules_dir = APP_ROOT / "modules"
    if not modules_dir.exists():
        return

    for module_path in modules_dir.iterdir():
        if not module_path.is_dir() or module_path.name == "__pycache__":
            continue
        mod_prefix = f"app.modules.{module_path.name}"
        for layer in ("domain", "application", "infrastructure", "presentation"):
            assert (module_path / layer).is_dir(), (
                f"Active module {module_path.name} missing required Clean Architecture layer {layer}/"
            )

        for py_file in (module_path / "domain").rglob("*.py"):
            imports = _iter_imported_modules(py_file)
            for imp in imports:
                root_pkg = imp.split(".")[0]
                assert root_pkg not in DOMAIN_FORBIDDEN_IMPORTS, (
                    f"{py_file} domain layer cannot import {imp}"
                )
                assert not imp.startswith(
                    (
                        f"{mod_prefix}.application",
                        f"{mod_prefix}.infrastructure",
                        f"{mod_prefix}.presentation",
                    )
                ), f"{py_file} domain layer cannot depend on outer layer {imp}"

        for py_file in (module_path / "application").rglob("*.py"):
            imports = _iter_imported_modules(py_file)
            for imp in imports:
                root_pkg = imp.split(".")[0]
                assert root_pkg not in {"fastapi", "starlette"}, (
                    f"{py_file} application layer cannot import web framework {imp}"
                )
                assert not imp.startswith(
                    (f"{mod_prefix}.infrastructure", f"{mod_prefix}.presentation")
                ), f"{py_file} application layer cannot import concrete {imp}"

        for py_file in (module_path / "presentation").rglob("*.py"):
            imports = _iter_imported_modules(py_file)
            for imp in imports:
                assert not imp.startswith(f"{mod_prefix}.infrastructure"), (
                    f"{py_file} presentation layer must call application, not infrastructure {imp}"
                )
