
# scripts/run_scan.py
import os
import json
import re
from datetime import datetime
from openpyxl import Workbook
import cis_checks as checks

os.makedirs("reports", exist_ok=True)
RESULTS = []

# --- Resolver: robust function lookup by slug ---
def _resolve_check_function(slug: str):
    safe = re.sub(r'[^a-zA-Z0-9_]', '_', slug)

    # 1) exact normalized name
    fn = getattr(checks, safe, None)
    if fn:
        return fn

    # 2) common generator tail: try trimming "_control"
    if safe.endswith("_control"):
        fn = getattr(checks, safe[:-8], None)
        if fn:
            return fn

    # 3) semantic map (aliases -> implemented functions)
    SEMANTIC = {
        # approvals
        "any_change_code_receives_approval": "require_pr_reviews",
        "any_change_code_receives_approval_two": "require_pr_reviews",
        # dismiss stale approvals
        "previous_approvals_dismissed_when_updates": "dismiss_stale_reviews",
        "previous_approvals_dismissed_when_updates_introduced": "dismiss_stale_reviews",
        # restrict who can dismiss
        "there_restrictions_who_can_dismiss": "restrict_dismissals",
        "there_restrictions_who_can_dismiss_code": "restrict_dismissals",
        # earlier mismatch
        "any_changes_code_tracked_version": "any_changes_code_tracked_version_control",
    }
    target = SEMANTIC.get(safe)
    if target and hasattr(checks, target):
        return getattr(checks, target)

    # 4) Not found: return None so caller can mark as error in results
    return None

def _append_result(control_id, title, res):
    # default
    status = "Compliant"
    details = "OK"

    if isinstance(res, list) and res:
        status = "Non-Compliant"
        details = "Issues: " + ", ".join(res[:10])
    elif res is False:
        status = "Non-Compliant"
        details = "Control requirement not met"
    elif isinstance(res, dict) and not res.get("implemented", True):
        status = "Non-Compliant"
        details = res.get("reason") or res.get("error") or "Not implemented"

    RESULTS.append({
        "control": control_id,
        "title": title,
        "status": status,
        "details": details,
        "checked_at": datetime.utcnow().isoformat()
    })

def main():
    with open("scripts/cis_controls.json") as f:
        controls = json.load(f)

    for c in controls:
        slug = c["check"]
        fn = _resolve_check_function(slug)
        if fn is None:
            # record a non-fatal error for this control and continue
            _append_result(
                c["id"], c["title"],
                {"implemented": False, "reason": f"Unknown check slug '{slug}'"}
            )
            continue

        try:
            res = fn()
        except Exception as e:
            # don't crash the whole run; record error for this control
            _append_result(
                c["id"], c["title"],
                {"implemented": False, "error": f"{type(e).__name__}: {e}"}
            )
        else:
            _append_result(c["id"], c["title"], res)

    # Always write outputs
    with open("reports/cis_report.json","w") as f:
        json.dump(RESULTS, f, indent=2)

    wb = Workbook()
    ws = wb.active
    ws.append(["Control","Title","Status","Details","Checked At"])
    for r in RESULTS:
        ws.append([r["control"], r["title"], r["status"], r["details"], r["checked_at"]])
    wb.save("reports/cis_report.xlsx")

if __name__ == "__main__":
    main()
