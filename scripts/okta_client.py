
import os, requests

OKTA_TOKEN = os.getenv("OKTA_TOKEN")
OKTA_ORG = os.getenv("OKTA_ORG")

HEADERS = {
  "Authorization": f"SSWS {OKTA_TOKEN}",
  "Accept": "application/json"
}

BASE = f"https://{OKTA_ORG}.okta.com"

def get(url):
    r = requests.get(BASE + url, headers=HEADERS)
    if r.status_code not in (200,201):
        return None
    return r.json()
