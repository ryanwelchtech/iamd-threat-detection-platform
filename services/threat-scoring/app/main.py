from fastapi import FastAPI
from typing import Dict, Any, List
from datetime import datetime, timezone
import uuid
import yaml
import os

from iamd_common.log import audit
from .scoring import score_track

app = FastAPI(title="threat-scoring", version="0.1.0")

RULES_PATH = os.getenv("RULES_PATH", "app/rules.yaml")

# One threat per track (upsert)
THREATS_BY_TRACK: Dict[str, Dict[str, Any]] = {}

STATS: Dict[str, Any] = {
    "tracks_received": 0,
    "threats_emitted": 0,     # counts updates too (emissions)
    "by_priority": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
    "last_update_utc": None
}


def load_rules() -> Dict[str, Any]:
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _track_to_threat_id(track_id: str) -> str:
    # Deterministic ID so the same track always maps to the same threat record
    # Example: TRK-000001 -> THR-000001
    if track_id.startswith("TRK-"):
        return "THR-" + track_id.split("TRK-", 1)[1]
    return f"THR-{track_id}"


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "active_threats": len(THREATS_BY_TRACK)}


@app.post("/tracks")
def ingest_track(track: Dict[str, Any]) -> Dict[str, Any]:
    rules = load_rules()

    now = datetime.now(timezone.utc).isoformat()
    STATS["tracks_received"] += 1
    STATS["last_update_utc"] = now

    score, rationale, priority, action = score_track(track, rules)

    track_id = track.get("track_id", "UNKNOWN")
    threat_id = _track_to_threat_id(track_id)
    label = track.get("label") or track.get("contact_type") or track.get("track_id")
    contact_type = track.get("contact_type") or "UNKNOWN"


    # Pull coordinates/altitude so the UI can plot on radar
    state = track.get("state", {})
    threat = {
        "threat_id": threat_id,
        "track_id": track_id,
        "label": label,
        "contact_type": contact_type,
        "priority": priority,
        "score": score,
        "rationale": rationale,
        "recommended_action": action,
        "last_update_utc": now,

        # For plotting / display (derived from current track state)
        "state": {
            "lat": state.get("lat"),
            "lon": state.get("lon"),
            "alt_m": state.get("alt_m")
        }
    }

    THREATS_BY_TRACK[track_id] = threat

    if len(THREATS_BY_TRACK) > 10:
        oldest_track = min(
            THREATS_BY_TRACK,
            key=lambda k: THREATS_BY_TRACK[k].get("last_update_utc", "")
        )
        del THREATS_BY_TRACK[oldest_track]

    STATS["threats_emitted"] += 1

    # Recompute by_priority counts from current active threats (more accurate than incrementing)
    byp = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for t in THREATS_BY_TRACK.values():
        p = t.get("priority", "LOW")
        if p not in byp:
            byp[p] = 0
        byp[p] += 1
    STATS["by_priority"] = byp

    audit({
        "event_id": str(uuid.uuid4()),
        "ts_utc": now,
        "source_service": "threat-scoring",
        "actor": "system",
        "action": "THREAT_UPSERTED",
        "details": {
            "threat_id": threat_id,
            "track_id": track_id,
            "priority": priority,
            "score": score,
            "rationale": rationale
        }
    })

    return threat


@app.get("/threats")
def get_threats():
    threats = list(THREATS_BY_TRACK.values())

    # highest score first, then most recent
    threats.sort(
        key=lambda t: (t.get("score", 0.0), t.get("last_update_utc", "")),
        reverse=True
    )

    return threats[:10]



@app.get("/stats")
def stats() -> Dict[str, Any]:
    # Keep stats consistent with current in-memory state
    active = len(THREATS_BY_TRACK)

    byp = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for t in THREATS_BY_TRACK.values():
        p = t.get("priority", "LOW")
        if p not in byp:
            byp[p] = 0
        byp[p] += 1

    return {
        **STATS,
        "active_threats": active,
        "by_priority": byp,
    }


@app.post("/reset")
def reset():
    THREATS_BY_TRACK.clear()
    STATS["tracks_received"] = 0
    STATS["threats_emitted"] = 0
    STATS["by_priority"] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    STATS["last_update_utc"] = None
    return {"ok": True}
