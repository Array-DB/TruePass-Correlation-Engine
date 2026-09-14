# Remediation Phases 17–21

This milestone continues the expanded TruePass Definition-of-Done remediation. It does not declare the entire platform complete.

## Phase 17 — TRUE-PASS-AGE backend

- Added a stateful `AgeService` that owns the local append-only evidence chain.
- Live API events are durably appended to the same chain used by AGE.
- Added ledger status, record browsing, individual record verification, signed Merkle batch creation, batch verification, inclusion proofs, Merkle metadata, and explicit opt-in anchor status endpoints.
- Evidence batch roots are signed with an isolated runtime Ed25519 signing key; identity inputs are never key material.
- Full-chain verification is used for record trust so an intact later row cannot hide a broken earlier link.

Primary endpoints:

- `GET /api/v1/ledger/status`
- `GET /api/v1/ledger/records`
- `GET /api/v1/ledger/records/{sequence}`
- `POST /api/v1/ledger/batches`
- `GET /api/v1/ledger/batches/{batch_id}/verify`
- `GET /api/v1/evidence/{sequence}/proof?batch_id=...`
- `GET /api/v1/merkle/{batch_id}`
- `GET /api/v1/anchors`

## Phase 18 — TRUE-PASS-AGE GUI

The integrated Control Center now exposes `/age` with:

- chain-valid/broken state;
- record count and chain head;
- evidence ledger browsing;
- individual record verification;
- signed evidence-batch creation;
- Merkle root, Ed25519 signature verification, and inclusion-proof inspection.

The UI intentionally does not imply that an external public anchor exists when none has been configured.

## Phase 19 — Identity, alerts, and management

- Added optional context-based identity verification API separated from cryptographic key generation.
- Alert generation now runs when events enter the runtime, preserving cooldown/deduplication state rather than recomputing a new engine per request.
- Added Alert Center and alert summary API.
- Added model inventory and runtime settings APIs/UI.
- Added security-sensitive settings validation; TruePass-Scan scope remains `local-host` only.
- Identity and settings actions are recorded in a bounded operational audit surface.

## Phase 20 — Security/privacy hardening

- Added HTTP response hardening headers: content-type sniff prevention, frame denial, no-referrer, restrictive browser permissions, CSP, and no-store for API responses.
- WebSockets now enforce the configured TruePass API key when API-key protection is enabled.
- API-key comparison remains constant-time.
- Added security-status, privacy-policy, retention-decision, and audit endpoints.
- External evidence anchoring remains opt-in and is never automatically enabled.
- Scan remains passive/read-only and constrained to the local host.

## Phase 21 — Automated testing expansion

Added coverage for:

- AGE append → chain verify → signed Merkle batch → signature verify → inclusion proof;
- missing evidence records;
- ledger tamper detection;
- identity verification;
- management settings validation;
- privacy/security status endpoints;
- API security headers and API-key protection;
- runtime alert persistence/summary;
- AGE, Alert Center, and Settings UI routes.

### Validation in this packaging environment

- `python -m compileall -q src tests`: required before packaging.
- `pytest -q`: **78 passed, 1 skipped** at the first full regression gate; final package count may be higher after package-only checks.
- The skipped test is the external PostgreSQL integration test and requires `TRUEPASS_TEST_DATABASE_URL`.

## Next phases

22. Hardware integration tests.
23. Full end-to-end workflow.
24. Performance/reliability validation.
25. Deployment/CI/documentation completion.
26. Overall Definition-of-Done audit.
