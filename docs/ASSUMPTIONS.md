# Assumptions

This project is a **portfolio-safe simulation**, not an operational system.

---

## Operational Assumptions

- No classified inputs
- No real-world targeting
- No weapon employment logic
- Human-in-the-loop decisions only

---

## Technical Assumptions

- Stateless services
- In-memory state resets on restart
- JWT shared secret (demo only)
- Single-region deployment

---

## Demo Assumptions

- Scenario buttons simulate sensor input
- Coordinates are randomized within bounded ranges
- Threat scoring is illustrative, not predictive

## Demo Scope Note
This hosted demo operates with a shared in-memory state across users to simplify public access and ensure stability.

In a production environment, track, threat, and audit state would be scoped per mission, per operator, or per security domain using session identifiers, tenant isolation, or backing data stores (e.g., Redis or Postgres).
