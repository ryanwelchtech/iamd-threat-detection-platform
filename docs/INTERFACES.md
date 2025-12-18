# Interface Definitions

This document defines the primary data contracts between services.

All interfaces are versioned implicitly through schema discipline and service ownership.

---

## Normalized Observation  
**sensor-ingest → track-fusion**

```json
{
  "observation_id": "uuid",
  "sensor_type": "RADAR | EOIR | AIS",
  "sensor_id": "string",
  "ts_utc": "ISO-8601 timestamp",
  "position": {
    "lat": 29.7604,
    "lon": -95.3698,
    "alt_m": 12000
  },
  "velocity": {
    "vx_mps": 200,
    "vy_mps": -15,
    "vz_mps": 0
  },
  "signature": {
    "rcs": 0.8,
    "ir": 0.2
  },
  "quality": {
    "snr_db": 18.4,
    "confidence": 0.86
  }
}
```

## Track Object

**track-fusion output**
```json
{
  "track_id": "TRK-000123",
  "last_update_utc": "ISO-8601 timestamp",
  "state": {
    "lat": 29.76,
    "lon": -95.36,
    "alt_m": 11890
  },
  "velocity": {
    "vx_mps": 210,
    "vy_mps": -12,
    "vz_mps": 0
  },
  "track_confidence": 0.78,
  "sources": ["RADAR-01", "EOIR-02"],
  "history_len": 15
}
```

## Threat Object

**threat-scoring output**
```json
{
  "threat_id": "THR-000045",
  "track_id": "TRK-000123",
  "priority": "HIGH | MEDIUM | LOW",
  "score": 0.92,
  "rationale": [
    "closing_rate_gt_threshold",
    "altitude_profile_suspicious",
    "no_ais_match"
  ],
  "recommended_action": "REVIEW | TRACK | ESCALATE"
}
```

## Audit Event

**any service → audit-log**
```json
{
  "event_id": "uuid",
  "ts_utc": "ISO-8601 timestamp",
  "source_service": "string",
  "actor": "system | operator:<id>",
  "action": "string",
  "details": {}
}
```