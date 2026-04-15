from __future__ import annotations

from typing import Any

from analyzer.models import ExtractedMethod


# -------------------------
# API principal
# -------------------------
def normalize_methods(methods: list[ExtractedMethod]) -> list[dict[str, Any]]:
    return [normalize_method(method) for method in methods]


def normalize_method(method: ExtractedMethod) -> dict[str, Any]:
    return {
        "file_path": _clean_str(method.file_path),
        "class_name": _clean_str(method.class_name),
        "method_name": _clean_str(method.method_name),
        "signature": _clean_str(method.signature),
        "parameters": [_normalize_parameter(p) for p in method.parameters],
        "return_type": _clean_str(method.return_type),
        "javadoc": _normalize_javadoc(method),
        "method_body": _clean_block(method.method_body),
        "line_start": method.line_start,
        "line_end": method.line_end,
    }


# -------------------------
# Subcomponentes
# -------------------------

def _normalize_parameter(param) -> dict[str, str]:
    return {
        "name": _clean_str(param.name),
        "type": _clean_str(param.type),
    }


def _normalize_javadoc(method: ExtractedMethod) -> dict[str, Any]:
    jd = method.javadoc

    base = {
        "exists": bool(jd.exists),
        "description": _clean_str(jd.description),
        "params": [
            {
                "name": _clean_str(p.name),
                "description": _clean_str(p.description),
            }
            for p in jd.params
        ],
        "return": _clean_str(jd.return_value),
    }

    # 👉 incluir tags extendidos
    if hasattr(jd, "extra_tags"):
        for key, value in jd.extra_tags.items():
            if isinstance(value, list):
                base[key] = [_clean_str(v) for v in value]
            else:
                base[key] = _clean_str(value)

    return base


# -------------------------
# Limpieza de datos
# -------------------------

def _clean_str(value: str | None) -> str:
    if not value:
        return ""
    return value.strip()


def _clean_block(block: str | None) -> str:
    if not block:
        return ""

    cleaned = block.strip()
    lines = cleaned.splitlines()

    return "\n".join(line.rstrip() for line in lines)