from __future__ import annotations

from typing import Any


def build_prompt(method: dict[str, Any]) -> str:
    jd = method["javadoc"]

    description = jd["description"] or "No description"
    params = _format_params(jd["params"])
    return_text = jd["return"] or "None"
    code = method["method_body"]

    return f"""
Evaluate consistency between Javadoc and Java method implementation.

Return ONLY one of the following formats:

CONSISTENT

INCONSISTENT: <short explanation>

UNCERTAIN: <short explanation>

Do not add extra text. Do not explain unless required.

---

JAVADOC:
{description}

PARAMS:
{params}

RETURN:
{return_text}

---

CODE:
{code}
""".strip()


def _format_params(params: list[dict[str, Any]]) -> str:
    if not params:
        return "None"

    return "\n".join(
        f"{p['name']}: {p['description']}" for p in params
    )