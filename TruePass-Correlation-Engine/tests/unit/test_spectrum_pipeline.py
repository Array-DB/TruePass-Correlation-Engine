from __future__ import annotations

import numpy as np

from truepass.spectrum.pipeline import SpectrumDSPPipeline


def test_pipeline_produces_bounded_serializable_frame() -> None:
    sample_rate = 2_000_000.0
    center = 915_000_000.0
    count = 4096
    t = np.arange(count) / sample_rate
    samples = np.exp(2j * np.pi * 125_000.0 * t)
    pipeline = SpectrumDSPPipeline(
        sample_rate_hz=sample_rate,
        center_frequency_hz=center,
        max_spectrum_bins=256,
        max_waterfall_frequency_bins=64,
        max_waterfall_time_bins=16,
    )
    frame = pipeline.process(samples)
    payload = frame.as_dict()
    assert frame.sample_count == count
    assert len(frame.frequencies_hz) <= 256
    assert len(frame.waterfall_frequencies_hz) <= 64
    assert len(frame.waterfall_times_s) <= 16
    assert payload["features"]["sample_count"] == count
