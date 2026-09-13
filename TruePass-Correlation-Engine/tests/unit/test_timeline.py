from __future__ import annotations

from truepass.eventspace.timeline import ClockQuality, Timeline
from truepass.models.events import Event, EventSource, EventType, Provenance


def _event(timestamp_ns: int, source: EventSource, event_type: EventType) -> Event:
    return Event(
        timestamp_ns=timestamp_ns,
        received_timestamp_ns=timestamp_ns + 10,
        source=source,
        sensor_id=f"{source.value}-01",
        host="workstation-01",
        event_type=event_type,
        provenance=Provenance(collector="test", method="synthetic"),
    )


def test_timeline_around_and_state_snapshot() -> None:
    anchor = _event(1_000_000_000, EventSource.SDR, EventType.RF_ANOMALY)
    network = _event(1_038_000_000, EventSource.NETWORK, EventType.NETWORK_CONNECTION)
    process = _event(1_062_000_000, EventSource.PROCESS, EventType.PROCESS_STARTED)
    far = _event(3_000_000_000, EventSource.SYSTEM, EventType.INCIDENT)
    timeline = Timeline(
        [far, process, anchor, network],
        clock_quality=ClockQuality(synchronized=True, source="ntp", max_error_ns=1_000_000),
    )

    around = timeline.around(anchor.event_id, before_ms=10, after_ms=100)
    snapshot = timeline.snapshot(anchor.event_id, before_ms=10, after_ms=100)

    assert [event.event_id for event in around] == [anchor.event_id, network.event_id, process.event_id]
    assert EventSource.NETWORK in snapshot.by_source
    assert snapshot.clock_quality.synchronized is True
    assert snapshot.clock_quality.max_error_ns == 1_000_000
