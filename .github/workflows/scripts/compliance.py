from github import Github
import os, sys, datetime, json

token = os.getenv("GITHUB_TOKEN")
org_name = os.getenv("ORG_NAME")

g = Github(token)
org = g.get_organization(org_name)

# Load trusted users list
with open("scripts/config.json") as f:
    trusted_users = json.load(f)["trusted_users"]

failures = []

# 1. SECURITY.md check
for repo in org.get_repos():
    if not repo.private:
        try:
            repo.get_contents("SECURITY.md")
        except:
            failures.append(f"{repo.name} missing SECURITY.md")

# 2. Inactive repos (>6 months)
cutoff = datetime.datetime.now() - datetime.timedelta(days=180)
for repo in org.get_repos():
    if repo.pushed_at < cutoff:
        failures.append(f"{repo.name} inactive since {repo.pushed_at}")

# 3. Fork tracking
for repo in org.get_repos():
    forks = repo.get_forks()
    if forks.totalCount > 0:
        print(f"{repo.name} has {forks.totalCount} forks")

# 4. Visibility changes (audit log requires curl/manual)
# Example: curl -H "Authorization: token $GITHUB_TOKEN" \
#   "https://api.github.com/orgs/{org}/audit-log?phrase=repo.access"

# Print results
if failures:
    print("❌ Compliance failures:")
    for f in failures:
        print("-", f)
    sys.exit(1)
else:
    print("✅ All checks passed")
