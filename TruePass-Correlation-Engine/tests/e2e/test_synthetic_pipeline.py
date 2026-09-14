from truepass.integration import SyntheticIntegrationPipeline


def test_synthetic_end_to_end_pipeline() -> None:
    result = SyntheticIntegrationPipeline().run()
    assert result.events == 4
    assert result.correlation_score > 0
    assert result.incident_score > 0
    assert result.ledger_verified
    assert result.merkle_verified
    assert result.api_incident_visible
