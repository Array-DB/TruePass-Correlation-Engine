from fastapi.testclient import TestClient

from truepass.api.server import create_app
from truepass.api.state import RuntimeState


def test_scan_requires_authorization_and_local_scope() -> None:
    client = TestClient(create_app(RuntimeState()))
    denied = client.post("/api/v1/scan/sessions")
    assert denied.status_code == 422
    remote = client.post(
        "/api/v1/scan/sessions",
        params={"authorization_acknowledged": True, "scope": "remote-network"},
    )
    assert remote.status_code == 422


def test_authorized_scan_session_exposes_passive_inventory() -> None:
    client = TestClient(create_app(RuntimeState()))
    response = client.post(
        "/api/v1/scan/sessions",
        params={"authorization_acknowledged": True, "scope": "local-host"},
    )
    assert response.status_code == 200
    session = response.json()
    session_id = session["session_id"]
    assert session["authorization_acknowledged"] is True
    assert session["scope"] == "local-host"
    assert client.get(f"/api/v1/scan/sessions/{session_id}/hosts").status_code == 200
    assert client.get(f"/api/v1/scan/sessions/{session_id}/ports").status_code == 200
    assert client.get(f"/api/v1/scan/sessions/{session_id}/processes").status_code == 200
    assert client.get(f"/api/v1/scan/sessions/{session_id}/connections").status_code == 200
    assert client.get(f"/api/v1/scan/sessions/{session_id}/devices").status_code == 200
    diff = client.get(f"/api/v1/scan/sessions/{session_id}/diff")
    assert diff.status_code == 200
    assert "processes" in diff.json()
    report = client.get(f"/api/v1/scan/sessions/{session_id}/report")
    assert report.status_code == 200
    assert report.json()["session"]["session_id"] == session_id


def test_operator_pages_serve_integrated_control_center() -> None:
    client = TestClient(create_app(RuntimeState()))
    for path in ("/", "/dashboard", "/live", "/spectrum", "/scan", "/incidents/view"):
        response = client.get(path)
        assert response.status_code == 200
        assert "TRUEPASS™ CONTROL CENTER" in response.text
    html = client.get("/spectrum").text
    assert "HackerRF One" in html
    assert "/ws/spectrum" in html
    assert "TruePass-Scan" in html
