import json

with open("reports/output.json") as f:
    data = json.load(f)

has_fail = any(r["final_status"] == "FAIL" for r in data)

if has_fail:
    print("FAIL detected - blocking merge")
    exit(1)

print("No blocking issues")