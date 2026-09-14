# TruePass Control Center Dashboard

Phase 24 provides an operator dashboard at `/dashboard`. It surfaces system health, normalized event volume, sensor count, incident count, RF anomaly count, evidence-ledger verification status, and recent normalized evidence.

The dashboard intentionally states the core analytical limitation: correlation does not independently establish causation. It consumes only the local TruePass API and sends no telemetry to a third party.

This phase establishes the operator surface and API contract. Rich spectrogram/Plotly views and the larger React/TypeScript application described in the extended UI roadmap can build on the same endpoints without changing the trusted telemetry core.
