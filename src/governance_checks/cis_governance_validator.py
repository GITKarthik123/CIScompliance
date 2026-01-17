
import yaml, datetime, os

MAX_AGE_DAYS = 90

def validate_attestation(path):
    if not os.path.exists(path):
        return {"status": "FAIL", "reason": "Missing evidence"}

    with open(path) as f:
        data = yaml.safe_load(f)

    reviewed = datetime.datetime.fromisoformat(data["reviewed_on"])
    age = (datetime.datetime.utcnow() - reviewed).days

    if age > MAX_AGE_DAYS:
        return {"status": "FAIL", "reason": "Evidence expired"}

    if not data.get("approved_by"):
        return {"status": "FAIL", "reason": "Missing approval"}

    return {"status": "PASS"}
