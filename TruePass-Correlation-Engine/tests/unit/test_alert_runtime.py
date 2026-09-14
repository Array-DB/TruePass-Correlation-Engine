from fastapi.testclient import TestClient

from truepass.api.server import create_app
from truepass.api.state import RuntimeState
from truepass.models.events import Event, EventSource, EventType, Provenance


def test_alert_is_persisted_in_runtime_and_exposed() -> None:
    state = RuntimeState()
    client = TestClient(create_app(state))
    event = Event(
        source=EventSource.SDR,
        sensor_id="sdr-alert",
        event_type=EventType.RF_ANOMALY,
        provenance=Provenance(collector="test", method="synthetic"),
    )
    assert client.post("/api/v1/events", json=event.model_dump(mode="json")).status_code == 201
    alerts = client.get("/api/v1/alerts").json()
    assert len(alerts) == 1
    assert alerts[0]["rule_id"] == "rf-anomaly"
    assert client.get("/api/v1/alerts/summary").json()["total"] == 1
