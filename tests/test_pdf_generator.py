import os
import json
from analyzer.report_generator import generate_pdf


def test_pdf_generation():
    data = [{
        "method": {
            "signature": "public void test()",
            "javadoc": {
                "description": "desc",
                "params": [],
                "return": ""
            }
        },
        "details": {}
    }]

    os.makedirs("reports", exist_ok=True)

    with open("reports/test.json", "w") as f:
        json.dump(data, f)

    generate_pdf("reports/test.json", "reports/test.pdf")

    assert os.path.exists("reports/test.pdf")