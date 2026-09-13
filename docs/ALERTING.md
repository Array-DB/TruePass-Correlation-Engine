# Alerting

Phase 25 adds evidence-first alert generation. Rules match normalized events and produce alerts that explain **why** they fired. `AlertEngine` deduplicates equivalent alerts using a stable rule/sensor/host/event-type key and enforces a per-rule cooldown to reduce operator fatigue.

Default rules cover RF anomalies, new listening-port observations, and incident candidates. Alerts are reporting artifacts only: they do not block traffic, transmit RF, kill processes, or modify monitored systems. `/alerts` exposes current explainable alert candidates through the FastAPI service.
