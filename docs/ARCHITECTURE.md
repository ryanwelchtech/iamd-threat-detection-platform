# System Architecture

The IAMD Threat Detection Platform is a distributed, event-driven microservice
architecture designed to simulate real-world defense mission systems.

---

## Core Design Principles

- Zero Trust by default
- Stateless services
- Deterministic identity
- Human-in-the-loop decision support
- Auditability over automation

---

## Service Architecture

sensor-ingest
- Entry point for all sensor observations
- JWT validation and schema enforcement
- Forwards normalized observations downstream

track-fusion
- Correlates observations into tracks
- Maintains position, altitude, confidence, and sources
- Emits track updates on every observation

threat-scoring
- Applies rule-based scoring to tracks
- Produces priority, score, rationale, and action
- One threat per track (upsert model)

cop-dashboard
- Human-facing COP interface
- Live radar visualization
- Scenario injection for demo purposes

audit-log
- Append-only event store
- Records all system actions
- Supports traceability and recovery validation

---

## Data Flow

1. Observation ingested
2. Track created or updated
3. Threat scored
4. Events logged
5. COP updated in real-time

---

## Trust Boundaries

- External input: sensor-ingest
- Internal services: authenticated via JWT
- UI: read-only access to system state
