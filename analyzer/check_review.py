from __future__ import annotations

import json
import os
import requests
from datetime import datetime, timezone


def is_pr_approved():
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")

    if not token or not repo or not pr_number:
        return False

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return False

    reviews = response.json()

    for review in reviews:
        if review["state"] == "APPROVED":
            return True

    return False


def main():
    with open("reports/output.json") as f:
        data = json.load(f)

    actor = os.getenv("GITHUB_ACTOR", "unknown")

    has_fail = any(r["final_status"] == "FAIL" for r in data)
    has_review = any(r["final_status"] == "NEEDS REVIEW" for r in data)

    def log(msg):
        print(f"{datetime.now(timezone.utc).isoformat()} | user={actor} | {msg}")

    if has_fail:
        log("FAIL detected - blocking merge")
        exit(1)

    if has_review:
        log("NEEDS REVIEW detected")

        if is_pr_approved():
            log("PR approved - allowing merge")
            return

        log("Approval required")
        exit(1)

    log("All PASS - allowing merge")


if __name__ == "__main__":
    main()