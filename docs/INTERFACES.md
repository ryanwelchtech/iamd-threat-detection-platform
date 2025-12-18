# Service Interfaces

---

## sensor-ingest

POST /observations
- Auth: Bearer JWT
- Validates observation schema
- Forwards to track-fusion

GET /health

---

## track-fusion

POST /observations
- Creates or updates tracks

GET /tracks
GET /stats
POST /reset

---

## threat-scoring

POST /tracks
- Scores tracks into threats

GET /threats
GET /stats
POST /reset

---

## audit-log

GET /events
POST /reset

---

## cop-dashboard

GET /
POST /scenario/{type}
POST /clear
