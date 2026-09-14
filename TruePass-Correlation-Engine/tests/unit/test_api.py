from fastapi.testclient import TestClient
from truepass.api.server import create_app
from truepass.api.state import RuntimeState
from truepass.models.events import Event, EventSource, EventType, Provenance


def event() -> Event:
    return Event(source=EventSource.SDR, sensor_id="sdr-test", event_type=EventType.RF_ANOMALY, confidence=.8, provenance=Provenance(collector="test", method="synthetic"))


def test_api_event_and_dashboard_flow() -> None:
    state = RuntimeState()
    client = TestClient(create_app(state))
    e = event()
    r = client.post("/events", json=e.model_dump(mode="json"))
    assert r.status_code == 201
    assert client.get("/health").json()["events"] == 1
    assert client.get("/events?source=sdr").json()[0]["event_type"] == "rf_anomaly"
    summary = client.get("/dashboard/summary").json()
    assert summary["rf_anomalies"] == 1
    assert client.get("/dashboard").status_code == 200
    assert "TRUEPASS" in client.get("/dashboard").text


def test_api_errors_are_structured_by_fastapi() -> None:
    client = TestClient(create_app(RuntimeState()))
    r = client.get("/events/not-there")
    assert r.status_code == 404
    assert r.json()["detail"] == "event not found"


def test_api_key_hook_can_protect_routes() -> None:
    client = TestClient(create_app(RuntimeState(), api_key="secret"))
    assert client.get("/health").status_code == 401
    assert client.get("/health", headers={"X-TruePass-API-Key": "secret"}).status_code == 200
