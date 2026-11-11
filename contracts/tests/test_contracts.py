"""Unit test suite wrapping deterministic M0 contract validation checks (K1-K10)."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import validate_contracts as vc


class M0ContractValidationTests(unittest.TestCase):
    """Verify cross-contract consistency across OpenAPI, catalogs, fixtures, and traceability."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.loaded, cls.k1_issues = vc.check_k1_syntax_and_unique_keys()
        if not cls.k1_issues:
            cls.oa = cls.loaded["yaml"]["openapi.v1.yaml"]
            cls.ec = cls.loaded["yaml"]["error-catalog.yaml"]
            cls.sc = cls.loaded["yaml"]["state-catalog.yaml"]
            cls.rp = cls.loaded["yaml"]["role-permissions.yaml"]
            cls.fixtures = cls.loaded["json"]

    def _assert_no_issues(self, issues: list[str]) -> None:
        self.assertEqual(issues, [], "\n".join(issues))

    def test_k1_syntax_and_duplicate_keys(self) -> None:
        self._assert_no_issues(self.k1_issues)

    def test_k2_openapi_spec(self) -> None:
        self.assertEqual(self.k1_issues, [], "K1 must pass before K2")
        self._assert_no_issues(vc.check_k2_openapi(self.oa))

    def test_k3_error_catalog(self) -> None:
        self.assertEqual(self.k1_issues, [], "K1 must pass before K3")
        self._assert_no_issues(
            vc.check_k3_error_catalog(self.ec, self.oa, self.sc, self.fixtures["error-scenarios.json"])
        )

    def test_k4_state_catalog(self) -> None:
        self.assertEqual(self.k1_issues, [], "K1 must pass before K4")
        self._assert_no_issues(vc.check_k4_state_catalog(self.sc, self.ec, self.oa, self.rp))

    def test_k5_role_permission_matrix(self) -> None:
        self.assertEqual(self.k1_issues, [], "K1 must pass before K5")
        self._assert_no_issues(vc.check_k5_role_permissions(self.rp, self.oa))

    def test_k6_fixtures_schema_and_crossref(self) -> None:
        self.assertEqual(self.k1_issues, [], "K1 must pass before K6")
        self._assert_no_issues(vc.check_k6_fixtures(self.fixtures, self.oa, self.rp, self.sc))

    def test_k7_traceability_completeness(self) -> None:
        self.assertEqual(self.k1_issues, [], "K1 must pass before K7")
        self._assert_no_issues(vc.check_k7_traceability(self.oa))

    def test_k8_openapi_typescript_codegen(self) -> None:
        self.assertEqual(self.k1_issues, [], "K1 must pass before K8")
        self._assert_no_issues(vc.check_k8_openapi_typescript())

    def test_k9_backend_contract_readiness(self) -> None:
        self.assertEqual(self.k1_issues, [], "K1 must pass before K9")
        self._assert_no_issues(vc.check_k9_backend_readiness(self.oa, self.ec, self.sc))

    def test_k10_scope_and_hygiene(self) -> None:
        self._assert_no_issues(vc.check_k10_scope_hygiene())

    def test_k10_phase_rules_m0_backend_and_frontend(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            for doc_rel in vc.PROTECTED_V11_DOCS:
                (root / doc_rel).write_text("V1.1 Baseline Content\n", encoding="utf-8")

            # 1. M0 rejects implementation folders
            (root / "backend").mkdir()
            issues_m0 = vc.check_k10_scope_hygiene(
                repo_root=root,
                checkpoint_text="# IMPLEMENTATION CHECKPOINTS\n## Checkpoint M0\n",
                check_git_baseline=False,
            )
            self.assertTrue(any("M0" in msg and "backend/" in msg for msg in issues_m0))

            # 2. Backend Track allows backend/alembic/versions but forbids frontend/ & stray root alembic/
            (root / "backend" / "alembic" / "versions").mkdir(parents=True)
            (root / "frontend").mkdir()
            issues_backend = vc.check_k10_scope_hygiene(
                repo_root=root,
                checkpoint_text="# BACKEND DEVELOPMENT TRACK\n",
                check_git_baseline=False,
            )
            self.assertEqual(len(issues_backend), 1)
            self.assertIn("frontend/", issues_backend[0])

            # 3. Frontend Track allows backend/ + frontend/ with codegen artifact, forbids stray root alembic/
            (root / "frontend" / "src" / "lib" / "api").mkdir(parents=True)
            (root / "frontend" / "package.json").write_text('{"name":"frontend"}\n', encoding="utf-8")
            (root / "frontend" / "src" / "lib" / "api" / "generated.d.ts").write_text(
                "export interface paths {}\n", encoding="utf-8"
            )
            cp_frontend = "# BACKEND DEVELOPMENT TRACK\n## FRONTEND DEVELOPMENT TRACK (`F0-F11`)\n"
            issues_frontend_ok = vc.check_k10_scope_hygiene(
                repo_root=root,
                checkpoint_text=cp_frontend,
                check_git_baseline=False,
            )
            self.assertEqual(issues_frontend_ok, [])

            (root / "alembic").mkdir()
            issues_stray_alembic = vc.check_k10_scope_hygiene(
                repo_root=root,
                checkpoint_text=cp_frontend,
                check_git_baseline=False,
            )
            self.assertTrue(any("alembic/" in msg for msg in issues_stray_alembic))

    def test_k10_blocks_unauthorized_contract_or_v11_modification(self) -> None:
        git_bin = shutil.which("git")
        if not git_bin:
            self.skipTest("git binary not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "contracts" / "fixtures").mkdir(parents=True)
            (root / "docs").mkdir(parents=True)
            for rel in vc.PROTECTED_CONTRACT_PATHS[:-1]:
                (root / rel).write_text("baseline: true\n", encoding="utf-8")
            (root / "contracts" / "fixtures" / "sample.json").write_text("{}\n", encoding="utf-8")
            for doc_rel in vc.PROTECTED_V11_DOCS:
                (root / doc_rel).write_text("V1.1\n", encoding="utf-8")

            subprocess.run([git_bin, "init"], cwd=str(root), check=True, capture_output=True)
            subprocess.run([git_bin, "config", "user.email", "test@local.invalid"], cwd=str(root), check=True)
            subprocess.run([git_bin, "config", "user.name", "Test Runner"], cwd=str(root), check=True)
            subprocess.run([git_bin, "add", "."], cwd=str(root), check=True)
            subprocess.run([git_bin, "commit", "-m", "baseline"], cwd=str(root), check=True, capture_output=True)

            # Clean baseline passes K10
            self.assertEqual(
                vc.check_k10_scope_hygiene(repo_root=root, checkpoint_text="## FRONTEND DEVELOPMENT TRACK"),
                [],
            )

            # Unauthorized contract modification triggers K10 failure
            (root / "contracts" / "openapi.v1.yaml").write_text("mutated: true\n", encoding="utf-8")
            issues_contract = vc.check_k10_scope_hygiene(
                repo_root=root, checkpoint_text="## FRONTEND DEVELOPMENT TRACK"
            )
            self.assertTrue(any("openapi.v1.yaml" in msg for msg in issues_contract))

            # Unauthorized V1.1 baseline doc modification triggers K10 failure
            subprocess.run(
                [git_bin, "checkout", "--", "contracts/openapi.v1.yaml"], cwd=str(root), check=True
            )
            (root / "docs" / "PRD.md").write_text("mutated doc\n", encoding="utf-8")
            issues_doc = vc.check_k10_scope_hygiene(
                repo_root=root, checkpoint_text="## FRONTEND DEVELOPMENT TRACK"
            )
            self.assertTrue(any("docs/PRD.md" in msg for msg in issues_doc))

    def test_k11_m0_1_handoff_doc_consistency(self) -> None:
        self.assertEqual(self.k1_issues, [], "K1 must pass before K11")
        self._assert_no_issues(vc.check_k11_handoff_doc_consistency(self.oa, self.rp))


if __name__ == "__main__":
    unittest.main(verbosity=2)
