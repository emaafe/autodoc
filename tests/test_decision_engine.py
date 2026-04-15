from analyzer.decision_engine import decide


def test_fail_from_rules():
    result = decide({"status": "FAIL"}, None)

    assert result["final_status"] == "FAIL"


def test_pass_when_consistent():
    result = decide(
        {"status": "PASS"},
        {"result": "CONSISTENT"}
    )

    assert result["final_status"] == "PASS"


def test_needs_review_when_inconsistent():
    result = decide(
        {"status": "PASS"},
        {"result": "INCONSISTENT", "explanation": "error"}
    )

    assert result["final_status"] == "NEEDS REVIEW"


def test_needs_review_when_uncertain():
    result = decide(
        {"status": "PASS"},
        {"result": "UNCERTAIN", "explanation": "duda"}
    )

    assert result["final_status"] == "NEEDS REVIEW"


def test_exempted_method():
    result = decide(
        {"status": "PASS", "exempted": True},
        None
    )

    assert result["final_status"] == "PASS"