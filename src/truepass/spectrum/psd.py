"""Power spectral density and spectrogram calculations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.signal import get_window, spectrogram

from .fft import WindowName, _as_complex_array


@dataclass(frozen=True, slots=True)
class PSDFrame:
    frequencies_hz: np.ndarray
    power_w_per_hz: np.ndarray
    power_db_per_hz: np.ndarray
    sample_rate_hz: float
    center_frequency_hz: float


@dataclass(frozen=True, slots=True)
class SpectrogramFrame:
    frequencies_hz: np.ndarray
    times_s: np.ndarray
    power_w_per_hz: np.ndarray
    power_db_per_hz: np.ndarray
    sample_rate_hz: float
    center_frequency_hz: float


def compute_psd(
    samples: Sequence[complex] | np.ndarray,
    *,
    sample_rate_hz: float,
    center_frequency_hz: float = 0.0,
    window: WindowName = "hann",
) -> PSDFrame:
    """Estimate periodogram-style PSD for a single complex I/Q frame."""

    if sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be positive")
    values = _as_complex_array(samples)
    weights = get_window(window, values.size, fftbins=True)
    weighted = values * weights
    spectrum = np.fft.fftshift(np.fft.fft(weighted))
    scale = sample_rate_hz * float(np.sum(weights**2))
    power = (np.abs(spectrum) ** 2) / max(scale, np.finfo(float).tiny)
    frequencies = (
        np.fft.fftshift(np.fft.fftfreq(values.size, d=1.0 / sample_rate_hz))
        + center_frequency_hz
    )
    db = 10.0 * np.log10(np.maximum(power, np.finfo(float).tiny))
    return PSDFrame(frequencies, power, db, float(sample_rate_hz), float(center_frequency_hz))


def compute_spectrogram(
    samples: Sequence[complex] | np.ndarray,
    *,
    sample_rate_hz: float,
    center_frequency_hz: float = 0.0,
    window: WindowName = "hann",
    nperseg: int = 256,
    overlap_fraction: float = 0.5,
) -> SpectrogramFrame:
    """Compute a two-dimensional PSD spectrogram for complex samples."""

    if sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be positive")
    values = _as_complex_array(samples)
    if nperseg < 8:
        raise ValueError("nperseg must be at least 8")
    nperseg = min(nperseg, values.size)
    if not 0 <= overlap_fraction < 1:
        raise ValueError("overlap_fraction must be in [0, 1)")
    noverlap = int(nperseg * overlap_fraction)

    frequencies, times, power = spectrogram(
        values,
        fs=sample_rate_hz,
        window=window,
        nperseg=nperseg,
        noverlap=noverlap,
        detrend=False,
        return_onesided=False,
        scaling="density",
        mode="psd",
    )
    order = np.argsort(frequencies)
    frequencies = frequencies[order] + center_frequency_hz
    power = power[order, :]
    db = 10.0 * np.log10(np.maximum(power, np.finfo(float).tiny))
    return SpectrogramFrame(
        frequencies,
        times,
        power,
        db,
        float(sample_rate_hz),
        float(center_frequency_hz),
    )
