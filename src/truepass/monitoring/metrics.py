"""Prometheus metrics shared by TruePass collectors and services."""

from prometheus_client import Counter, Histogram

EVENTS_TOTAL = Counter(
    "truepass_events_total",
    "Normalized TruePass events emitted.",
    labelnames=("source", "event_type"),
)
COLLECTOR_ERRORS_TOTAL = Counter(
    "truepass_collector_errors_total",
    "Collector errors that did not terminate the service.",
    labelnames=("collector", "error_type"),
)
EVENT_PROCESSING_SECONDS = Histogram(
    "truepass_events_processing_seconds",
    "Time spent producing or processing normalized events.",
    labelnames=("component",),
)
RF_ANOMALIES_TOTAL = Counter(
    "truepass_rf_anomalies_total",
    "RF anomaly observations emitted by configured detectors.",
)
INCIDENTS_TOTAL = Counter(
    "truepass_incidents_total",
    "Incident candidates produced by the correlation engine.",
    labelnames=("severity",),
)
