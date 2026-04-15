from __future__ import annotations
import yaml
from pathlib import Path


def load_ci_policy(path: str = "policy/ci-policy.yaml") -> dict:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"CI Policy file not found: {path}")

    with file_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)