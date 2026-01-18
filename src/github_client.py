import os, requests

TOKEN = os.getenv("GH_AUDIT_TOKEN")
HEADERS = {
  "Authorization": f"Bearer {TOKEN}",
  "Accept": "application/vnd.github+json"
}
BASE = "https://api.github.com"

def get(url):
    r = requests.get(BASE + url, headers=HEADERS)
    if r.status_code not in (200,201):
        return None
    return r.json()