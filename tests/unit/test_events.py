from uuid import UUID

import pytest
from pydantic import ValidationError

from truepass.models.events import Event, EventSource, EventType, Provenance


def make_event() -> Event:
    return Event(
        event_id=UUID("00000000-0000-0000-0000-000000000001"),
        timestamp_ns=100,
        received_timestamp_ns=120,
        source=EventSource.PROCESS,
        sensor_id="test-sensor",
        host="test-host",
        event_type=EventType.PROCESS_STARTED,
        confidence=0.8,
        features={"b": 2, "a": 1},
        metadata={"z": True, "x": "value"},
        provenance=Provenance(collector="unit-test", method="fixture"),
    )


def test_canonical_serialization_is_deterministic() -> None:
    first = make_event()
    second = make_event().model_copy(update={"features": {"a": 1, "b": 2}})
    assert first.canonical_bytes() == second.canonical_bytes()
    assert first.sha256() == second.sha256()


def test_event_is_immutable() -> None:
    event = make_event()
    with pytest.raises(ValidationError):
        event.confidence = 0.1  # type: ignore[misc]


def test_confidence_is_bounded() -> None:
    with pytest.raises(ValidationError):
        make_event().model_copy(update={"confidence": 2.0}).model_validate(
            make_event().model_dump() | {"confidence": 2.0}
        )
