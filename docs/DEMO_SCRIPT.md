# Demo Script (5–8 minutes)

This script is designed for recruiter or interview demos.

---

## 1. Context (1 minute)

- Explain the goal: **threat detection and decision support**
- Emphasize: simulation, portfolio-safe, human-in-the-loop

---

## 2. Architecture Walkthrough (2 minutes)

- Show `docs/ARCHITECTURE.md`
- Call out service boundaries and trust zones

---

## 3. Live Demo (3 minutes)

```bash
docker compose up --build
``` 

```powershell
.\scripts\seed-data.ps1
``` 

- Open COP: http://localhost:8080
- Show tracks appearing
- Highlight threat score + rationale

4. Traceability (1 minute)
- Open audit events:
http://localhost:8004/events
- Show how decisions are logged

5. Close (1 minute)
- Explain how this maps to real mission systems
- Mention extensions: metrics, SAST, SBOMs, admission control