import numpy as np
from truepass.detection.rf_intelligence import RFIntelligenceEngine
from truepass.spectrum.features import extract_rf_features


def feature(amplitude: float, tone: float = 50_000.0):
    rate = 1_000_000.0
    count = 1024
    t = np.arange(count) / rate
    samples = amplitude * np.exp(2j * np.pi * tone * t)
    return extract_rf_features(samples, sample_rate_hz=rate, center_frequency_hz=100_000_000.0)


def test_rf_intelligence_warms_up_then_assesses() -> None:
    engine = RFIntelligenceEngine(warmup_samples=4, history_size=16)
    for amplitude in (1.0, 1.01, .99, 1.02):
        result = engine.observe(feature(amplitude))
        assert not result.is_anomaly
    result = engine.observe(feature(8.0, 180_000.0), learn=False)
    assert result.model_ids
    assert result.sample_count == 4
    assert result.reasons
