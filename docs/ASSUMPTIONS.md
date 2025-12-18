# Assumptions

This project is a portfolio-safe simulation intended to demonstrate systems engineering and DevSecOps practices.

## Operational assumptions
- Inputs are simulated (RADAR / EO-IR / AIS); no real sensor integration.
- The system provides recommendations only; human operators make decisions.
- Threat scoring is policy-driven and explainable, not autonomous.

## Data/model assumptions
- Observations use a normalized schema (`docs/INTERFACES.md`).
- Track fusion uses simple correlation logic suitable for demo and testing.
- IDs are generated locally (incrementing) and are not globally unique in a distributed sense.

## Security assumptions
- Local demo uses HS256 JWT with a shared secret (`JWT_SECRET`) for simplicity.
- In production, identity would use centrally managed keys, rotation, and stronger authn/authz controls (mTLS, OIDC, etc.).

## Reliability assumptions
- Services are designed to be restart-tolerant (stateless demo), with health endpoints for liveness/readiness.
- Audit logging is “fail-open” for demo resilience (audit failures do not block mission flow).
