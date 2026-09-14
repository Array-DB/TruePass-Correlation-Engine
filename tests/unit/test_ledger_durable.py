from __future__ import annotations

from truepass.evidence.ledger import FileEvidenceLedger
from truepass.models.events import Event, EventSource, EventType, Provenance


def _event() -> Event:
    return Event(
        source=EventSource.SYSTEM,
        sensor_id="durability-test",
        event_type=EventType.EVIDENCE_RECORD,
        provenance=Provenance(collector="test", method="unit"),
    )


def test_records_and_sequence_lookup(tmp_path) -> None:
    ledger = FileEvidenceLedger(tmp_path / "ledger.jsonl")
    first = ledger.append(_event())
    second = ledger.append(_event())
    assert first.sequence == 1
    assert second.sequence == 2
    assert len(ledger.records()) == 2
    assert ledger.get_record(2) == second
    assert ledger.get_record(0) is None
    assert ledger.verify().valid
