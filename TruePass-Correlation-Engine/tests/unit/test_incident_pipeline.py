from truepass.incidents.pipeline import IncidentPipeline
from truepass.models.events import Event, EventSource, EventType, Provenance


def event(source, event_type, timestamp, features=None):
    return Event(
        timestamp_ns=timestamp,
        received_timestamp_ns=timestamp,
        source=source,
        sensor_id="sensor",
        host="host",
        event_type=event_type,
        features=features or {},
        provenance=Provenance(collector="test", method="synthetic"),
    )


def test_incident_pipeline_preserves_evidence_and_no_causation_claim() -> None:
    rf = event(EventSource.SDR, EventType.RF_ANOMALY, 1_000_000_000, {"anomaly_score": .9})
    process = event(EventSource.PROCESS, EventType.PROCESS_STARTED, 1_020_000_000)
    network = event(EventSource.NETWORK, EventType.NETWORK_CONNECTION, 1_030_000_000)
    result = IncidentPipeline(window_ms=100).evaluate(rf, [rf, process, network])
    assert 0 <= result.score <= 1
    assert len(result.evidence_ids) == 3
    assert result.explanations
    assert result.causation_established is False
