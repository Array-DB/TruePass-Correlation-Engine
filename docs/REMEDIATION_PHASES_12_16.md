# Remediation Phases 12–16

This milestone continues the expanded Overall Definition of Done. It does not declare the full platform complete.

## Phase 12 — TruePass Control Center

- Replaced the previous compact status page with an integrated operator shell.
- Added system health, event/sensor/incident/RF counters, evidence-ledger state, recent normalized evidence, and spectrum availability.
- Added responsive navigation for Dashboard, Live Monitor, Spectrum, Incidents, and TruePass-Scan.

## Phase 13 — Live Monitor, Timeline, and Incident Explorer

- Added `/api/v1/live` snapshot support plus the existing `/ws/events` stream.
- Added live event filtering, pause/resume, event detail, and correlated timeline inspection.
- Added incident list/detail investigation UI and `/api/v1/incidents/{incident_id}`.

## Phase 14 — Spectrum Dashboard

- Added an RF Spectrum page that receives frames over `/ws/spectrum`.
- Added FFT/PSD rendering, waterfall rendering, RF feature metadata, and capture state.
- Added receive-only source selection for synthetic input or HackerRF One.
- Live capture uses the existing `/api/v1/spectrum/capture` DSP path. The browser requests successive frames; each processed frame is broadcast through `/ws/spectrum`.
- Real HackerRF operation still requires SoapySDR + SoapyHackRF and connected hardware on the deployment host.

## Phase 15 — TruePass-Scan engine

- Added explicitly authorized, passive `local-host` sessions.
- Sessions snapshot existing read-only process, socket, interface, Wi-Fi, and Bluetooth telemetry.
- Added host, listening-port, process, connection, device, differential-baseline, refresh, stop, and report operations.
- This implementation intentionally does **not** perform active remote port probing, exploitation, or unauthorized scanning.

## Phase 16 — TruePass-Scan GUI

- Added authorization acknowledgement and session controls.
- Added inventory counters, listening port/process attribution, device/interface view, baseline differential, and JSON report export.

## Verification gate

The milestone is considered implemented only if the Python compile check and project test suite pass. Hardware-specific HackerRF behavior cannot be claimed as physically verified unless a HackerRF One is attached to the environment used for the test.

## Next milestone

Phases 17–21: TRUE-PASS-AGE backend, TRUE-PASS-AGE GUI, identity/alerts/management, security/privacy hardening, and complete automated testing expansion.
