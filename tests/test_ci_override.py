import os
import json
import subprocess


def test_override_denied():
    data = [{"final_status": "NEEDS REVIEW"}]

    os.makedirs("reports", exist_ok=True)

    with open("reports/output.json", "w") as f:
        json.dump(data, f)

    os.environ["GITHUB_ACTOR"] = "unauthorized"
    os.environ["AUTODOC_OVERRIDE"] = "true"

    result = subprocess.run(
        ["python", "-m", "analyzer.check_review"],
        capture_output=True
    )

    assert result.returncode != 0


def test_override_allowed():
    data = [{"final_status": "NEEDS REVIEW"}]

    os.makedirs("reports", exist_ok=True)

    with open("reports/output.json", "w") as f:
        json.dump(data, f)

    os.environ["GITHUB_ACTOR"] = "tech-lead"
    os.environ["AUTODOC_OVERRIDE"] = "true"

    result = subprocess.run(
        ["python", "-m", "analyzer.check_review"],
        capture_output=True
    )

    assert result.returncode == 0