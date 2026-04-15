from __future__ import annotations

import os
import json
import requests
from datetime import datetime, timezone

from analyzer.ci_policy_loader import load_ci_policy


def post_override_comment(pr_number: str):
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    actor = os.getenv("GITHUB_ACTOR")

    if not token or not repo or not pr_number:
        print("Skipping override comment (missing context)")
        return

    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    message = f"""
##AutoDoc Override Approved

Override aprobado para PR #{pr_number} por **{actor}**.

⚠ Para aplicar los cambios:

- Hacer commit vacío:
  git commit --allow-empty -m "apply override"
  git push

- O usar **Re-run jobs**
"""

    response = requests.post(url, headers=headers, json={"body": message})

    if response.status_code >= 300:
        print("Failed to post override comment:", response.text)
    else:
        print("Override comment posted successfully")


def main():
    with open("reports/output.json") as f:
        data = json.load(f)

    policy = load_ci_policy()

    actor = os.getenv("GITHUB_ACTOR", "unknown")
    pr_number = os.getenv("PR_NUMBER")
    event = os.getenv("GITHUB_EVENT_NAME")

    has_review = any(r["final_status"] == "NEEDS REVIEW" for r in data)

    def log(msg):
        print(f"{datetime.now(timezone.utc).isoformat()} | user={actor} | {msg}")

    if has_review:

        log("NEEDS REVIEW detected")

        if event == "workflow_dispatch":
            log(f"Override applied for PR {pr_number}")

            post_override_comment(pr_number)

            return

        log("Override required but not provided")
        exit(1)

    log("No review required - passing check")


if __name__ == "__main__":
    main()