# Integrated Air & Missile Defense (IAMD) Threat Detection Platform

Portfolio-safe, mission-aligned demo platform that simulates multi-modal sensor feeds (RADAR / EO-IR / AIS) and produces:

- **Fused object tracks** (track continuity + confidence)
- **Threat scoring & prioritization** (rules + rationale)
- **Common Operational Picture (COP)** operator dashboard
- **Append-only audit logging** for traceability
- **Zero Trust** service-to-service access using JWT (demo HS256)

> This is a simulation for engineering demonstration only. No classified data, no weapon employment logic, and no sensitive tactics.

---

## Architecture (high level)

1. **sensor-ingest** receives sensor observations and normalizes payloads.
2. **track-fusion** correlates observations into tracks and maintains track confidence.
3. **threat-scoring** scores tracks into prioritized threats with explainable rationale.
4. **cop-dashboard** provides a human-in-the-loop COP view of tracks and threats.
5. **audit-log** stores append-only events for traceability.

See:
- `docs/ARCHITECTURE.md`
- `docs/INTERFACES.md`
- `docs/THREAT_MODEL.md`

---

## Quick start (local)

### Prereqs
- Docker Desktop
- PowerShell (Windows)
- Optional (for token + seed script): Python 3.11+ and `pyjwt`

### Run the stack
```bash
docker compose up --build
```

Open the COP:

http://localhost:8080

### Seed sensor data
```powershell
.\scripts\seed-data.ps1
```

Audit events:
- http://localhost:8004/events

Health checks:
- sensor-ingest: http://localhost:8001/health
- track-fusion: http://localhost:8002/health
- threat-scoring: http://localhost:8003/health
- audit-log: http://localhost:8004/health
- cop-dashboard: http://localhost:8080/health

### Zero Trust (demo JWT)

Write endpoints require an auth header:
```powershell
Authorization: Bearer <token>
```

Generate a dev token:
```powershell
.\scripts\new-jwt.ps1 -Subject "operator@demo.local" -Role "operator"
```

### Notes:

-Local demo uses HS256 with JWT_SECRET (shared secret).
-In a real environment, use a managed secret store + rotation, mTLS, signed images, and policy enforcement.

# Operations Runbook

This runbook supports local development, demo execution, and troubleshooting
for the Integrated Air & Missile Defense (IAMD) Threat Detection Platform.

---

## Service Health Endpoints

| Service | URL |
|------|-----|
| sensor-ingest | http://localhost:8001/health |
| track-fusion | http://localhost:8002/health |
| threat-scoring | http://localhost:8003/health |
| audit-log | http://localhost:8004/health |
| cop-dashboard | http://localhost:8080/health |

---

## Normal Demo Flow

1. Start all services with Docker Compose
2. Open the COP dashboard
3. Load scenarios using the UI buttons:
   - Load Benign
   - Load Air
   - Load Sea
4. Observe:
   - Radar population (non-refresh, real-time)
   - Track continuity
   - Threat scoring + rationale
   - Audit events

---

## Common Issues & Fixes

### COP shows no tracks or threats
- Ensure all services are healthy
- Click a scenario button in the UI (no page refresh required)

### Radar shows but no objects
- Confirm track-fusion has active tracks:
  http://localhost:8002/tracks
- Confirm threat-scoring has threats:
  http://localhost:8003/threats

### 401 Unauthorized errors
- Write endpoints require JWT
- Generate a dev token:
  ```powershell
  .\scripts\new-jwt.ps1 -Subject "operator@demo.local" -Role "operator"
  ```

### Scenario button fails
- Check cop-dashboard logs:
  ```powershell
  docker compose logs cop-dashboard
  ```
- Verify sensor-ingest validation errors are not occurring

### Services fail to start
- Inspect logs:
  ```powershell
  docker compose logs <service>
  ```

---

## Clear / Reset Behavior

- "Clear Radar" button:
  - Resets track-fusion, threat-scoring, and audit-log
  - Clears radar, tables, and top-level counters
  - Does NOT refresh the page

---

## Recovery Behavior

- Services are stateless by design
- Restarting any service does not corrupt others
- Audit-log persists events until reset
- Tracks and threats are rebuilt from new observations

---

## Demo Safety Notes

- No classified data
- No weapon employment logic
- No real-world targeting
- Recommendations only (human-in-the-loop)

## Project structure
```text
iamd-threat-detection-platform/
  services/
    sensor-ingest/
    track-fusion/
    threat-scoring/
    cop-dashboard/
    audit-log/
  deploy/
    k8s/
  docs/
  scripts/
  policy/
```

## Demo scenarios

-Baseline traffic: seed radar/EO-IR/AIS samples and confirm tracks populate.
-Escalation: inject a high-speed closing track and observe threat score + rationale.
-Resilience: restart a service and confirm recovery behavior + audit trail continuity.

See `docs/DEMO_SCRIPT.md`.

## Security & compliance posture (demo)

- `policy/policy.json` demonstrates a release gate concept (block Critical/High; track Medium/Low).

- `docs/THREAT_MODEL.md` documents trust boundaries and mitigations.