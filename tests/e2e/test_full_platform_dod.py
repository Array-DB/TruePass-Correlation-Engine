from truepass.integration import FullPlatformIntegrationPipeline


def test_full_platform_definition_of_done_workflow() -> None:
    result = FullPlatformIntegrationPipeline().run()
    assert result.overall_verified
    assert result.events >= 4
    assert result.timeline_events >= 4
    assert result.ledger_records >= 4
    assert result.signed_batches >= 1
    assert result.spectrum_bins >= 16
    assert result.scan_session
