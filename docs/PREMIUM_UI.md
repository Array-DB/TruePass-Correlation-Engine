# TruePass Premium Operator UI

This release upgrades the Control Center presentation without changing the forensic meaning of backend data.

## Upgraded surfaces

- Dashboard: clearer operational hierarchy, premium metric cards, evidence table, status hierarchy.
- Live Monitor: sticky event table, source/severity chips, readable confidence, improved detail presentation.
- Timeline: stronger investigation layout, event-source chips, syntax-highlighted provenance/correlation details.
- Spectrum: larger FFT/PSD plot, grid/axis labels, spectral fill, larger waterfall, anomaly status, structured RF metadata cards.
- Incidents: severity chips and score/confidence progress visualization.
- TruePass-Scan: improved session metrics, passive-scope status, cleaner inventory/differential presentation.
- TRUE-PASS-AGE: stronger chain state hierarchy, ledger readability, proof/signature detail highlighting.
- Alerts: professional triage table with severity/rule hierarchy.
- Settings: improved configuration hierarchy and readable security/privacy/model details.
- Verification: clearer release assurance metrics and check status presentation.
- Theme: polished dark/light themes with persistent selection.

## Runtime dependency fix

`websockets>=15,<16` is now an explicit project dependency so Uvicorn can service `/ws/events` and `/ws/spectrum` after a normal local install.
