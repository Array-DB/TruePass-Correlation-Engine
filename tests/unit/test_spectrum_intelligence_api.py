from fastapi.testclient import TestClient
from truepass.api.server import create_app
from truepass.api.state import RuntimeState


def test_spectrum_exposes_rf_assessment_and_cluster_metadata() -> None:
    client = TestClient(create_app(RuntimeState()))
    response = client.post("/api/v1/spectrum/capture?device=synthetic&samples=4096")
    assert response.status_code == 200
    data = response.json()
    assert "rf_assessment" in data
    assert "cluster" in data
    assert data["rf_assessment"]["sample_count"] >= 1
