from fastapi.testclient import TestClient

from truepass.api.server import create_app
from truepass.api.state import RuntimeState


def test_identity_settings_privacy_and_security_status() -> None:
    client = TestClient(create_app(RuntimeState()))
    identity = client.post(
        "/api/v1/identity/verify",
        json={"subject_id": "operator-1", "operator_verified": True},
    )
    assert identity.status_code == 200
    assert identity.json()["authorized"] is True

    patch = client.patch(
        "/api/v1/settings",
        json={"rf_anomaly_threshold": 0.82, "incident_threshold": 0.71, "scan_scope": "local-host"},
    )
    assert patch.status_code == 200
    assert patch.json()["rf_anomaly_threshold"] == 0.82

    policies = client.get("/api/v1/privacy/policies")
    assert policies.status_code == 200
    assert any(item["domain"] == "forensics" for item in policies.json())

    security = client.get("/api/v1/security/status")
    assert security.status_code == 200
    assert security.json()["security_headers"] is True
    assert security.headers["x-content-type-options"] == "nosniff"
    assert security.headers["x-frame-options"] == "DENY"


def test_settings_reject_non_local_scan_scope() -> None:
    client = TestClient(create_app(RuntimeState()))
    response = client.patch("/api/v1/settings", json={"scan_scope": "remote"})
    assert response.status_code == 422


def test_api_cache_control_and_key_protection() -> None:
    client = TestClient(create_app(RuntimeState(), api_key="secret"))
    assert client.get("/api/v1/security/status").status_code == 401
    response = client.get("/api/v1/security/status", headers={"X-TruePass-API-Key": "secret"})
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"


def test_age_alerts_and_settings_dashboard_routes_exist() -> None:
    client = TestClient(create_app(RuntimeState()))
    for path in ("/age", "/alerts/view", "/settings"):
        response = client.get(path)
        assert response.status_code == 200
        assert "TRUEPASS" in response.text
