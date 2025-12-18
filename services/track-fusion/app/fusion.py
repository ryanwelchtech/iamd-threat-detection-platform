from typing import Dict, Any, Tuple
import math


def _approx_dist_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Very rough distance approximation for demo use only.
    Not geodesic. Good enough for correlation demos.
    """
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) * 111.0


def find_best_track_match(tracks: Dict[str, Dict[str, Any]], obs: Dict[str, Any], max_km: float = 5.0) -> Tuple[str, float]:
    """
    Return (track_id, distance_km). If none within max_km, returns ("", inf).
    """
    pos = obs.get("position", {})
    lat = float(pos.get("lat", 0.0))
    lon = float(pos.get("lon", 0.0))

    best_id = ""
    best_d = float("inf")

    for tid, t in tracks.items():
        s = t.get("state", {})
        d = _approx_dist_km(float(s.get("lat", 0.0)), float(s.get("lon", 0.0)), lat, lon)
        if d < best_d:
            best_d = d
            best_id = tid

    if best_id and best_d <= max_km:
        return best_id, best_d

    return "", float("inf")
