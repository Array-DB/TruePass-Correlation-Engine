from fastapi.testclient import TestClient
from truepass.api.server import create_app
from truepass.api.state import RuntimeState


def test_synthetic_spectrum_capture_is_browser_ready() -> None:
    client = TestClient(create_app(RuntimeState()))
    response = client.post(
        "/api/v1/spectrum/capture",
        params={"device": "synthetic", "samples": 1024, "center_frequency": 100_000_000},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "synthetic"
    assert len(payload["frequencies_hz"]) > 0
    assert len(payload["fft_magnitude_db"]) == len(payload["frequencies_hz"])
    assert payload["waterfall_db_per_hz"]
    assert client.get("/api/v1/spectrum").status_code == 200


def test_realtime_websocket_contract_connects() -> None:
    client = TestClient(create_app(RuntimeState()))
    with client.websocket_connect("/ws/spectrum") as websocket:
        hello = websocket.receive_json()
        assert hello == {"type": "connected", "channel": "spectrum"}
