# Changelog

## 1.0.0 - 2026-09-13

First complete TruePass release candidate/final source release through Master Plan Phase 37.

### Added
- Comprehensive automated synthetic end-to-end integration scenario.
- Local reproducible benchmark harness and recorded benchmark output.
- Production-oriented non-root Dockerfile, persisted Compose services, health checks, and optional Prometheus.
- Complete architecture, installation, configuration, security, evidence, RF, correlation, development, troubleshooting, release, and migration documentation.
- Expanded CI/CD stages for quality, PostgreSQL integration, security auditing, E2E, and Docker build.
- Final release metadata and Definition-of-Done audit.

### Security boundaries
- Defensive/read-only collection remains the default.
- HackRF One integration remains receive-only.
- PII/biometrics never become cryptographic key entropy.
- Public timestamp anchors receive commitments only.
- Voice/EEG modules remain isolated experimental observations, not identity proof or autonomous response inputs.
