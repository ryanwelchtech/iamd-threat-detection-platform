from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException
import os
import requests
import uuid
import time
import random
import math
import json

from iamd_common.auth import issue_token

app = FastAPI(title="cop-dashboard", version="0.2.0")
templates = Jinja2Templates(directory="app/templates")

SENSOR_INGEST_URL = os.getenv("SENSOR_INGEST_URL", "http://sensor-ingest:8001")
TRACK_FUSION_URL = os.getenv("TRACK_FUSION_URL", "http://track-fusion:8002")
THREAT_SCORING_URL = os.getenv("THREAT_SCORING_URL", "http://threat-scoring:8003")
AUDIT_URL = os.getenv("AUDIT_URL", "http://audit-log:8004")

JWT_SECRET = os.getenv("JWT_SECRET", "dev_super_secret_change_me")


RATIONALE_MAP = {
    "closing_rate_gt_threshold": "High closing speed exceeds threshold",
    "no_ais_match": "No AIS match (identity/attribution gap)",
    "altitude_high": "High altitude profile",
    "surface_contact": "Surface contact without positive ID",
}


def _get_json(url: str, default):
    try:
        r = requests.get(url, timeout=2)
        if r.status_code != 200:
            return default
        return r.json()
    except Exception:
        return default


def _pretty(obj) -> str:
    try:
        return json.dumps(obj, indent=2)
    except Exception:
        return str(obj)


# ----------------------------
# Miles-based randomization helpers
# ----------------------------

# 1° latitude ~ 69 miles
def _miles_to_lat(dmiles: float) -> float:
    return dmiles / 69.0

# 1° longitude ~ 69*cos(lat) miles
def _miles_to_lon(dmiles: float, at_lat: float) -> float:
    denom = 69.0 * math.cos(math.radians(at_lat))
    if denom == 0:
        return 0.0
    return dmiles / denom


def _random_offset_miles(center_lat: float, center_lon: float, max_miles: float = 8.0):
    # dx east/west, dy north/south
    dx = random.uniform(-max_miles, max_miles)
    dy = random.uniform(-max_miles, max_miles)

    lat = center_lat + _miles_to_lat(dy)
    lon = center_lon + _miles_to_lon(dx, center_lat)
    return lat, lon


def _bearer_for_demo_operator() -> str:
    # 2 hours = 7200 seconds
    token = issue_token("operator@demo.local", "operator", ttl_seconds=7200)
    return f"Bearer {token}"

def _post_observation(obs: dict, bearer: str):
    r = requests.post(
        f"{SENSOR_INGEST_URL}/observations",
        json=obs,
        headers={"Authorization": bearer},
        timeout=3,
    )
    if r.status_code != 200:
        raise RuntimeError(f"sensor-ingest rejected observation: {r.status_code} {r.text}")
    return r.json()


