import os
import time
import jwt
from typing import Dict, Any


def _secret() -> str:
    return os.getenv("JWT_SECRET", "dev_super_secret_change_me")


def issue_token(subject: str, role: str, ttl_seconds: int = 3600) -> str:
    now = int(time.time())
    payload = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + ttl_seconds
    }
    return jwt.encode(payload, _secret(), algorithm="HS256")


def verify_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, _secret(), algorithms=["HS256"])
