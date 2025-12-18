from fastapi import FastAPI, Header, HTTPException
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import os
import requests

from pydantic import ValidationError
from iamd_common.models import Observation
from iamd_common.auth import verify_token
from iamd_common.log import audit

app = FastAPI(title="sensor-ingest", version="0.1.0")

TRACK_FUSION_URL = os.getenv("TRACK_FUSION_URL", "http://track-fusion:8002")


def _require_auth(auth_header: Optional[str]) -> Dict[str, Any]:
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = auth_header.split(" ", 1)[1].strip()

    try:
        return verify_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True}


@app.post("/observations")
def post_observation(payload: Dict[str, Any], authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    claims = _require_auth(authorization)

    if claims.get("role") not in ["sensor", "operator", "system"]:
        raise HTTPException(status_code=403, detail="Insufficient role")

    try:
        obs = Observation(**payload)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    audit({
        "event_id": str(uuid.uuid4()),
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "source_service": "sensor-ingest",
        "actor": f"operator:{claims.get('sub','unknown')}",
        "action": "OBSERVATION_INGESTED",
        "details": {
            "observation_id": obs.observation_id,
            "sensor_type": obs.sensor_type,
            "sensor_id": obs.sensor_id
        }
    })

    # Forward to track-fusion (preserve authorization to enforce Zero Trust end-to-end)
    try:
        r = requests.post(
            f"{TRACK_FUSION_URL}/observations",
            json=obs.model_dump(),
            headers={"Authorization": authorization},
            timeout=3
        )
        return {"forwarded": True, "fusion_status": r.status_code}
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to forward observation to track-fusion")
