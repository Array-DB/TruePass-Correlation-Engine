from __future__ import annotations

import numpy as np

from truepass.spectrum.fft import compute_fft
from truepass.spectrum.psd import compute_psd, compute_spectrogram


def _tone(sample_rate: float, tone_hz: float, count: int = 4096) -> np.ndarray:
    t = np.arange(count) / sample_rate
    return np.exp(2j * np.pi * tone_hz * t)


def test_fft_and_psd_locate_known_tone() -> None:
    sample_rate = 1_000_000.0
    center = 100_000_000.0
    tone_hz = 125_000.0
    samples = _tone(sample_rate, tone_hz)

    fft = compute_fft(samples, sample_rate_hz=sample_rate, center_frequency_hz=center)
    psd = compute_psd(samples, sample_rate_hz=sample_rate, center_frequency_hz=center)

    fft_peak = fft.frequencies_hz[int(np.argmax(fft.magnitude))]
    psd_peak = psd.frequencies_hz[int(np.argmax(psd.power_w_per_hz))]
    bin_width = sample_rate / samples.size
    assert abs(fft_peak - (center + tone_hz)) <= bin_width
    assert abs(psd_peak - (center + tone_hz)) <= bin_width
    assert np.all(np.isfinite(psd.power_db_per_hz))


def test_spectrogram_has_consistent_axes() -> None:
    samples = _tone(1_000_000.0, 50_000.0, 2048)
    frame = compute_spectrogram(samples, sample_rate_hz=1_000_000.0, nperseg=256)
    assert frame.power_w_per_hz.shape == (frame.frequencies_hz.size, frame.times_s.size)
    assert frame.times_s.size > 1
