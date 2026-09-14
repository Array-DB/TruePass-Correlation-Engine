# TruePass API

Run locally with:

```bash
truepass run --host 127.0.0.1 --port 8000
```

OpenAPI is available at `/docs`. Core endpoint groups implemented in Phase 23 are `/health`, `/metrics`, `/events`, `/incidents`, `/sensors`, `/timeline`, `/correlation`, `/evidence`, `/baselines`, `/similarity`, `/system`, and `/dashboard/summary`.

`create_app(..., api_key="...")` enables the API-key authentication hook through the `X-TruePass-API-Key` header. When no key is supplied, local development remains open by default. Production deployments should place the service behind TLS and configure authentication at the application and/or reverse-proxy layer.

## Definition-of-Done realtime API additions (Phases 7–11)

The remediation API preserves the original routes and also exposes `/api/v1` aliases for core event, incident, sensor, timeline, correlation, evidence, baseline, similarity, system, alert, and dashboard data.

### Spectrum

- `GET /api/v1/spectrum` — latest processed DSP frame.
- `POST /api/v1/spectrum/capture` — acquire one receive-only frame from a configured `synthetic`, `hackrf`, or other supported SDR source; process FFT/PSD/waterfall/RF features; publish it to realtime subscribers.

### WebSocket streams

- `/ws/events`
- `/ws/spectrum`
- `/ws/incidents`
- `/ws/alerts`
- `/ws/system`

Each connection receives a `connected` message. Idle streams emit heartbeats. Stream queues are bounded so slow consumers do not create unbounded memory growth.
