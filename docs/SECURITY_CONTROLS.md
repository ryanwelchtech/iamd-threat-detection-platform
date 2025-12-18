# Security Controls (Demo Mapping)

This mapping is portfolio-safe and demonstrates security engineering intent. It is not a formal compliance attestation.

## Access control
- JWT-based authn/authz for write paths (sensor-ingest and track-fusion)
- Explicit roles: sensor / operator / system

## Audit and accountability
- Append-only audit events emitted for:
  - observation ingestion
  - track create/update
  - threat emission
- After-action review supported via `/events`

## Configuration management
- Version-controlled infrastructure and manifests:
  - Docker Compose
  - Kubernetes YAML
  - CI workflow

## System and communications protection
- Service boundaries defined with explicit APIs
- Recommendation: replace demo HS256 with managed identity (OIDC), mTLS, and short-lived tokens

## Vulnerability management / release gating
- `policy/policy.json` demonstrates release gates:
  - block on Critical/High
  - track Medium/Low with backlog requirement
- Recommendation: enforce via Trivy/SCA + SBOM checks in CI

## Availability / resilience
- Health endpoints per service
- Kubernetes readiness/liveness probes included in manifests
- Fail-open audit submission (audit does not break mission flow)
