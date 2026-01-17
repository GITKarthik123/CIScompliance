# src/github_client.py
import os
import requests

GITHUB_API = "https://api.github.com"

def get(path: str):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN not set")

    url = f"{GITHUB_API}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    r = requests.get(url, headers=headers, timeout=30)
    if r.status_code == 404:
        return {}
    r.raise_for_status()
    return r.json()