# Operations Runbook

This runbook supports local development and demo execution.

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

## Common Issues

### COP shows no data
- Run the seed script:
  ```powershell
  .\scripts\seed-data.ps1
  ```

### 401 Unauthorized errors

- Ensure requests include a valid JWT
- Use:
    ```powershell
    .\scripts\new-jwt.ps1
    ```

### Service not starting

- Check Docker logs:
    ```powershell
    docker compose logs <service>
    ```

## Recovery Behavior

- Services are stateless by design
- Restarting a service does not corrupt others
- Audit events persist for post-restart review