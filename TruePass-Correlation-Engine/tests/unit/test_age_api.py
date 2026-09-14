from fastapi.testclient import TestClient

from truepass.api.server import create_app
from truepass.api.state import RuntimeState
from truepass.models.events import Event, EventSource, EventType, Provenance


def evidence_event() -> Event:
    return Event(
        source=EventSource.SYSTEM,
        sensor_id="age-test",
        event_type=EventType.EVIDENCE_RECORD,
        provenance=Provenance(collector="age-test", method="unit"),
    )


def test_age_chain_batch_signature_and_proof() -> None:
    state = RuntimeState()
    client = TestClient(create_app(state))
    first = evidence_event()
    second = evidence_event()
    assert client.post("/api/v1/events", json=first.model_dump(mode="json")).status_code == 201
    assert client.post("/api/v1/events", json=second.model_dump(mode="json")).status_code == 201

    status = client.get("/api/v1/ledger/status").json()
    assert status["valid"] is True
    assert status["records"] == 2

    batch_response = client.post("/api/v1/ledger/batches")
    assert batch_response.status_code == 200
    batch = batch_response.json()
    assert batch["leaf_count"] == 2

    verification = client.get(f"/api/v1/ledger/batches/{batch['batch_id']}/verify").json()
    assert verification["signature_valid"] is True

    proof = client.get(
        f"/api/v1/evidence/1/proof?batch_id={batch['batch_id']}"
    ).json()
    assert proof["verified"] is True


def test_age_missing_record_is_404() -> None:
    client = TestClient(create_app(RuntimeState()))
    assert client.get("/api/v1/ledger/records/1").status_code == 404


def test_age_detects_ledger_tampering() -> None:
    import json

    state = RuntimeState()
    client = TestClient(create_app(state))
    item = evidence_event()
    client.post("/api/v1/events", json=item.model_dump(mode="json"))
    rows = state.age.path.read_text(encoding="utf-8").splitlines()
    record = json.loads(rows[0])
    record["event_hash"] = "0" * 64
    state.age.path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    status = client.get("/api/v1/ledger/status").json()
    assert status["valid"] is False
    assert status["error"] is not None
