# Remediation Phases 22–26

## Phase 22 — Hardware integration tests
Added receive-only `scripts/hardware_verify.py` and final DoD external hardware gate. It enumerates HackerRF through SoapySDR, captures I/Q and verifies DSP output. No transmit API exists.

## Phase 23 — Full end-to-end workflow
Added `FullPlatformIntegrationPipeline`, exercising normalized events, timeline, correlation/incident generation, synthetic spectrum, authorized Scan/report, AGE chain, signed Merkle batch and inclusion proof.

## Phase 24 — Performance/reliability
Added `scripts/reliability_soak.py` and retained the benchmark harness. Realtime queues remain bounded.

## Phase 25 — Deployment/CI/documentation
Added executable DoD/release verification artifacts, typed frontend audit compilation, and expanded release documentation.

## Phase 26 — Overall Definition-of-Done audit
Added `truepass verify dod`, `/api/v1/verification/dod`, and a Verification page. The audit never converts an unexecuted physical/infrastructure check into a pass.
