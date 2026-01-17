
from datetime import date

def build_report(results: dict, output="reports/cis_report.md"):
    lines = []
    lines.append("# GitHub Enterprise EMU — CIS Compliance Report")
    lines.append(f"Date: {date.today()}\n")

    pass_c = sum(1 for r in results.values() if r["status"] == "PASS")
    fail_c = sum(1 for r in results.values() if r["status"] == "FAIL")

    lines.append("## Summary")
    lines.append(f"- PASS: {pass_c}")
    lines.append(f"- FAIL: {fail_c}\n")

    lines.append("## Detailed Results")
    for cid, res in results.items():
        lines.append(f"### {cid}")
        lines.append(f"Status: **{res['status']}**")
        if "non_compliant" in res:
            lines.append(f"Non-compliant: {res['non_compliant']}")
        if "reason" in res:
            lines.append(f"Reason: {res['reason']}")
        lines.append("")
    os.makedirs("reports", exist_ok=True)
    with open(output, "w") as f:
        f.write("\n".join(lines))
