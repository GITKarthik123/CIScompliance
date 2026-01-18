
import datetime
#from src.github_client import get as gh_get
from src.github_client import get as gh_get


ORG = "DevOps-Common"

def list_repos():
    return gh_get(f"/orgs/{ORG}/repos?per_page=100") or []

def inactive_repositories(days=180):
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    stale = []

    for r in list_repos():
        pushed = r.get("pushed_at")

        if not pushed:
            stale.append(r["name"])
            continue

        dt = datetime.datetime.fromisoformat(pushed.replace("Z", "+00:00"))
        if dt < cutoff:
            stale.append(r["name"])

    return {
        "control_id": "RM-1.2",
        "status": "FAIL" if stale else "PASS",
        "non_compliant": stale,
        "evidence": "Checked via GitHub REST API (repos.pushed_at)",
        "validation_type": "AUTOMATED"
    }
