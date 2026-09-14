from __future__ import annotations

from datetime import UTC, datetime, timedelta
from dataclasses import replace

from truepass.detection.baseline import RFBaselineTrainer, RollingRFBaseline
from truepass.spectrum.features import extract_rf_features
from truepass.sdr.sources import SDRConfig, SyntheticIQSource


def test_rf_baseline_scores_large_deviation_higher() -> None:
    source = SyntheticIQSource(SDRConfig(sample_rate=1_000_000.0, center_frequency=100_000_000.0), noise_amplitude=0.01)
    features = [
        extract_rf_features(source.read_samples(2048), sample_rate_hz=1_000_000.0, center_frequency_hz=100_000_000.0)
        for _ in range(5)
    ]
    now = datetime.now(UTC)
    baseline = RFBaselineTrainer().fit(
        features,
        sensor_id="sdr-01",
        frequency_band_hz=(99_500_000.0, 100_500_000.0),
        training_start=now - timedelta(minutes=5),
        training_end=now,
        hour_bucket=now.hour,
    )
    normal_score = baseline.anomaly_score(features[-1])
    changed = replace(features[-1], amplitude_peak=features[-1].amplitude_peak * 10)
    changed_score = baseline.anomaly_score(changed)

    assert baseline.sample_count == 5
    assert baseline.sensor_id == "sdr-01"
    assert changed_score > normal_score
    assert baseline.to_dict()["feature_schema_version"] == features[0].feature_schema_version


def test_rolling_baseline_respects_window() -> None:
    source = SyntheticIQSource(SDRConfig(sample_rate=1_000_000.0, center_frequency=100_000_000.0), noise_amplitude=0.01)
    rolling = RollingRFBaseline(max_samples=3)
    last = None
    for _ in range(5):
        last = extract_rf_features(source.read_samples(1024), sample_rate_hz=1_000_000.0, center_frequency_hz=100_000_000.0)
        rolling.update(last)
    assert rolling.sample_count == 3
    assert last is not None
    assert rolling.anomaly_score(last) >= 0.0
