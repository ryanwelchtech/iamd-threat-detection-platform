import random
from typing import Any, Dict, Tuple, List

RATIONALES = [
    "High closing speed exceeds threshold",
    "No AIS match (identity/attribution gap)",
    "Altitude profile inconsistent with declared route",
    "Emissions/identity mismatch across sensors",
    "Rapid heading change within short interval",
    "Surface contact without positive ID",
    "Intermittent track quality / sensor disagreement",
]

def score_track(track: Dict[str, Any], rules: Dict[str, Any]) -> Tuple[float, List[str], str, str]:
    # Weighted random priority
    priority = random.choices(
        population=["LOW", "MEDIUM", "HIGH"],
        weights=[0.55, 0.30, 0.15],
        k=1
    )[0]

    # Score ranges per priority
    if priority == "LOW":
        score = round(random.uniform(0.05, 0.35), 2)
        action = "TRACK"
    elif priority == "MEDIUM":
        score = round(random.uniform(0.36, 0.70), 2)
        action = "REVIEW"
    else:
        score = round(random.uniform(0.71, 0.95), 2)
        action = "ESCALATE"

    # 1–3 rationale items
    n = random.randint(1, 3)
    rationale = random.sample(RATIONALES, n)

    return score, rationale, priority, action
