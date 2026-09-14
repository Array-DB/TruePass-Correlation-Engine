# Realtime ingest and visualization

The local API now starts passive host telemetry automatically when `truepass run` starts, unless `TRUEPASS_AUTO_COLLECT=0` is set.

Active read-only collectors:

- host telemetry (CPU, memory, disk, network throughput, process and connection counts)
- process lifecycle changes
- local socket/network changes
- Wi-Fi state changes
- Bluetooth state changes

Host telemetry is emitted as normalized `system/host_snapshot` events every two seconds. These events use the same realtime WebSocket and AGE evidence path as other normalized events.

The Dashboard charts are data-bound to `/api/v1/dashboard` and `/api/v1/telemetry/status`. They show measured host history, source counts, collector health and current ingest rate. No placeholder values are generated for those charts.

Spectrum provenance is explicit: `synthetic-test` is generated I/Q and `hardware-rx` is receive-only SDR I/Q. Synthetic data is labeled as a test signal in the UI and must not be represented as physical RF observation.
