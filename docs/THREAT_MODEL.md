# Threat Model (Portfolio-Safe)

This threat model is intentionally high-level and avoids real-world tactics, techniques, or classified considerations.

---

## Assets

- Integrity of track and threat outputs
- Availability of COP dashboard
- Audit log immutability
- Operator trust in system recommendations

---

## Trust Boundaries

1. **External Sensors → sensor-ingest**
   - Untrusted input boundary
   - Schema validation required

2. **Service-to-Service APIs**
   - Authenticated via JWT
   - Explicit role-based access

3. **Operator UI**
   - Read-only access to mission state
   - Human-in-the-loop control

---

## Representative Threats & Mitigations

| Threat | Mitigation |
|------|-----------|
| Malformed input | Schema validation |
| Spoofed service calls | JWT authentication |
| Data tampering | Append-only audit log |
| Silent failure | Health checks + probes |
| Over-automation risk | Human review required |

---

## Notes

This model focuses on **engineering discipline**, not tactical realism.