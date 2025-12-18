from fastapi import FastAPI
from typing import Any, Dict, List

app = FastAPI(title="audit-log", version="0.1.0")

# Demo-only in-memory append-only log
EVENTS: List[Dict[str, Any]] = []


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "events": len(EVENTS)}


@app.post("/events")
def add_event(evt: Dict[str, Any]) -> Dict[str, Any]:
    # Append-only behavior (demo)
    EVENTS.append(evt)
    EVENTS[:] = EVENTS[-10:]
    return {"stored": True, "count": len(EVENTS)}


@app.get("/events")
def get_events() -> List[Dict[str, Any]]:
    # Return last 10 events for quick viewing
    return EVENTS[-10:][::-1]

@app.post("/reset")
def reset():
    EVENTS.clear()
    return {"ok": True}
