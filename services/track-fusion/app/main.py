from fastapi import FastAPI, Header, HTTPException
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import os
import requests
import math

from iamd_common.auth import verify_token
from iamd_common.log import audit

app = FastAPI(title="track-fusion", version="0.2.0")

THREAT_URL = os.getenv("THREAT_URL", "http://threat-scoring:8003")

# In-memory stores (demo-safe)
TRACKS: Dict[str, Dict[str, Any]] = {}
OBJECT_TO_TRACK: Dict[str, str] = {}

STATS = {
    "observations_ingested": 0,
    "tracks_created": 0,
    "tracks_updated": 0,
    "active_tracks": 0,
    "last_update_utc": None,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _require_auth(auth_header: Optional[str]) -> Dict[str, Any]:
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = auth_header.split(" ", 1)[1].strip()
    try:
        return verify_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # simple local approximation (fine for demo scope)
    return math.sqrt(((lat1 - lat2) * 111.0) ** 2 + ((lon1 - lon2) * 111.0) ** 2)


def _new_track_id() -> str:
    return f"TRK-{str(uuid.uuid4())[:8]}"


@app.get("/health")
def health():
    return {"ok": True, "tracks": len(TRACKS)}


@app.get("/tracks")
def get_tracks():
    tracks = list(TRACKS.values())

    # newest first
    tracks.sort(key=lambda t: t.get("last_update_utc", ""), reverse=True)

    # cap to latest 10
    return tracks[:10]



@app.get("/stats")
def stats():
    STATS["active_tracks"] = len(TRACKS)
    return STATS


@app.post("/reset")
def reset():
    TRACKS.clear()
    OBJECT_TO_TRACK.clear()
    STATS["observations_ingested"] = 0
    STATS["tracks_created"] = 0
    STATS["tracks_updated"] = 0
    STATS["active_tracks"] = 0
    STATS["last_update_utc"] = None
    return {"ok": True}


@app.post("/observations")
def ingest_observation(obs: Dict[str, Any], authorization: Optional[str] = Header(None)):
    _ = _require_auth(authorization)

    # validate
    if "position" not in obs or "quality" not in obs or "sensor_id" not in obs:
        raise HTTPException(status_code=400, detail="Observation missing required fields")

    pos = obs["position"]
    lat = float(pos["lat"])
    lon = float(pos["lon"])
    alt = float(pos.get("alt_m", 0.0))

    sensor_id = str(obs["sensor_id"])
    confidence = float(obs["quality"].get("confidence", 0.5))

    # >>> These fields are what lets COP label dots as AIR/SEA/BENIGN
    object_id = obs.get("object_id")          # unique per contact per click
    label = obs.get("label")                  # e.g. "AIR-01"
    contact_type = obs.get("contact_type")    # "AIR" | "SEA" | "BENIGN"

    STATS["observations_ingested"] += 1
    STATS["last_update_utc"] = _utc_now()

    # 1) strong correlation: object_id mapping
    match_track_id: Optional[str] = None
    if object_id and object_id in OBJECT_TO_TRACK:
        mapped = OBJECT_TO_TRACK[object_id]
        if mapped in TRACKS:
            match_track_id = mapped

    # 2) fallback correlation: spatial proximity (weak)
    if not match_track_id:
        for tid, trk in TRACKS.items():
            st = trk.get("state", {})
            d = _distance_km(float(st.get("lat", 0.0)), float(st.get("lon", 0.0)), lat, lon)
            if d < 2.0:  # km threshold
                match_track_id = tid
                break

    now = _utc_now()

    if not match_track_id:
        track_id = _new_track_id()

        track = {
            "track_id": track_id,
            "last_update_utc": now,
            "state": {"lat": lat, "lon": lon, "alt_m": alt},
            "sources": [sensor_id],
            "track_confidence": max(0.0, min(1.0, confidence)),
            # >>> labeling fields for radar/UI
            "label": label or (object_id or track_id),
            "contact_type": contact_type or "UNKNOWN",
        }

        TRACKS[track_id] = track
        STATS["tracks_created"] += 1

        if object_id:
            OBJECT_TO_TRACK[object_id] = track_id

        audit({
            "event_id": str(uuid.uuid4()),
            "ts_utc": now,
            "source_service": "track-fusion",
            "actor": "system",
            "action": "TRACK_CREATED",
            "details": {
                "track_id": track_id,
                "object_id": object_id,
                "label": track["label"],
                "contact_type": track["contact_type"],
            }
        })

    else:
        track = TRACKS[match_track_id]

        track["state"] = {"lat": lat, "lon": lon, "alt_m": alt}
        track["last_update_utc"] = now

        track["track_confidence"] = max(
            0.0,
            min(1.0, float(track.get("track_confidence", 0.5)) + 0.05)
        )

        if sensor_id not in track.get("sources", []):
            track.setdefault("sources", []).append(sensor_id)

        # >>> preserve/update label/type when present
        if label:
            track["label"] = label
        if contact_type:
            track["contact_type"] = contact_type

        STATS["tracks_updated"] += 1
        track_id = match_track_id

        audit({
            "event_id": str(uuid.uuid4()),
            "ts_utc": now,
            "source_service": "track-fusion",
            "actor": "system",
            "action": "TRACK_UPDATED",
            "details": {
                "track_id": track_id,
                "object_id": object_id,
                "label": track.get("label"),
                "contact_type": track.get("contact_type"),
            }
        })

    # forward to threat-scoring (best effort)
    try:
        requests.post(
            f"{THREAT_URL}/tracks",
            json=TRACKS[track_id],
            headers={"Authorization": authorization},
            timeout=3,
        )
    except Exception:
        pass

    return {"ok": True, "track_id": track_id}
