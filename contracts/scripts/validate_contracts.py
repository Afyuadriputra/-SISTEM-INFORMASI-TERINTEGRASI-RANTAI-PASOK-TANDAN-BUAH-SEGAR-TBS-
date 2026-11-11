"""Deterministic offline contract validation suite (M0 Phase K: K1-K10).

Run from repository root:
    python contracts/scripts/validate_contracts.py
"""

from __future__ import annotations

import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator, FormatChecker
from openapi_pydantic import OpenAPI
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = REPO_ROOT / "contracts"
FIXTURES_DIR = CONTRACTS_DIR / "fixtures"
DOCS_DIR = REPO_ROOT / "docs"
TRACEABILITY_FILE = DOCS_DIR / "m0" / "M0_REQUIREMENT_TRACEABILITY.md"


class UniqueKeySafeLoader(yaml.SafeLoader):
    """YAML SafeLoader that rejects duplicate mapping keys."""


def _construct_mapping_no_duplicates(
    loader: UniqueKeySafeLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"Duplicate YAML mapping key detected: {key!r} at line {key_node.start_mark.line + 1}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping_no_duplicates,
)


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, val in pairs:
        if key in obj:
            raise ValueError(f"Duplicate JSON object key detected: {key!r}")
        obj[key] = val
    return obj


def load_strict_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.load(fh, Loader=UniqueKeySafeLoader)


def load_strict_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.loads(fh.read(), object_pairs_hook=_reject_duplicate_json_keys)


def build_json_schema_from_oas(schema_name: str, oa: dict[str, Any]) -> dict[str, Any]:
    """Build a self-contained Draft 2020-12 JSON Schema referencing OpenAPI components."""
    components_schemas = copy.deepcopy(oa["components"]["schemas"])
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": f"#/components/schemas/{schema_name}",
        "components": {"schemas": components_schemas},
    }


def validate_against_oas_schema(
    instance: Any, schema_name: str, oa: dict[str, Any], label: str
) -> list[str]:
    schema = build_json_schema_from_oas(schema_name, oa)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    return [f"{label} [{schema_name}] at {list(err.path)}: {err.message}" for err in errors]


def extract_oas_operations(oa: dict[str, Any]) -> dict[str, dict[str, Any]]:
    ops: dict[str, dict[str, Any]] = {}
    for path, path_item in oa.get("paths", {}).items():
        if not isinstance(path_item, dict):
            continue
        path_params = path_item.get("parameters", [])
        for method in ("get", "post", "put", "patch", "delete", "options", "head"):
            op = path_item.get(method)
            if not isinstance(op, dict):
                continue
            op_id = op.get("operationId")
            ops[op_id] = {
                "operationId": op_id,
                "method": method.upper(),
                "path": path,
                "op": op,
                "path_parameters": path_params,
            }
    return ops


def check_k1_syntax_and_unique_keys() -> tuple[dict[str, Any], list[str]]:
    issues: list[str] = []
    loaded: dict[str, Any] = {"yaml": {}, "json": {}}
    yaml_files = sorted(CONTRACTS_DIR.glob("*.yaml"))
    json_files = sorted(FIXTURES_DIR.glob("*.json"))
    if not yaml_files or not json_files:
        issues.append("Missing contract YAML files or fixture JSON files.")
        return loaded, issues

    for path in yaml_files:
        try:
            loaded["yaml"][path.name] = load_strict_yaml(path)
        except Exception as exc:
            issues.append(f"K1 YAML error in {path.relative_to(REPO_ROOT)}: {exc}")

    for path in json_files:
        try:
            loaded["json"][path.name] = load_strict_json(path)
        except Exception as exc:
            issues.append(f"K1 JSON error in {path.relative_to(REPO_ROOT)}: {exc}")

    return loaded, issues


