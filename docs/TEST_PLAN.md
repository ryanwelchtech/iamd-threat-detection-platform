# Test Plan

## Objective
Validate correct behavior for ingestion, fusion, scoring, dashboard display, and auditability.

## Preconditions
- Stack running: `docker compose up --build`
- COP reachable: http://localhost:8080

## Test cases

### TC-01: Benign scenario (LOW expected)
**Steps**
1. Run: `.\scripts\seed-data.ps1 -Scenario benign`
2. Refresh COP

**Expected**
- 1+ track appears
- Threat score trends LOW (or remains below MEDIUM threshold)
- Audit events recorded for observation ingestion, track update, and threat emission

---

### TC-02: Airborne fast closing (MEDIUM/HIGH expected)
**Steps**
1. Run: `.\scripts\seed-data.ps1 -Scenario airborne_fast_closing`
2. Refresh COP

**Expected**
- Track confidence increases with multi-sensor sources (RADAR + EOIR)
- Threat shows rationale including:
  - closing rate exceeds threshold
  - no AIS match
- Recommended action: REVIEW (or higher per policy)

---

### TC-03: Sea surface no AIS (MEDIUM expected)
**Steps**
1. Run: `.\scripts\seed-data.ps1 -Scenario sea_surface_no_ais`
2. Refresh COP

**Expected**
- Track altitude near 0
- Threat rationale includes “no AIS match”
- No “closing rate” rationale unless speed exceeds threshold

---

### TC-04: Resilience (restart service)
**Steps**
1. Seed any scenario
2. Restart `threat-scoring` container
3. Refresh COP

**Expected**
- System continues to ingest tracks
- Dashboard remains available
- New threats appear after restart
- Audit trail continues to append events

---

### TC-05: Metrics endpoints
**Steps**
1. Open:
   - http://localhost:8002/stats
   - http://localhost:8003/stats
2. Seed any scenario and refresh stats

**Expected**
- Counters increase (observations ingested, threats emitted)
- `by_priority` reflects emitted threats
