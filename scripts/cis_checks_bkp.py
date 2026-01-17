
from github_client import get as gh_get
from okta_client import get as okta_get

ORG = "DevOps-Common"

def branch_protection():
    repos = gh_get(f"/orgs/{ORG}/repos?per_page=100") or []
    missing = []
    for r in repos:
        name = r["name"]
        bp = gh_get(f"/repos/{ORG}/{name}/branches/main/protection")
        if not bp:
            missing.append(name)
    return missing

def security_md():
    repos = gh_get(f"/orgs/{ORG}/repos?per_page=100") or []
    missing = []
    for r in repos:
        name = r["name"]
        sec = gh_get(f"/repos/{ORG}/{name}/contents/SECURITY.md")
        if not sec:
            missing.append(name)
    return missing

def admin_count(max_admins=5):
    admins = gh_get(f"/orgs/{ORG}/members?role=admin") or []
    return len(admins) <= max_admins

def app_approval():
    apps = gh_get(f"/orgs/{ORG}/installations") or []
    for a in apps:
        if a.get("suspended") is False:
            return False
    return True

def okta_mfa():
    policies = okta_get("/api/v1/policies?type=MFA_ENROLL")
    if not policies:
        return False
    for p in policies:
        if p.get("status") == "ACTIVE":
            return True
    return False
