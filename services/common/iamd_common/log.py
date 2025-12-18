import os
import requests
from typing import Dict, Any


def audit(event: Dict[str, Any]) -> None:
    """
    Send an audit event to the audit-log service.

    Fail-open by design:
    audit failure must not break mission flow.
    """
    url = os.getenv("AUDIT_URL")
    if not url:
        return

    try:
        requests.post(f"{url}/events", json=event, timeout=2)
    except Exception:
        # Intentionally swallow errors for demo resilience
        return
