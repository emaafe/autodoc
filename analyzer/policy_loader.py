from __future__ import annotations

import yaml
from pathlib import Path


def load_policy(path: str = "policy/doc-policy.yaml") -> dict:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Policy file not found: {path}")

    with file_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)