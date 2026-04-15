from __future__ import annotations

import json
import os
from datetime import datetime

from analyzer.ci_policy_loader import load_ci_policy
from datetime import datetime, timezone


def main():
    # -------------------------
    # Load report
    # -------------------------
    with open("reports/output.json") as f:
        data = json.load(f)

    # -------------------------
    # Load CI policy
    # -------------------------
    policy = load_ci_policy()

    ci_control = policy.get("ci_control", {})
    override_config = ci_control.get("override", {})
    review_behavior = ci_control.get("review_behavior", {})
    logging_config = ci_control.get("logging", {})

    override_enabled = override_config.get("enabled", False)
    allowed_users = override_config.get("allowed_users", [])

    block_on_review = review_behavior.get("block_on_needs_review", True)
    require_override = review_behavior.get("require_override", True)

    log_enabled = logging_config.get("enabled", True)
    include_user = logging_config.get("include_user", True)
    include_timestamp = logging_config.get("include_timestamp", True)

    # -------------------------
    # Runtime context
    # -------------------------
    actor = os.getenv("GITHUB_ACTOR", "unknown")
    override = os.getenv("AUTODOC_OVERRIDE") == "true"

    has_review = any(r["final_status"] == "NEEDS REVIEW" for r in data)

    # -------------------------
    # Logging helper
    # -------------------------
    def log(message: str):
        if not log_enabled:
            return

        parts = []

        if include_timestamp:
            parts.append(datetime.now(timezone.utc).isoformat())

        if include_user:
            parts.append(f"user={actor}")

        parts.append(message)

        log_line = " | ".join(parts)

        print(log_line)

        # Guardar en archivo persistente
        with open("reports/override.log", "a") as f:
            f.write(log_line + "\n")

    # -------------------------
    # Main logic
    # -------------------------
    if has_review:

        log("NEEDS REVIEW detected")

        if not block_on_review:
            log("Review does not block merge (policy)")
            return

        if not override_enabled:
            log("Override disabled by policy")
            exit(1)

        if require_override and not override:
            log("Override required but not provided")
            exit(1)

        if override and actor not in allowed_users:
            log(f"Override denied for user: {actor}")
            exit(1)

        if override and actor in allowed_users:
            log(f"Override approved by authorized user: {actor}")
            return

    # -------------------------
    # No review needed
    # -------------------------
    log("No review required - passing check")


if __name__ == "__main__":
    main()