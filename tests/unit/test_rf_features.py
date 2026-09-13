from __future__ import annotations

import numpy as np

from truepass.spectrum.features import FEATURE_SCHEMA_VERSION, extract_rf_features


def test_rf_features_are_finite_and_peak_matches_tone() -> None:
    sample_rate = 1_000_000.0
    center = 2_437_000_000.0
    tone = 100_000.0
    count = 4096
    t = np.arange(count) / sample_rate
    samples = np.exp(2j * np.pi * tone * t)

    features = extract_rf_features(samples, sample_rate_hz=sample_rate, center_frequency_hz=center)

    assert features.feature_schema_version == FEATURE_SCHEMA_VERSION
    assert abs(features.peak_frequency_hz - (center + tone)) < sample_rate / count * 2
    assert 0.0 <= features.spectral_entropy <= 1.0
    assert 0.0 <= features.spectral_flatness <= 1.0
    assert features.sample_count == count
    assert np.all(np.isfinite(features.numeric_vector()))
