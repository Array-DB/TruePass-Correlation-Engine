"""FFT utilities for complex I/Q samples."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence

import numpy as np
from scipy.signal import get_window

WindowName = Literal["hann", "blackman", "boxcar"]


@dataclass(frozen=True, slots=True)
class SpectrumFrame:
    """Frequency-domain representation of one I/Q frame."""

    frequencies_hz: np.ndarray
    spectrum: np.ndarray
    sample_rate_hz: float
    center_frequency_hz: float
    window: WindowName

    @property
    def magnitude(self) -> np.ndarray:
        return np.abs(self.spectrum)


def _as_complex_array(samples: Sequence[complex] | np.ndarray) -> np.ndarray:
    values = np.asarray(samples, dtype=np.complex128)
    if values.ndim != 1:
        raise ValueError("I/Q samples must be a one-dimensional sequence")
    if values.size < 2:
        raise ValueError("at least two I/Q samples are required")
    if not np.all(np.isfinite(values.real)) or not np.all(np.isfinite(values.imag)):
        raise ValueError("I/Q samples must be finite")
    return values


def compute_fft(
    samples: Sequence[complex] | np.ndarray,
    *,
    sample_rate_hz: float,
    center_frequency_hz: float = 0.0,
    window: WindowName = "hann",
) -> SpectrumFrame:
    """Compute a centered FFT using a supported deterministic window."""

    if sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be positive")
    values = _as_complex_array(samples)
    if window not in {"hann", "blackman", "boxcar"}:
        raise ValueError(f"unsupported window: {window}")

    weights = get_window(window, values.size, fftbins=True)
    spectrum = np.fft.fftshift(np.fft.fft(values * weights))
    frequencies = (
        np.fft.fftshift(np.fft.fftfreq(values.size, d=1.0 / sample_rate_hz))
        + center_frequency_hz
    )
    return SpectrumFrame(
        frequencies_hz=frequencies,
        spectrum=spectrum,
        sample_rate_hz=float(sample_rate_hz),
        center_frequency_hz=float(center_frequency_hz),
        window=window,
    )
