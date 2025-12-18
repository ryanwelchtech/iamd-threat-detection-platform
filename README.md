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

---

## Quick Start (Hosted Demo on AWS EC2)

This platform can be hosted as a publicly accessible demo so non-technical
users (recruiters, managers, interviewers) can view the COP dashboard without
running Docker locally.

### Hosting Model

- Single EC2 instance (t3.medium or larger)
- Docker + Docker Compose
- Public HTTP access (port 8080)
- No authentication required for read-only demo

### EC2 Setup (High-Level)

1. Launch EC2 (Amazon Linux 2023 or Ubuntu 22.04)
2. Open inbound ports:
   - 22 (SSH)
   - 8080 (COP dashboard)
3. Install Docker and Docker Compose
4. Clone the repository
5. Start the stack

```bash
sudo yum install docker -y
sudo systemctl start docker
sudo usermod -aG docker ec2-user
```

```bash
docker-compose up --build
```

### Access the Demo

Open in a browser:
http://<EC2_PUBLIC_IP>:8080

### Demo Safety Notes

- Read-only dashboard
- No real sensor data
- No weapon logic
- No persistence beyond runtime

This hosted demo is intended for **visual and architectural evaluation only**.


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