# ----------------------------
# Scenario generator (THIS is where object_id + random lat/lon happen)
# ----------------------------
def _build_scenario_observations(scenario: str) -> list[dict]:
    scenario = (scenario or "").strip().lower()

    # Allow aliases
    if scenario in ["airborne_fast_closing", "airborne", "fast_air"]:
        scenario = "air"
    if scenario in ["sea_surface_no_ais", "surface", "maritime"]:
        scenario = "sea"
    if scenario in ["benign_contacts", "benign_scenario"]:
        scenario = "benign"

    # Center point (you can pick any reference). This one is Gulf/Houston-ish.
    center_lat = 29.7604
    center_lon = -95.3698

    # Unique run id per click (seconds + small salt)
    run_id = str(int(time.time()))
    salt = uuid.uuid4().hex[:6]

    def make_id(prefix: str, idx: int) -> str:
        # >>> Unique per click and per contact
        return f"{prefix}-{run_id}-{salt}-{idx:02d}"

    def make_obs_id() -> str:
        return f"OBS-{uuid.uuid4().hex[:12]}"

    def make_signature() -> dict:
        # Demo-safe placeholder for "signed" sensor messages.
        # You can later upgrade to HMAC/JWS.
        return {"alg": "none", "kid": "demo", "sig": "unsigned"}


    observations: list[dict] = []

    # Baseline fields
    base = {
        "schema_version": "1.0",
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        # REQUIRED by sensor-ingest
        "signature": make_signature(),
    }


    if scenario == "benign":
        # 2 benign contacts (lower altitude, stable)
        for i in range(1, 3):
            lat, lon = _random_offset_miles(center_lat, center_lon, max_miles=6.0)
            observations.append({
                **base,
                "observation_id": make_obs_id(),
                "sensor_type": "RADAR",
                "object_id": make_id("BENIGN", i),
                "contact_type": "BENIGN",
                "label": f"BENIGN-{i:02d}",
                "sensor_id": "RADAR-01",
                "modality": "RADAR",
                "position": {"lat": lat, "lon": lon, "alt_m": 1500.0},
                "velocity": {"vx_mps": 120.0, "vy_mps": 40.0, "vz_mps": 0.0},
                "quality": {"confidence": 0.85},
                "metadata": {"scenario": "benign"}
            })

    elif scenario == "air":
        # 3 air contacts, higher alt, one "fast closing" profile
        for i in range(1, 4):
            lat, lon = _random_offset_miles(center_lat, center_lon, max_miles=10.0)
            closing_fast = (i == 1)
            observations.append({
                **base,
                "observation_id": make_obs_id(),
                "sensor_type": "EOIR" if i == 2 else "RADAR",
                "object_id": make_id("AIR", i),
                "contact_type": "AIR",
                "label": f"AIRPLANE-{i:02d}",
                "sensor_id": "EOIR-02" if i == 2 else "RADAR-01",
                "modality": "EOIR" if i == 2 else "RADAR",
                "position": {"lat": lat, "lon": lon, "alt_m": 12000.0 if closing_fast else 9000.0},
                "velocity": {"vx_mps": 420.0 if closing_fast else 250.0, "vy_mps": 80.0, "vz_mps": 0.0},
                "quality": {"confidence": 0.88},
                "metadata": {"scenario": "airborne_fast_closing" if closing_fast else "air"}
            })

    elif scenario == "sea":
        # 3 sea contacts, surface alt, no AIS context implied by metadata
        for i in range(1, 4):
            lat, lon = _random_offset_miles(center_lat, center_lon, max_miles=12.0)
            observations.append({
                **base,
                "observation_id": make_obs_id(),
                "sensor_type": "AIS" if i == 3 else "RADAR",
                "object_id": make_id("SEA", i),
                "contact_type": "SEA",
                "label": f"VESSEL-{i:02d}",
                "sensor_id": "AIS-EDGE-01" if i == 3 else "RADAR-01",
                "modality": "AIS" if i == 3 else "RADAR",
                "position": {"lat": lat, "lon": lon, "alt_m": 0.0},
                "velocity": {"vx_mps": 18.0, "vy_mps": 3.0, "vz_mps": 0.0},
                "quality": {"confidence": 0.82},
                "metadata": {"scenario": "sea_surface_no_ais"}
            })

    else:
        # default = benign-like single contact
        lat, lon = _random_offset_miles(center_lat, center_lon, max_miles=6.0)
        observations.append({
            **base,
            "object_id": make_id("CONTACT", 1),
            "contact_type": "BENIGN",
            "label": "CONTACT-01",
            "sensor_id": "RADAR-01",
            "modality": "RADAR",
            "position": {"lat": lat, "lon": lon, "alt_m": 2000.0},
            "velocity": {"vx_mps": 120.0, "vy_mps": 20.0, "vz_mps": 0.0},
            "quality": {"confidence": 0.80},
            "metadata": {"scenario": "default"}
        })

    return observations


# ----------------------------
# UI routes
# ----------------------------

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    tracks = _get_json(f"{TRACK_FUSION_URL}/tracks", [])
    threats = _get_json(f"{THREAT_SCORING_URL}/threats", [])
    fusion_stats = _get_json(f"{TRACK_FUSION_URL}/stats", {})
    scoring_stats = _get_json(f"{THREAT_SCORING_URL}/stats", {})
    events = _get_json(f"{AUDIT_URL}/events", [])

    observations_ingested = int(fusion_stats.get("observations_ingested", 0) or 0)
    active_tracks = int(fusion_stats.get("active_tracks", len(tracks)) or len(tracks))
    active_threats = int(scoring_stats.get("active_threats", len(threats)) or len(threats))

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "tracks": tracks,
            "threats": threats,
            "events": events,
            "fusion_stats_pretty": _pretty(fusion_stats),
            "scoring_stats_pretty": _pretty(scoring_stats),
            "rationale_map": RATIONALE_MAP,
            "observations_ingested": observations_ingested,
            "active_tracks": active_tracks,
            "active_threats": active_threats,
        }
    )


@app.get("/api/snapshot")
def api_snapshot():
    tracks = _get_json(f"{TRACK_FUSION_URL}/tracks", [])
    threats = _get_json(f"{THREAT_SCORING_URL}/threats", [])
    return JSONResponse({"tracks": tracks, "threats": threats})


# Scenario endpoints (buttons call these)
@app.post("/scenario/{scenario}")
def run_scenario(scenario: str):
    bearer = _bearer_for_demo_operator()
    try:
        obs_list = _build_scenario_observations(scenario)
        for obs in obs_list:
            _post_observation(obs, bearer)
        return {"ok": True, "scenario": scenario, "count": len(obs_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scenario/{scenario}")
def run_scenario_get(scenario: str):
    return run_scenario(scenario)


# Clear Radar / reset all in-memory services
@app.post("/clear")
def clear_all():
    try:
        requests.post(f"{TRACK_FUSION_URL}/reset", timeout=2)
    except Exception:
        pass
    try:
        requests.post(f"{THREAT_SCORING_URL}/reset", timeout=2)
    except Exception:
        pass
    try:
        requests.post(f"{AUDIT_URL}/reset", timeout=2)
    except Exception:
        pass
    return {"ok": True}
