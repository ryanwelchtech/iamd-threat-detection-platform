# System Architecture

This project models a simplified **Integrated Air & Missile Defense (IAMD)** threat detection pipeline using loosely coupled microservices.

The goal is to demonstrate **systems engineering thinking**:
- Clear service boundaries
- Defined interfaces
- Failure-tolerant behavior
- Human-in-the-loop decision support

---

## High-Level Data Flow

1. **sensor-ingest**
   - Accepts simulated RADAR, EO/IR, and AIS observations
   - Validates schema and enforces authentication
   - Emits normalized observations

2. **track-fusion**
   - Correlates observations into object tracks
   - Maintains track confidence and source attribution
   - Handles sensor dropouts gracefully

3. **threat-scoring**
   - Evaluates tracks against policy-driven rules
   - Produces threat priority, score, and rationale
   - Designed for explainability, not autonomy

4. **cop-dashboard**
   - Displays tracks and threats to an operator
   - Enables human-in-the-loop assessment

5. **audit-log**
   - Stores append-only events
   - Enables traceability and after-action review

---

## Logical Architecture Diagram

```text
[Sensors]
   |
   v
[sensor-ingest]
   |
   v
[track-fusion]
   |
   +--> [cop-dashboard]
   |
   v
[threat-scoring]
   |
   +--> [cop-dashboard]

(All services emit events to audit-log)
```

## Design Principles
- Zero Trust by default: all write operations require authentication
- Loose coupling: services communicate via explicit APIs
- Explainability over automation: system recommends, humans decide
- Auditability: every major action generates an audit event