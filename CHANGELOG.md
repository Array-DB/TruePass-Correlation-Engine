# Changelog

## 1.0.0 Overall Definition of Done completion - 2026-09-14

- Completed remediation Phases 22–26.
- Added physical receive-only HackerRF host verification.
- Added full-platform E2E workflow covering events, timeline, incidents, Scan, spectrum, AGE, signed Merkle batches and inclusion proofs.
- Added RF assessment and cluster metadata to live spectrum frames.
- Added Timeline and Overall DoD Verification operator pages, theme toggle, reconnect status, and Alert layout repair.
- Added reliability soak tooling, typed frontend audit compile, and executable `truepass verify dod` gate.
- Source/runtime Overall DoD gate passes in the release build; physical/infrastructure checks remain explicit target-host evidence and are never fabricated.

## Definition-of-Done remediation — Phases 7–11 - 2026-09-14

- Added integrated RF intelligence service with bounded online baselining and anomaly assessment.
- Added incident orchestration and safer correlation-score aggregation.
- Added PostgreSQL pgvector migration with HNSW cosine indexing plus repository hardening.
- Added signed Merkle evidence batches and inclusion-proof verification.
- Added bounded realtime WebSocket channels and `/api/v1/spectrum/capture` → `/ws/spectrum` transport.
- Overall Definition of Done remains in progress; modern Control Center, Spectrum UI, TruePass-Scan, and TRUE-PASS-AGE remain later remediation milestones.

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
