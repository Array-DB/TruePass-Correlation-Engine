# TruePass Overall Definition of Done

This document is the executable release gate for the integrated TruePass platform.

## Release rule

TruePass distinguishes two states:

1. **Implementation complete** — all source-level, synthetic, API, GUI-route, evidence, correlation, Scan, realtime, TypeScript audit, packaging, and documentation checks pass.
2. **Environment verified** — deployment-specific checks pass on the target machine: physical HackerRF receive path, PostgreSQL/pgvector, and Docker runtime.

`truepass verify dod` reports both states. A missing physical device, database URL, or Docker daemon is reported as a failed external gate and is never silently marked as passed.

## Phase 22 — Hardware integration

- Receive-only HackerRF source enumerates through SoapySDR/SoapyHackRF.
- Hardware verification captures I/Q samples and runs them through FFT/PSD/waterfall.
- `scripts/hardware_verify.py` is the deployment-host verification command.
- Spectrum API supports `device=hackrf` without exposing a transmit path.

Run on the machine with HackerRF One connected:

```bash
python scripts/hardware_verify.py
```

## Phase 23 — Full end-to-end workflow

`FullPlatformIntegrationPipeline` and `tests/e2e/test_full_platform_dod.py` verify:

```text
Synthetic RF observation
  -> normalized event
  -> live/API event state
  -> correlated timeline
  -> incident generation
  -> authorized TruePass-Scan session/report
  -> evidence hash chain
  -> signed Merkle batch
  -> inclusion proof
  -> TRUE-PASS-AGE verification
```

The Spectrum API additionally verifies FFT, PSD, waterfall, RF assessment, and cluster metadata.

## Phase 24 — Performance and reliability

- `scripts/benchmark.py` covers event serialization, persistence, correlation, FFT/spectrogram and vector-query throughput.
- `scripts/reliability_soak.py` performs a bounded repeated synthetic spectrum workload and reports throughput and Python peak memory.
- Realtime channels remain bounded and discard the oldest queued frame under backpressure rather than growing without limit.

## Phase 25 — Deployment, CI and documentation

The release contains:

- Dockerfile and Compose deployment.
- PostgreSQL/pgvector integration CI.
- lint, format, strict type check, tests, compile checks and dependency audit CI jobs.
- release verification script.
- on-host hardware verification script.
- executable Overall DoD verifier.
- typed frontend audit sources compiled under `frontend/tsconfig.json`.
- installation, configuration, security, privacy, RF, evidence, API and troubleshooting documentation.

## Phase 26 — Overall Definition-of-Done audit

Run the source/runtime release gate:

```bash
truepass verify dod --no-external
```

Run the complete target-host gate:

```bash
truepass verify dod
```

The complete gate checks:

- Control Center/operator routes.
- live spectrum products.
- RF assessment and clustering metadata.
- complete synthetic cross-domain workflow.
- deployment/release artifacts.
- TypeScript compilation.
- physical HackerRF receive integration.
- PostgreSQL connectivity.
- Docker daemon availability.

## GUI requirements

The integrated Control Center exposes Dashboard, Live Monitor, Timeline, Spectrum, Incidents, TruePass-Scan, TRUE-PASS-AGE, Alerts, Settings and Verification.

Spectrum renders FFT/PSD and waterfall frames and exposes RF anomaly/cluster metadata. Live Monitor supports filtering and pause/resume. Timeline exposes event provenance and correlation context. Scan remains authorized passive local-host observation. AGE provides chain, Merkle inclusion-proof and signature verification. The UI includes responsive layout, light/dark theme, visible health/reconnect state and useful empty/error states.

## Scientific and security boundary

An RF anomaly, unknown cluster, temporal correlation, or candidate path is not proof of compromise or causation. TruePass preserves the distinction between observed facts, derived measurements, statistical/model inference, correlation, operator interpretation, and cryptographically verified integrity facts.
