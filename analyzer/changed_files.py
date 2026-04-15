from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import os
import requests

from analyzer.config import (
    ALLOWED_CHANGE_STATUSES,
    GITHUB_API_URL,
    JAVA_EXTENSION,
    PRODUCTIVE_SOURCE_PREFIX,
    TEST_SOURCE_PREFIX,
)
from analyzer.utils import getenv_required


@dataclass(frozen=True)
class ChangedFile:
    filename: str
    status: str


def is_productive_java_file(path: str) -> bool:
    """
    Returns True only for Java source files under src/main/java
    and excludes test sources.
    """
    normalized = path.strip()

    return (
        normalized.endswith(JAVA_EXTENSION)
        and normalized.startswith(PRODUCTIVE_SOURCE_PREFIX)
        and not normalized.startswith(TEST_SOURCE_PREFIX)
    )


def is_supported_change_status(status: str) -> bool:
    return status in ALLOWED_CHANGE_STATUSES


def filter_analyzable_files(files: list[ChangedFile]) -> list[str]:
    """
    Applies project rules:
    - only .java
    - only productive code
    - only added/modified/renamed
    """
    result: list[str] = []

    for file in files:
        if not is_supported_change_status(file.status):
            continue

        if not is_productive_java_file(file.filename):
            continue

        result.append(file.filename)

    return result


def _build_pull_request_files_url(repo: str, pr_number: str) -> str:
    return f"{GITHUB_API_URL}/repos/{repo}/pulls/{pr_number}/files"


def fetch_changed_files_from_github() -> list[ChangedFile]:
    """
    Reads GitHub Actions environment variables and fetches files changed in the PR.

    Required environment variables:
    - GITHUB_TOKEN
    - GITHUB_REPOSITORY
    - PR_NUMBER

    Returns a flat list of ChangedFile entries.
    Handles GitHub API pagination.
    """
    token = getenv_required("GITHUB_TOKEN")
    repo = getenv_required("GITHUB_REPOSITORY")
    pr_number = getenv_required("PR_NUMBER")

    url = _build_pull_request_files_url(repo=repo, pr_number=pr_number)

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    all_files: list[ChangedFile] = []
    page = 1
    per_page = 100

    while True:
        response = requests.get(
            url,
            headers=headers,
            params={"page": page, "per_page": per_page},
            timeout=30,
        )
        response.raise_for_status()

        payload: list[dict[str, Any]] = response.json()
        if not payload:
            break

        for item in payload:
            filename = item.get("filename")
            status = item.get("status")

            if not filename or not status:
                continue

            all_files.append(ChangedFile(filename=filename, status=status))

        if len(payload) < per_page:
            break

        page += 1

    return all_files


def get_analyzable_files() -> list[str]:
    changed_files = fetch_changed_files_from_github()
    return filter_analyzable_files(changed_files)


if __name__ == "__main__":
    files = get_analyzable_files()
    for file in files:
        print(file)