def _collect_refs(node: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(node, dict):
        if "$ref" in node and isinstance(node["$ref"], str):
            refs.append(node["$ref"])
        for val in node.values():
            refs.extend(_collect_refs(val))
    elif isinstance(node, list):
        for item in node:
            refs.extend(_collect_refs(item))
    return refs


def _resolve_param(param: dict[str, Any], oa: dict[str, Any]) -> dict[str, Any]:
    if "$ref" in param:
        ref = param["$ref"]
        if ref.startswith("#/components/parameters/"):
            key = ref.split("/")[-1]
            return oa.get("components", {}).get("parameters", {}).get(key, param)
    return param


def check_k2_openapi(oa: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    try:
        OpenAPI.model_validate(oa)
    except Exception as exc:
        issues.append(f"K2 openapi_pydantic validation failed: {exc}")
        return issues

    if oa.get("openapi") != "3.1.0":
        issues.append(f"K2 expected OpenAPI version 3.1.0, got {oa.get('openapi')!r}")

    components = oa.get("components", {})
    for ref in _collect_refs(oa):
        if not ref.startswith("#/components/"):
            issues.append(f"K2 non-local or unexpected $ref: {ref}")
            continue
        parts = ref[2:].split("/")
        cur: Any = oa
        for part in parts:
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                issues.append(f"K2 unresolved $ref: {ref}")
                break

    sec_schemes = components.get("securitySchemes", {})
    for req_sec in ("SessionCookieAuth", "CsrfTokenHeader"):
        if req_sec not in sec_schemes:
            issues.append(f"K2 missing securityScheme {req_sec!r}")

    seen_op_ids: set[str] = set()
    for path, path_item in oa.get("paths", {}).items():
        if not isinstance(path_item, dict):
            continue
        path_vars = set(re.findall(r"\{([^}]+)\}", path))
        path_param_defs = {}
        for raw_p in path_item.get("parameters", []):
            p = _resolve_param(raw_p, oa) if isinstance(raw_p, dict) else {}
            if p.get("in") == "path":
                path_param_defs[p.get("name")] = p
        for method in ("get", "post", "put", "patch", "delete"):
            op = path_item.get(method)
            if not op:
                continue
            op_id = op.get("operationId")
            if not op_id:
                issues.append(f"K2 missing operationId on {method.upper()} {path}")
                continue
            if op_id in seen_op_ids:
                issues.append(f"K2 duplicate operationId {op_id!r}")
            seen_op_ids.add(op_id)

            op_param_defs = dict(path_param_defs)
            for raw_p in op.get("parameters", []):
                p = _resolve_param(raw_p, oa) if isinstance(raw_p, dict) else {}
                if p.get("in") == "path":
                    op_param_defs[p.get("name")] = p
            missing_vars = path_vars - set(op_param_defs.keys())
            if missing_vars:
                issues.append(f"K2 {op_id} missing path parameter definitions: {sorted(missing_vars)}")
            for pname, pdef in op_param_defs.items():
                if pname in path_vars and pdef.get("required") is not True:
                    issues.append(f"K2 {op_id} path parameter {pname!r} must have required: true")

            if not op.get("responses"):
                issues.append(f"K2 {op_id} has no responses")
            if not op.get("summary"):
                issues.append(f"K2 {op_id} missing summary")

    return issues


def check_k3_error_catalog(
    ec: dict[str, Any], oa: dict[str, Any], sc: dict[str, Any], err_fx: dict[str, Any]
) -> list[str]:
    issues: list[str] = []
    valid_http = {400, 401, 403, 404, 409, 413, 415, 422, 429, 500, 502, 503, 504}
    ops = extract_oas_operations(oa)
    errors = ec.get("errors", [])
    seen_codes: set[str] = set()
    code_map: dict[str, dict[str, Any]] = {}

    for item in errors:
        code = item.get("code", "")
        if code in seen_codes:
            issues.append(f"K3 duplicate error code in error-catalog.yaml: {code}")
        seen_codes.add(code)
        code_map[code] = item

        if not re.match(r"^[A-Z0-9]+(_[A-Z0-9]+)+$", code):
            issues.append(f"K3 error code violates MODULE_CATEGORY_DESCRIPTION convention: {code}")
        if item.get("http_status") not in valid_http:
            issues.append(f"K3 invalid HTTP status {item.get('http_status')} on {code}")
        if not isinstance(item.get("retryable"), bool):
            issues.append(f"K3 retryable must be boolean on {code}")
        for req_text in ("client_safe_message", "required_user_action", "security_considerations"):
            if not isinstance(item.get(req_text), str) or not item[req_text].strip():
                issues.append(f"K3 missing or empty {req_text!r} on {code}")
        for rel_op in item.get("related_operations", []):
            if rel_op not in ops:
                issues.append(f"K3 {code} references unknown related_operation {rel_op!r}")

    oa_error_enum = set(oa["components"]["schemas"]["ErrorCode"].get("enum", []))
    if seen_codes != oa_error_enum:
        missing_in_oa = sorted(seen_codes - oa_error_enum)
        missing_in_ec = sorted(oa_error_enum - seen_codes)
        issues.append(
            f"K3 ErrorCode mismatch: in error-catalog only={missing_in_oa}, in OpenAPI only={missing_in_ec}"
        )

    for machine in sc.get("state_machines", []):
        for trans in machine.get("transitions", []):
            for err_code in trans.get("error_codes", []):
                if err_code not in code_map:
                    issues.append(
                        f"K3 state-catalog {machine['machine_id']} references unknown error {err_code!r}"
                    )

    for scen in err_fx.get("scenarios", []):
        sid = scen.get("scenario_id")
        exp_http = scen.get("expected_http_status")
        resp = scen.get("error_response", {})
        err_obj = resp.get("error", {})
        ecode = err_obj.get("code")
        if ecode not in code_map:
            issues.append(f"K3 error-scenarios {sid} references unknown error {ecode!r}")
        elif code_map[ecode]["http_status"] != exp_http:
            issues.append(
                f"K3 error-scenarios {sid} HTTP mismatch: fixture={exp_http}, catalog={code_map[ecode]['http_status']}"
            )

    return issues


def _derived_state_names(machine: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for item in machine.get("derived_states", []):
        if isinstance(item, dict) and "name" in item:
            names.add(str(item["name"]))
        elif isinstance(item, str):
            names.add(item)
    return names


def check_k4_state_catalog(
    sc: dict[str, Any], ec: dict[str, Any], oa: dict[str, Any], rp: dict[str, Any]
) -> list[str]:
    issues: list[str] = []
    ops = extract_oas_operations(oa)
    error_codes = {e["code"] for e in ec.get("errors", [])}
    perm_codes = {p["code"] for p in rp.get("permissions", [])}

    machines = sc.get("state_machines", [])
    if len(machines) < 11:
        issues.append(f"K4 expected at least 11 state machines, got {len(machines)}")

    seen_ids: set[str] = set()
    by_id: dict[str, dict[str, Any]] = {}
    for m in machines:
        mid = m.get("machine_id")
        if mid in seen_ids:
            issues.append(f"K4 duplicate machine_id {mid!r}")
        seen_ids.add(mid)
        by_id[mid] = m

        persisted = set(m.get("persisted_states", []))
        derived = _derived_state_names(m)
        if not persisted:
            issues.append(f"K4 {mid} has empty persisted_states")
        if persisted & derived:
            issues.append(f"K4 {mid} overlaps persisted and derived states: {sorted(persisted & derived)}")
        if m.get("initial_state") not in persisted:
            issues.append(f"K4 {mid} initial_state {m.get('initial_state')!r} not in persisted_states")
        term = set(m.get("terminal_states", []))
        if not term or not term.issubset(persisted):
            issues.append(f"K4 {mid} invalid terminal_states: {sorted(term)}")
        if "pending_sop_classification" not in m:
            issues.append(f"K4 {mid} missing pending_sop_classification")

        for t in m.get("transitions", []):
            if t.get("from") not in persisted:
                issues.append(f"K4 {mid} transition from invalid state {t.get('from')!r}")
            if t.get("to") not in persisted:
                issues.append(f"K4 {mid} transition to invalid state {t.get('to')!r}")
            op_id = t.get("api_operation_id")
            if op_id not in ops:
                issues.append(f"K4 {mid} transition references unknown operation {op_id!r}")
            req_perm = t.get("required_permission")
            if req_perm and req_perm not in perm_codes:
                issues.append(f"K4 {mid} transition references unknown permission {req_perm!r}")
            for err in t.get("error_codes", []):
                if err not in error_codes:
                    issues.append(f"K4 {mid} transition references unknown error {err!r}")

    schemas = oa["components"]["schemas"]
    enum_pairs = [
        ("SM-01_PRICE_QUOTE", "PriceQuoteStatus", "persisted"),
        ("SM-01_PRICE_QUOTE", "PriceDisplayStatus", "combined"),
        ("SM-02_TBS_RECEIPT", "ReceiptStatus", "persisted"),
        ("SM-03_TRADE_CONTRACT", "ContractStatus", "persisted"),
        ("SM-05_DELIVERY_ORDER", "DeliveryOrderStatus", "persisted"),
        ("SM-06_MILL_TICKET", "MillTicketStatus", "persisted"),
        ("SM-07_RECONCILIATION_CASE", "ReconciliationStatus", "persisted"),
        ("SM-09_INVOICE", "InvoiceStatus", "persisted"),
        ("SM-11_PAYMENT_RECORD", "PaymentRecordStatus", "persisted"),
    ]
    for mid, oa_schema, mode in enum_pairs:
        machine = by_id.get(mid)
        if not machine:
            issues.append(f"K4 missing required state machine {mid}")
            continue
        expected = set(machine["persisted_states"])
        if mode == "combined":
            expected |= _derived_state_names(machine)
        actual = set(schemas[oa_schema].get("enum", []))
        if expected != actual:
            issues.append(
                f"K4 enum mismatch for {mid} vs OpenAPI {oa_schema}: sc={sorted(expected)}, oa={sorted(actual)}"
            )

    return issues


def check_k5_role_permissions(rp: dict[str, Any], oa: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    expected_db_roles = {
        "FARMER",
        "COOPERATIVE_OPERATOR",
        "PERUMDA_OPERATIONS",
        "PERUMDA_FINANCE",
        "MILL_OPERATOR",
        "DIRECTOR",
        "SYSTEM_ADMIN",
    }
    oa_roles = set(oa["components"]["schemas"]["RoleCode"]["enum"])
    if oa_roles != expected_db_roles:
        issues.append(f"K5 OpenAPI RoleCode mismatch: {sorted(oa_roles)}")

    rp_roles = {r["role_code"] if isinstance(r, dict) else r for r in rp.get("roles", [])}
    if rp_roles != expected_db_roles:
        issues.append(f"K5 role-permissions roles mismatch: {sorted(rp_roles)}")

    all_actor_codes = rp_roles | {a["role_code"] if isinstance(a, dict) else a for a in rp.get("actors", [])}
    if "PUBLIC" not in all_actor_codes:
        issues.append("K5 missing PUBLIC actor definition")

    perm_list = rp.get("permissions", [])
    perm_codes: set[str] = set()
    for p in perm_list:
        c = p["code"]
        if c in perm_codes:
            issues.append(f"K5 duplicate permission code {c!r}")
        perm_codes.add(c)

    role_grants = rp.get("role_grants", {})
    if set(role_grants.keys()) != all_actor_codes:
        issues.append(f"K5 role_grants keys mismatch vs actors+roles: {sorted(role_grants.keys())}")

    for role_name, grant in role_grants.items():
        for perm in grant.get("permissions", []):
            if perm not in perm_codes:
                issues.append(f"K5 role_grants[{role_name}] uses undefined permission {perm!r}")

    admin_perms = set(role_grants.get("SYSTEM_ADMIN", {}).get("permissions", []))
    forbidden_admin_perms = {
        "prices.verify",
        "prices.publish",
        "contracts.approve",
        "reconciliations.resolve",
        "invoices.create",
        "invoices.verify",
        "invoices.issue",
        "payments.approve",
        "payments.record",
        "payments.verify",
    }
    if admin_perms & forbidden_admin_perms:
        issues.append(f"K5 BR-SYS-002 violation: SYSTEM_ADMIN holds business permissions {sorted(admin_perms & forbidden_admin_perms)}")

    ops = extract_oas_operations(oa)
    matrix = rp.get("operation_access_matrix", [])
    matrix_by_id: dict[str, dict[str, Any]] = {}
    for row in matrix:
        oid = row["operationId"]
        if oid in matrix_by_id:
            issues.append(f"K5 duplicate operationId in operation_access_matrix: {oid}")
        matrix_by_id[oid] = row

    if set(matrix_by_id.keys()) != set(ops.keys()):
        missing_in_matrix = sorted(set(ops.keys()) - set(matrix_by_id.keys()))
        extra_in_matrix = sorted(set(matrix_by_id.keys()) - set(ops.keys()))
        issues.append(
            f"K5 1:1 bijection failed: missing in matrix={missing_in_matrix}, extra in matrix={extra_in_matrix}"
        )

    for oid, oa_entry in ops.items():
        row = matrix_by_id.get(oid)
        if not row:
            continue
        if row["method"] != oa_entry["method"] or row["path"] != oa_entry["path"]:
            issues.append(
                f"K5 {oid} method/path mismatch: rp=({row['method']} {row['path']}) vs oa=({oa_entry['method']} {oa_entry['path']})"
            )
        for perm in row.get("required_permissions", []):
            if perm not in perm_codes:
                issues.append(f"K5 {oid} uses undefined required_permission {perm!r}")
        for role in row.get("allowed_roles", []):
            if role not in all_actor_codes:
                issues.append(f"K5 {oid} uses undefined allowed_role {role!r}")

        is_mutation = row["method"] in {"POST", "PUT", "PATCH", "DELETE"}
        if row["path"].startswith("/health/") or row["path"].startswith("/api/v1/public/") or row["path"] in {"/api/v1/auth/csrf", "/api/v1/auth/login"}:
            if row["auth_required"] is not False:
                issues.append(f"K5 {oid} should have auth_required: false")
        else:
            if row["auth_required"] is not True:
                issues.append(f"K5 {oid} should have auth_required: true")
            if is_mutation and row["csrf_required"] is not True:
                issues.append(f"K5 internal mutation {oid} must require CSRF")
            if is_mutation and not oa_entry["op"].get("security"):
                issues.append(f"K5 OpenAPI operation {oid} missing security requirement")
            if "SYSTEM_ADMIN" in row.get("allowed_roles", []) and oid not in {
                "logoutUser", "getCurrentUser", "listUsers", "createUser", "updateUserAccess",
                "listSystemRuleVersions", "createSystemRuleVersion", "listAuditEvents", "getSystemObservabilitySummary"
            }:
                issues.append(f"K5 BR-SYS-002 violation: SYSTEM_ADMIN allowed on non-admin op {oid}")

    return issues


def check_k6_fixtures(
    fixtures: dict[str, Any], oa: dict[str, Any], rp: dict[str, Any], sc: dict[str, Any]
) -> list[str]:
    issues: list[str] = []

    schema_checks: list[tuple[str, str, str]] = [
        ("actors.json", "authenticated_users", "AuthenticatedUser"),
        ("public-prices.json", "price_sources", "PriceSource"),
        ("public-prices.json", "price_categories", "PriceCategory"),
        ("public-prices.json", "mill_price_quotes", "InternalPriceQuote"),
        ("public-prices.json", "disbun_reference_prices", "PublicDisbunPrice"),
        ("mills.json", "mill_companies", "MillCompany"),
        ("mills.json", "mills", "Mill"),
        ("mills.json", "public_notices", "PublicNotice"),
        ("master-data.json", "cooperatives", "Cooperative"),
        ("master-data.json", "farmers", "Farmer"),
        ("master-data.json", "farms", "Farm"),
        ("master-data.json", "vehicles", "Vehicle"),
        ("master-data.json", "drivers", "Driver"),
        ("tbs-receipts.json", "tbs_receipts", "TbsReceipt"),
        ("contracts-quota.json", "trade_contracts", "TradeContract"),
        ("contracts-quota.json", "quota_reservations", "QuotaReservation"),
        ("delivery-orders.json", "delivery_orders", "DeliveryOrder"),
        ("mill-tickets.json", "mill_weighing_tickets", "MillWeighingTicket"),
        ("reconciliations.json", "system_rule_versions", "SystemRuleVersion"),
        ("reconciliations.json", "reconciliation_cases", "ReconciliationCase"),
        ("invoices-payments.json", "file_assets", "FileAsset"),
        ("invoices-payments.json", "invoices", "Invoice"),
    ]

    for fname, key, schema_name in schema_checks:
        data = fixtures.get(fname, {})
        items = data.get(key, [])
        if not items:
            issues.append(f"K6 {fname}.{key} is empty")
        for idx, item in enumerate(items):
            issues.extend(validate_against_oas_schema(item, schema_name, oa, f"{fname}.{key}[{idx}]"))

    issues.extend(
        validate_against_oas_schema(
            fixtures["mills.json"]["public_profile"], "PublicProfile", oa, "mills.json.public_profile"
        )
    )
    issues.extend(
        validate_against_oas_schema(
            fixtures["public-prices.json"]["empty_public_prices_envelope"],
            "PublicPriceListEnvelope",
            oa,
            "public-prices.json.empty_public_prices_envelope",
        )
    )
    for idx, scen in enumerate(fixtures["error-scenarios.json"]["scenarios"]):
        issues.extend(
            validate_against_oas_schema(
                scen["error_response"],
                "ErrorResponse",
                oa,
                f"error-scenarios.json.scenarios[{idx}]",
            )
        )

    # Actor permissions parity check vs role-permissions.yaml
    role_grants = rp["role_grants"]
    pub_perms = set(fixtures["actors.json"]["public_visitor"]["permissions"])
    if pub_perms != set(role_grants["PUBLIC"]["permissions"]):
        issues.append("K6 actors.json public_visitor permissions mismatch role_grants.PUBLIC")
    for u in fixtures["actors.json"]["authenticated_users"]:
        expected_perms: set[str] = set()
        for r in u["roles"]:
            expected_perms |= set(role_grants[r]["permissions"])
        if set(u["permissions"]) != expected_perms:
            issues.append(f"K6 user {u['username']} permissions differ from role_grants for {u['roles']}")
        if "SYSTEM_ADMIN" in u["roles"] and u.get("non_approver_admin") is not True:
            issues.append(f"K6 SYSTEM_ADMIN fixture {u['username']} missing non_approver_admin=true")

    # Cross-file Foreign Key Integrity
    coop_ids = {c["id"] for c in fixtures["master-data.json"]["cooperatives"]}
    farmer_ids = {f["id"] for f in fixtures["master-data.json"]["farmers"]}
    farm_ids = {f["id"] for f in fixtures["master-data.json"]["farms"]}
    vehicle_ids = {v["id"] for v in fixtures["master-data.json"]["vehicles"]}
    driver_ids = {d["id"] for d in fixtures["master-data.json"]["drivers"]}
    mill_co_ids = {m["id"] for m in fixtures["mills.json"]["mill_companies"]}
    mill_ids = {m["id"] for m in fixtures["mills.json"]["mills"]}
    source_ids = {s["id"] for s in fixtures["public-prices.json"]["price_sources"]}
    cat_ids = {c["id"] for c in fixtures["public-prices.json"]["price_categories"]}
    receipt_ids = {r["id"] for r in fixtures["tbs-receipts.json"]["tbs_receipts"]}
    contract_ids = {c["id"] for c in fixtures["contracts-quota.json"]["trade_contracts"]}
    quota_period_ids = {
        qp["id"]
        for c in fixtures["contracts-quota.json"]["trade_contracts"]
        for qp in c.get("quota_periods", [])
    }
    do_ids = {d["id"] for d in fixtures["delivery-orders.json"]["delivery_orders"]}
    ticket_ids = {t["id"] for t in fixtures["mill-tickets.json"]["mill_weighing_tickets"]}
    rule_ids = {rv["id"] for rv in fixtures["reconciliations.json"]["system_rule_versions"]}
    recon_ids = {r["id"] for r in fixtures["reconciliations.json"]["reconciliation_cases"]}
    file_ids = {fa["id"] for fa in fixtures["invoices-payments.json"]["file_assets"]}
    party_ids = {p["id"] for p in fixtures["actors.json"]["parties"]}

    for m in fixtures["mills.json"]["mills"]:
        if m["mill_company_id"] not in mill_co_ids:
            issues.append(f"K6 mill {m['id']} broken mill_company_id FK")
    for q in fixtures["public-prices.json"]["mill_price_quotes"]:
        if q["mill_id"] not in mill_ids or q["price_category_id"] not in cat_ids or q["source_id"] not in source_ids:
            issues.append(f"K6 price_quote {q['id']} broken FK")
    for f in fixtures["master-data.json"]["farmers"]:
        if f["cooperative_id"] not in coop_ids:
            issues.append(f"K6 farmer {f['id']} broken cooperative_id FK")
    for fm in fixtures["master-data.json"]["farms"]:
        if fm["farmer_id"] not in farmer_ids:
            issues.append(f"K6 farm {fm['id']} broken farmer_id FK")
    for r in fixtures["tbs-receipts.json"]["tbs_receipts"]:
        if r["farmer_id"] not in farmer_ids or r["farm_id"] not in farm_ids or r["cooperative_id"] not in coop_ids:
            issues.append(f"K6 receipt {r['id']} broken FK")
        cw = r.get("current_weighing")
        if cw:
            gross = Decimal(cw["gross_weight_kg"])
            tare = Decimal(cw["tare_weight_kg"])
            net = Decimal(cw["net_weight_kg"])
            if gross - tare != net:
                issues.append(f"K6 receipt {r['id']} gross-tare != net ({gross}-{tare}!={net})")
            ded = sum((Decimal(g.get("deduction_weight_kg") or "0") for g in r.get("grading_items", [])), Decimal("0"))
            after = Decimal(r["net_weight_after_grading_kg"])
            if net - ded != after:
                issues.append(f"K6 receipt {r['id']} net_weight_after_grading_kg mismatch ({net}-{ded}!={after})")

    for c in fixtures["contracts-quota.json"]["trade_contracts"]:
        if c["mill_id"] not in mill_ids:
            issues.append(f"K6 contract {c['id']} broken mill_id FK")
        for qp in c.get("quota_periods", []):
            lim = Decimal(qp["quota_limit_kg"])
            res = Decimal(qp["active_reserved_kg"])
            rel = Decimal(qp["consumed_weight_kg"])
            rem = Decimal(qp["available_quota_kg"])
            if lim - res - rel != rem:
                issues.append(f"K6 quota_period {qp['id']} available != limit-reserved-consumed")
    for qr in fixtures["contracts-quota.json"]["quota_reservations"]:
        if qr["quota_period_id"] not in quota_period_ids or qr["delivery_order_id"] not in do_ids:
            issues.append(f"K6 quota_reservation {qr['id']} broken FK")

    for do in fixtures["delivery-orders.json"]["delivery_orders"]:
        if (
            do["cooperative_id"] not in coop_ids
            or do["mill_id"] not in mill_ids
            or do["contract_id"] not in contract_ids
            or do["vehicle_id"] not in vehicle_ids
            or do["driver_id"] not in driver_ids
        ):
            issues.append(f"K6 delivery_order {do['id']} broken header FK")
        for ln in do.get("lines", []):
            if ln["receipt_id"] not in receipt_ids:
                issues.append(f"K6 delivery_order {do['id']} line broken receipt_id FK")

    for t in fixtures["mill-tickets.json"]["mill_weighing_tickets"]:
        if t["delivery_order_id"] not in do_ids or t["mill_id"] not in mill_ids:
            issues.append(f"K6 mill_ticket {t['id']} broken FK")
        if t.get("proof_file_id") and t["proof_file_id"] not in file_ids:
            issues.append(f"K6 mill_ticket {t['id']} broken proof_file_id FK")
        if Decimal(t["gross_weight_kg"]) - Decimal(t["tare_weight_kg"]) != Decimal(t["net_weight_kg"]):
            issues.append(f"K6 mill_ticket {t['id']} gross-tare != net")

    for rc in fixtures["reconciliations.json"]["reconciliation_cases"]:
        if rc["delivery_order_id"] not in do_ids or rc["rule_version_id"] not in rule_ids:
            issues.append(f"K6 reconciliation {rc['id']} broken delivery_order/rule FK")
        if rc["status"] == "WAITING_TICKET":
            if rc["mill_ticket_id"] is not None or rc["calculated_at"] is not None:
                issues.append(f"K6 WAITING_TICKET reconciliation {rc['id']} must have null mill_ticket_id and calculated_at")
            continue
        if rc["mill_ticket_id"] not in ticket_ids:
            issues.append(f"K6 reconciliation {rc['id']} broken mill_ticket_id FK")
        orig = Decimal(rc["origin_weight_kg"])
        mill = Decimal(rc["mill_weight_kg"])
        diff = Decimal(rc["difference_weight_kg"])
        if orig - mill != diff:
            issues.append(f"K6 reconciliation {rc['id']} origin-mill != diff")
        if orig < mill and rc["is_negative_difference"] is not True:
            issues.append(f"K6 reconciliation {rc['id']} origin<mill missing is_negative_difference=true")
        allocs = rc.get("farmer_allocations", [])
        if allocs:
            for al in allocs:
                if al["farmer_id"] not in farmer_ids or al["receipt_id"] not in receipt_ids:
                    issues.append(f"K6 reconciliation {rc['id']} allocation broken FK")

    for inv in fixtures["invoices-payments.json"]["invoices"]:
        if (
            inv["creditor_party_id"] not in party_ids
            or inv["debtor_party_id"] not in party_ids
            or inv["business_model_rule_version_id"] not in rule_ids
        ):
            issues.append(f"K6 invoice {inv['id']} broken party/rule FK")
        if inv.get("reconciliation_case_id") and inv["reconciliation_case_id"] not in recon_ids:
            issues.append(f"K6 invoice {inv['id']} broken reconciliation_case_id FK")
        gross = Decimal(inv["gross_amount"])
        ded = Decimal(inv["deduction_amount"])
        total = Decimal(inv["total_amount"])
        if gross - ded != total:
            issues.append(f"K6 invoice {inv['id']} gross - deduction != total")
        if inv.get("lines"):
            line_sum = sum((Decimal(ln["line_amount"]) for ln in inv["lines"]), Decimal("0"))
            if line_sum != gross:
                issues.append(f"K6 invoice {inv['id']} lines sum ({line_sum}) != gross ({gross})")
        for pay in inv.get("payments", []):
            if pay.get("proof_file_id") and pay["proof_file_id"] not in file_ids:
                issues.append(f"K6 payment {pay['id']} broken proof_file_id FK")

    # Negative scenario coverage check
    covered_error_codes = {s["error_response"]["error"]["code"] for s in fixtures["error-scenarios.json"]["scenarios"]}
    required_neg_codes = {
        "AUTH_REQUIRED",
        "AUTH_INVALID_CREDENTIALS",
        "AUTH_CSRF_INVALID",
        "AUTH_OPERATION_FORBIDDEN",
        "AUTH_SCOPE_FORBIDDEN",
        "AUTH_CONFLICT_OF_DUTIES",
        "CONTRACT_QUOTA_EXCEEDED",
        "IDM_KEY_CONFLICT_PAYLOAD_MISMATCH",
        "FIN_DISPUTE_HOLD_BLOCKED",
        "PAY_PARTIAL_NOT_SUPPORTED",
        "FIN_POLICY_UNCONFIRMED",
        "REC_NEGATIVE_DIFFERENCE_HOLD",
        "TBS_RECEIPT_LOCKED",
        "MD_STALE_RECORD_VERSION",
    }
    missing_neg = sorted(required_neg_codes - covered_error_codes)
    if missing_neg:
        issues.append(f"K6 error-scenarios.json missing key negative test scenarios: {missing_neg}")

    # Security/secret leakage hygiene check across all fixtures
    serialized = json.dumps(fixtures)
    for bad_token in ("$argon2id$", "sk-live-", "password_hash", "Bearer eyJ"):
        if bad_token in serialized:
            issues.append(f"K6 forbidden sensitive token/field string {bad_token!r} found in fixtures")

    return issues


def check_k7_traceability(oa: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if not TRACEABILITY_FILE.exists():
        issues.append(f"K7 missing traceability matrix: {TRACEABILITY_FILE.relative_to(REPO_ROOT)}")
        return issues

    text = TRACEABILITY_FILE.read_text(encoding="utf-8")
    ops = extract_oas_operations(oa)
    missing_ops = [oid for oid in ops if oid not in text]
    if missing_ops:
        issues.append(f"K7 traceability matrix missing OpenAPI operations: {missing_ops[:10]} (total {len(missing_ops)})")

    required_routes = [
        "/", "/harga-tbs", "/pks/:id", "/lokasi-pks", "/tentang", "/kemitraan", "/kontak", "/login",
        "/app/petani", "/app/petani/panen",
        "/app/koperasi", "/app/koperasi/penerimaan", "/app/koperasi/surat-jalan",
        "/app/perumda", "/app/perumda/harga", "/app/perumda/kontrak",
        "/app/perumda/logistik", "/app/perumda/rekonsiliasi", "/app/perumda/pembayaran",
        "/app/pks", "/app/pks/tiket-timbang",
        "/app/direksi", "/app/direksi/persetujuan",
        "/app/admin", "/app/admin/pengguna", "/app/admin/audit",
    ]
    missing_routes = [r for r in required_routes if r not in text]
    if missing_routes:
        issues.append(f"K7 traceability matrix missing AFD §36 routes: {missing_routes}")

    for flow_num in range(1, 25):
        tag = f"FLOW-{flow_num:02d}"
        if tag not in text:
            issues.append(f"K7 traceability matrix missing {tag}")

    for biz_num in range(1, 31):
        tag = f"BIZ-{biz_num:03d}"
        if tag not in text:
            issues.append(f"K7 traceability matrix missing {tag}")

    prd_fr_ranges = [
        ("FR-PUB", 7), ("FR-MD", 5), ("FR-HRG", 7), ("FR-TBS", 5),
        ("FR-KTR", 4), ("FR-LOG", 6), ("FR-PKS", 5), ("FR-REC", 10), ("FR-DSH", 7),
    ]
    for prefix, count in prd_fr_ranges:
        for i in range(1, count + 1):
            code = f"{prefix}-{i:03d}"
            if code not in text:
                issues.append(f"K7 traceability matrix missing {code}")

    for i in range(1, 21):
        nfr = f"NFR-{i:03d}"
        if nfr not in text:
            issues.append(f"K7 traceability matrix missing {nfr}")

    return issues


def check_k8_openapi_typescript() -> list[str]:
    issues: list[str] = []
    npx_bin = shutil.which("npx.cmd") or shutil.which("npx")
    if not npx_bin:
        issues.append("K8 npx not available in PATH")
        return issues

    with tempfile.TemporaryDirectory() as tmpdir:
        out_dts = Path(tmpdir) / "openapi-types.d.ts"
        cmd = [npx_bin, "--yes", "openapi-typescript", str(CONTRACTS_DIR / "openapi.v1.yaml"), "-o", str(out_dts)]
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            issues.append(f"K8 openapi-typescript exited {proc.returncode}: {proc.stderr or proc.stdout}")
            return issues
        if not out_dts.exists() or out_dts.stat().st_size < 10000:
            issues.append("K8 openapi-typescript output missing or unexpectedly small")
            return issues
        content = out_dts.read_text(encoding="utf-8")
        for expected in ("paths", "components", "PublicPriceQuote", "ReconciliationCase", "ErrorResponse"):
            if expected not in content:
                issues.append(f"K8 generated .d.ts missing {expected!r}")
    return issues


def check_k9_backend_readiness(oa: dict[str, Any], ec: dict[str, Any], sc: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    schemas = oa["components"]["schemas"]
    decimal_schemas = [
        "DecimalKgString", "NonNegativeDecimalKgString", "DecimalPriceString",
        "DecimalMoneyString", "DecimalPercentString", "DecimalAreaString",
        "NullableLatitudeString", "NullableLongitudeString",
    ]
    for sname in decimal_schemas:
        sdef = schemas.get(sname)
        if not sdef:
            issues.append(f"K9 missing decimal schema {sname}")
            continue
        stype = sdef.get("type")
        is_str = stype == "string" or (isinstance(stype, list) and "string" in stype)
        if not is_str or not sdef.get("pattern"):
            issues.append(f"K9 {sname} must represent numeric quantity as regex-validated string (avoid float)")

    # Verify health endpoints are present without auth
    paths = oa["paths"]
    for hp in ("/health/live", "/health/ready"):
        if hp not in paths or "get" not in paths[hp]:
            issues.append(f"K9 missing required health probe {hp}")

    # Verify Pending SOP flags exist in key contracts
    if "PolicyClassification" not in schemas:
        issues.append("K9 missing PolicyClassification enum in OpenAPI")
    ec_codes = {e["code"] for e in ec["errors"]}
    for sop_err in ("FIN_POLICY_UNCONFIRMED", "REC_ALLOCATION_POLICY_UNCONFIRMED"):
        if sop_err not in ec_codes:
            issues.append(f"K9 missing Pending SOP error {sop_err}")

    return issues


PROTECTED_CONTRACT_PATHS: tuple[str, ...] = (
    "contracts/openapi.v1.yaml",
    "contracts/error-catalog.yaml",
    "contracts/state-catalog.yaml",
    "contracts/role-permissions.yaml",
    "contracts/fixtures",
)

PROTECTED_V11_DOCS: tuple[str, ...] = (
    "docs/PRD.md",
    "docs/TRD.md",
    "docs/AFD.md",
    "docs/DBD.md",
    "docs/BSD.md",
    "docs/IPD.md",
)


def detect_development_phase(checkpoint_text: str) -> str:
    """Detect active repository phase from IMPLEMENTATION_CHECKPOINTS.md headings."""
    if "## FRONTEND DEVELOPMENT TRACK" in checkpoint_text:
        return "FRONTEND"
    if "# BACKEND DEVELOPMENT TRACK" in checkpoint_text:
        return "BACKEND"
    return "M0"


def check_k10_scope_hygiene(
    repo_root: Path | None = None,
    checkpoint_text: str | None = None,
    check_git_baseline: bool = True,
) -> list[str]:
    """Validate phase directory boundaries and guard protected contracts & V1.1 baseline."""
    issues: list[str] = []
    root = repo_root or REPO_ROOT

    if checkpoint_text is None:
        cp_file = root / "docs" / "IMPLEMENTATION_CHECKPOINTS.md"
        checkpoint_text = cp_file.read_text(encoding="utf-8") if cp_file.exists() else ""

    phase = detect_development_phase(checkpoint_text)
    if phase == "M0":
        forbidden_dirs: tuple[str, ...] = ("backend", "frontend", "alembic", "infra")
    elif phase == "BACKEND":
        forbidden_dirs = ("frontend", "alembic")
    else:
        # Stray root alembic/ remains disallowed; canonical migrations reside in backend/alembic/.
        forbidden_dirs = ("alembic",)

    for d in forbidden_dirs:
        if (root / d).exists():
            issues.append(f"K10 forbidden directory exists during {phase} track: {d}/")

    if phase in ("BACKEND", "FRONTEND") and (root / "backend").exists():
        if not (root / "backend" / "alembic" / "versions").exists():
            issues.append("K10 missing canonical backend/alembic/versions directory")

    if phase == "FRONTEND" and (root / "frontend").exists():
        for req_rel in ("frontend/package.json", "frontend/src/lib/api/generated.d.ts"):
            if not (root / req_rel).exists():
                issues.append(f"K10 missing required Frontend Track artifact: {req_rel}")

    for doc_rel in PROTECTED_V11_DOCS:
        doc_path = root / doc_rel
        if (root / "docs").exists() and (not doc_path.exists() or doc_path.stat().st_size == 0):
            issues.append(f"K10 missing or empty protected baseline document: {doc_rel}")

    if check_git_baseline and (root / ".git").exists():
        git_bin = shutil.which("git")
        if git_bin:
            targets = list(PROTECTED_CONTRACT_PATHS) + list(PROTECTED_V11_DOCS)
            proc = subprocess.run(
                [git_bin, "status", "--porcelain", "--", *targets],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=15,
            )
            if proc.returncode != 0:
                issues.append(f"K10 git baseline check failed: {proc.stderr.strip()}")
            else:
                for line in proc.stdout.splitlines():
                    if line.strip():
                        issues.append(
                            f"K10 unauthorized modification to protected contract/V1.1 baseline: {line.strip()}"
                        )

    return issues


CANONICAL_DBD_TABLES: tuple[str, ...] = (
    "user_accounts", "roles", "permissions", "role_permissions", "user_role_grants",
    "user_access_scopes", "auth_sessions",
    "parties", "farmers", "farms", "cooperatives", "cooperative_memberships",
    "mill_companies", "mills", "perumda_offices", "vehicles", "drivers",
    "price_sources", "price_categories", "mill_price_quotes", "price_verification_events",
    "disbun_reference_prices",
    "tbs_receipts", "receipt_weighing_revisions", "receipt_grading_items",
    "trade_contracts", "contract_quota_periods", "quota_reservations",
    "delivery_orders", "delivery_order_lines", "delivery_status_events",
    "mill_weighing_tickets", "mill_grading_items",
    "reconciliation_cases", "dispute_reviews", "farmer_settlement_allocations",
    "invoices", "invoice_lines", "payment_approvals", "payment_records",
    "public_pages", "public_notices", "file_assets", "audit_events",
    "idempotency_records", "outbox_events", "system_rule_versions", "user_notifications",
)


def check_k11_handoff_doc_consistency(oa: dict[str, Any], rp: dict[str, Any]) -> list[str]:
    """Automated M0.1 regression checks across docs/m0/, docs/adr/, checkpoints, and contracts."""
    issues: list[str] = []

    # 1. Verify all 48 canonical DBD §4 tables exist in M0_REQUIREMENT_TRACEABILITY.md
    trace_txt = TRACEABILITY_FILE.read_text(encoding="utf-8") if TRACEABILITY_FILE.exists() else ""
    missing_tables = [tbl for tbl in CANONICAL_DBD_TABLES if tbl not in trace_txt]
    if missing_tables:
        issues.append(f"K11 missing canonical DBD tables in traceability: {missing_tables}")

    # 2. Forbid legacy/wrong table identifiers & React Router across M0 docs, ADRs, checkpoints, contracts
    scan_paths = (
        sorted((DOCS_DIR / "m0").glob("*.md"))
        + sorted((DOCS_DIR / "adr").glob("*.md"))
        + [DOCS_DIR / "IMPLEMENTATION_CHECKPOINTS.md"]
        + sorted(CONTRACTS_DIR.glob("*.yaml"))
    )
    banned_patterns = [
        (r"`users`", "non-canonical table identifier `users` (expected `user_accounts`)"),
        (r"`user_roles`", "non-canonical table identifier `user_roles` (expected `user_role_grants`)"),
        (r"\breceipt_weighing_records\b", "non-canonical table identifier receipt_weighing_records"),
        (r"\bdelivery_order_items\b", "non-canonical table identifier delivery_order_items"),
        (r"\bdelivery_order_status_events\b", "non-canonical table identifier delivery_order_status_events"),
        (r"\bReact Router\b", "disallowed router React Router (TRD/ADR-006 specify TanStack Router)"),
    ]
    for path in scan_paths:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(content.splitlines(), 1):
            for pat, reason in banned_patterns:
                if re.search(pat, line):
                    issues.append(f"K11 {path.relative_to(REPO_ROOT)}:{lineno} -> {reason}")

    # 3. Verify TanStack Router is stated consistently
    for rpath in (
        DOCS_DIR / "adr" / "ADR-006-atomic-design-frontend.md",
        DOCS_DIR / "m0" / "M0_HANDOFF.md",
        DOCS_DIR / "IMPLEMENTATION_CHECKPOINTS.md",
    ):
        if not rpath.exists() or "TanStack Router" not in rpath.read_text(encoding="utf-8"):
            issues.append(f"K11 missing TanStack Router reference in {rpath.relative_to(REPO_ROOT)}")

    # 4. Operation counts by category & auth parity
    oas_ops = extract_oas_operations(oa)
    health_ops = [oid for oid, info in oas_ops.items() if info["path"].startswith("/health/")]
    public_ops = [oid for oid, info in oas_ops.items() if info["path"].startswith("/api/v1/public/")]
    auth_unauth_ops = [
        oid for oid, info in oas_ops.items()
        if info["path"].startswith("/api/v1/auth/") and not info["op"].get("security")
    ]
    auth_internal_ops = [
        oid for oid, info in oas_ops.items()
        if info["path"].startswith("/api/v1/auth/") and bool(info["op"].get("security"))
    ]
    internal_biz_ops = [
        oid for oid, info in oas_ops.items()
        if not info["path"].startswith(("/health/", "/api/v1/public/", "/api/v1/auth/"))
    ]
    if (
        len(health_ops), len(public_ops), len(auth_unauth_ops), len(auth_internal_ops), len(internal_biz_ops)
    ) != (2, 7, 2, 2, 82):
        issues.append(
            f"K11 unexpected OpenAPI category breakdown: {(len(health_ops), len(public_ops), len(auth_unauth_ops), len(auth_internal_ops), len(internal_biz_ops))}"
        )

    handoff_path = DOCS_DIR / "m0" / "M0_HANDOFF.md"
    handoff_txt = handoff_path.read_text(encoding="utf-8") if handoff_path.exists() else ""
    if "84" not in handoff_txt or "82" not in handoff_txt or "95" not in handoff_txt or "91 endpoint" in handoff_txt:
        issues.append("K11 M0_HANDOFF.md operation counts not aligned to verified 95 total (11 unauth / 84 auth = 2+82)")

    # 5. Idempotency 1:1 bijection (OpenAPI <-> role-permissions <-> ADR-010 & M0_HANDOFF & Decision Register)
    oa_idem: set[str] = set()
    for oid, info in oas_ops.items():
        path_item = oa["paths"][info["path"]]
        params = list(path_item.get("parameters", [])) + list(info["op"].get("parameters", []))
        if any(
            isinstance(p, dict) and (p.get("$ref", "").endswith("IdempotencyKeyHeader") or p.get("name") == "Idempotency-Key")
            for p in params
        ):
            oa_idem.add(oid)
    rp_idem = {row["operationId"] for row in rp["operation_access_matrix"] if row.get("idempotency_required")}
    if oa_idem != rp_idem or len(oa_idem) != 8:
        issues.append(f"K11 Idempotency bijection failed: oa={sorted(oa_idem)} vs rp={sorted(rp_idem)}")

    for doc_path in (
        DOCS_DIR / "adr" / "ADR-010-idempotency-concurrency-pending-sop.md",
        DOCS_DIR / "m0" / "M0_DECISION_REGISTER.md",
        handoff_path,
    ):
        dtxt = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
        missing_idem = sorted(oid for oid in oa_idem if oid not in dtxt)
        if missing_idem or "7 mutasi" in dtxt or "8" not in dtxt:
            issues.append(f"K11 idempotency mismatch in {doc_path.relative_to(REPO_ROOT)}: missing={missing_idem}")

    # 6. M0-CNF-05 Decision Register consistency
    audit_txt = (DOCS_DIR / "m0" / "M0_DOCUMENT_AUDIT.md").read_text(encoding="utf-8")
    reg_txt = (DOCS_DIR / "m0" / "M0_DECISION_REGISTER.md").read_text(encoding="utf-8")
    if "PROPOSED" in audit_txt or "| **CNF-05**" not in audit_txt or "| **M0-CNF-05**" not in reg_txt:
        issues.append("K11 M0-CNF-05 status inconsistency (must be RESOLVED without lingering PROPOSED)")

    return issues


def run_all_checks() -> tuple[dict[str, list[str]], int]:
    results: dict[str, list[str]] = {}
    loaded, k1_issues = check_k1_syntax_and_unique_keys()
    results["K1_syntax_and_unique_keys"] = k1_issues
    if k1_issues:
        return results, 1

    oa = loaded["yaml"]["openapi.v1.yaml"]
    ec = loaded["yaml"]["error-catalog.yaml"]
    sc = loaded["yaml"]["state-catalog.yaml"]
    rp = loaded["yaml"]["role-permissions.yaml"]
    fixtures = loaded["json"]

    results["K2_openapi_validation"] = check_k2_openapi(oa)
    results["K3_error_catalog_consistency"] = check_k3_error_catalog(ec, oa, sc, fixtures["error-scenarios.json"])
    results["K4_state_catalog_consistency"] = check_k4_state_catalog(sc, ec, oa, rp)
    results["K5_role_permission_matrix"] = check_k5_role_permissions(rp, oa)
    results["K6_fixture_schema_and_crossref"] = check_k6_fixtures(fixtures, oa, rp, sc)
    results["K7_traceability_completeness"] = check_k7_traceability(oa)
    results["K8_frontend_openapi_typescript"] = check_k8_openapi_typescript()
    results["K9_backend_contract_readiness"] = check_k9_backend_readiness(oa, ec, sc)
    results["K10_scope_and_hygiene"] = check_k10_scope_hygiene()
    results["K11_m0_1_handoff_doc_consistency"] = check_k11_handoff_doc_consistency(oa, rp)

    total_issues = sum(len(v) for v in results.values())
    return results, total_issues


def main() -> int:
    results, total_issues = run_all_checks()
    print("=== M0 CONTRACT VALIDATION SUMMARY ===")
    for name, issues in results.items():
        status = "PASS" if not issues else f"FAIL ({len(issues)})"
        print(f"[{status}] {name}")
        for msg in issues:
            print(f"  - {msg}")
    print(f"TOTAL ISSUES: {total_issues}")
    return 0 if total_issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
