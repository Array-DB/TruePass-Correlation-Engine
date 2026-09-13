# TruePass v1.0.0 Release Checklist

- [x] Source compiles on Python 3.13 in the build environment.
- [x] Unit/API/DSP/correlation/evidence/configuration/security/E2E tests execute.
- [x] Synthetic E2E persists an incident, verifies ledger/Merkle integrity, and returns the incident through the API.
- [x] Local benchmark harness exists and results are stored under `docs/benchmarks/`.
- [x] Dockerfile uses a non-root user and health check.
- [x] Docker Compose defines TruePass, PostgreSQL/pgvector, persisted volumes, health checks, and optional Prometheus.
- [x] GitHub Actions defines format/lint/type/test/integration/security/Docker stages.
- [x] Security/privacy/cryptography/permissions/defaults/error-handling documentation reviewed.
- [x] Release notes, migration notes, sample configuration, known limitations, and changelog are present.
- [ ] Physical HackRF One capture validation on operator hardware (hardware unavailable in build sandbox).
- [ ] Full PostgreSQL/pgvector Compose startup validation in an environment with Docker daemon access.
- [ ] Ruff/mypy/pip-audit execution in a dependency-complete environment (tools unavailable in build sandbox if noted in development status).

Unchecked environment-dependent items are explicit release limitations, not silently reported as passing.
