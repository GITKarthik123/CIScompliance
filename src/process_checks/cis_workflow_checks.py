
import re
from github_client import get as gh_get

ORG = "DevOps-Common"
REPO = "sample-repo"
TICKET = re.compile(r"(JIRA|TASK|INC)-\d+")

def pr_change_tracking():
    prs = gh_get(f"/repos/{ORG}/{REPO}/pulls?state=open") or []
    bad = []
    for pr in prs:
        text = (pr.get("title","") + pr.get("body",""))
        if not TICKET.search(text):
            bad.append(pr["number"])
    return {"status": "FAIL" if bad else "PASS", "non_compliant_prs": bad}
