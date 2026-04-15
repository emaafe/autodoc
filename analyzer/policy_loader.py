from __future__ import annotations

import yaml
from pathlib import Path


def _get_autodoc_base_path() -> Path:
    """
    Devuelve la raíz del proyecto AutoDoc
    """
    return Path(__file__).resolve().parent.parent


def load_policy() -> dict:
    base_path = _get_autodoc_base_path()
    path = base_path / "policy" / "doc-policy.yaml"

    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)