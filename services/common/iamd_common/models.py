from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class Position(BaseModel):
    lat: float
    lon: float
    alt_m: float


class Velocity(BaseModel):
    vx_mps: float
    vy_mps: float
    vz_mps: float


class Signature(BaseModel):
    rcs: float = 0.0
    ir: float = 0.0


class Quality(BaseModel):
    snr_db: float = 0.0
    confidence: float = Field(ge=0.0, le=1.0)


class Observation(BaseModel):
    observation_id: str
    sensor_type: str
    sensor_id: str
    ts_utc: str
    position: Position
    velocity: Velocity
    signature: Signature
    quality: Quality
    
    # Optional enrichment fields (preserved end-to-end)
    object_id: Optional[str] = None
    label: Optional[str] = None
    contact_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None



class Track(BaseModel):
    track_id: str
    last_update_utc: str
    state: Position
    velocity: Velocity
    track_confidence: float = Field(ge=0.0, le=1.0)
    sources: List[str]
    history_len: int


class Threat(BaseModel):
    threat_id: str
    track_id: str
    priority: str
    score: float = Field(ge=0.0, le=1.0)
    rationale: List[str]
    recommended_action: str


class AuditEvent(BaseModel):
    event_id: str
    ts_utc: str
    source_service: str
    actor: str
    action: str
    details: Dict[str, Any]
