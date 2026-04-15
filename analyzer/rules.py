from __future__ import annotations

from typing import Any

from analyzer.policy_loader import load_policy

policy = load_policy()

def evaluate_method(method: dict[str, Any]) -> dict[str, Any]:
    exemptions = policy.get("exemptions", {})

    # -------------------------
    # Exemptions
    # -------------------------
    if exemptions.get("getters_setters_trivial"):
        if _is_trivial_getter_setter(method):
            return {
                "status": "PASS",
                "issues": [],
                "exempted": True  # 👈 opcional pero MUY útil
            }

    # -------------------------
    # Reglas normales
    # -------------------------
    visibility = _detect_visibility(method["signature"])
    rules = policy.get("visibility_rules", {}).get(visibility)

    if not rules:
        return {
            "status": "PASS",
            "issues": [],
            "exempted": False
        }

    issues = _apply_rules(method, rules)
    status = _resolve_status(issues)

    return {
        "status": status,
        "issues": issues,
        "exempted": False
    }

# -------------------------
# Aplicación de reglas
# -------------------------

def _apply_rules(method: dict[str, Any], rules: dict[str, Any]) -> list[dict[str, Any]]:
    issues = []

    required = rules.get("required", [])
    optional = rules.get("optional", [])
    behavior = rules.get("behavior", {})

    # Required
    for rule in required:
        result, message = _check_rule(method, rule)

        if not result:
            issues.append(
                _issue(
                    rule,
                    message,
                    behavior.get("missing_required", "error"),
                )
            )

    # Optional
    for rule in optional:
        result, message = _check_rule(method, rule)

        if not result:
            issues.append(
                _issue(
                    rule,
                    message,
                    behavior.get("missing_optional", "warning"),
                )
            )

    return issues


# -------------------------
# Evaluación de reglas
# -------------------------

def _check_rule(method: dict[str, Any], rule: str) -> tuple[bool, str]:
    jd = method["javadoc"]
    params = method["parameters"]

    # summary_text
    if rule == "summary_text":
        if not jd["description"]:
            return False, "Falta descripción en Javadoc"
        return True, ""

    # summary_text_or_purpose
    if rule == "summary_text_or_purpose":
        if not jd["description"]:
            return False, "Falta descripción del método"
        
        min_len = policy.get("defaults", {}).get("min_summary_chars", 0)
        if len(jd["description"]) < min_len:
            return False, f"La descripción es demasiado corta (mínimo {min_len} caracteres)"
        
        return True, ""

    # param_for_each
    if rule == "param_for_each":
        param_names = {p["name"] for p in params}
        doc_param_names = {p["name"] for p in jd["params"]}

        missing = param_names - doc_param_names

        if missing:
            return False, f"Falta @param para: {', '.join(missing)}"

        return True, ""

    # return_if_not_void
    if rule == "return_if_not_void":
        if method["return_type"] == "void":
            return True, ""

        if not jd["return"]:
            return False, "Falta @return en método no void"

        return True, ""

    # throws_if_present_in_signature (simplificado)
    if rule == "throws_if_present_in_signature":
        # no implementado aún → no falla
        return True, ""

    # optional no implementados aún → warning si aplica
    if rule in ["param", "return", "throws", "notes", "example", "ticket", "requirements", "sideEffects", "since"]:
        # Por ahora no validamos estos → asumimos OK
        return True, ""

    return True, ""


# -------------------------
# Helpers
# -------------------------

def _detect_visibility(signature: str) -> str:
    if signature.startswith("public"):
        return "public"
    if signature.startswith("private"):
        return "private"
    if signature.startswith("protected"):
        return "protected"
    return "package"


def _issue(rule: str, message: str, severity: str) -> dict[str, Any]:
    return {
        "rule": rule,
        "message": message,
        "severity": severity,
    }


def _resolve_status(issues: list[dict[str, Any]]) -> str:
    if any(i["severity"] == "error" for i in issues):
        return "FAIL"
    if issues:
        return "WARNING"
    return "PASS"

def _is_trivial_getter_setter(method: dict[str, Any]) -> bool:
    name = method["method_name"]
    body = method["method_body"]
    params = method["parameters"]

    lines = [line.strip() for line in body.splitlines() if line.strip()]

    # eliminar firma
    if lines:
        lines = lines[1:]

    # eliminar llaves
    lines = [line for line in lines if line not in ("{", "}")]

    # getter
    if name.startswith("get") and len(params) == 0:
        if len(lines) == 1 and lines[0].startswith("return"):
            return True

    # setter
    if name.startswith("set") and len(params) == 1:
        if len(lines) == 1 and "=" in lines[0]:
            return True

    return False