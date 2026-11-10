"""Unit test suite wrapping deterministic M0 contract validation checks (K1-K10)."""

from __future__ import annotations

import sys
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

    def test_k11_m0_1_handoff_doc_consistency(self) -> None:
        self.assertEqual(self.k1_issues, [], "K1 must pass before K11")
        self._assert_no_issues(vc.check_k11_handoff_doc_consistency(self.oa, self.rp))


if __name__ == "__main__":
    unittest.main(verbosity=2)
