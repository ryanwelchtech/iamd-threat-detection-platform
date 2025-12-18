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
