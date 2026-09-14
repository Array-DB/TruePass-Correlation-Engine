"""Reusable receive-side DSP pipeline for live and replay SDR frames."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from typing import Sequence

import numpy as np

from truepass.spectrum.features import RFFeatureVector, extract_rf_features
from truepass.spectrum.fft import WindowName, compute_fft
from truepass.spectrum.psd import compute_psd, compute_spectrogram


@dataclass(frozen=True, slots=True)
class DSPFrame:
    timestamp_ns: int
    sample_count: int
    sample_rate_hz: float
    center_frequency_hz: float
    frequencies_hz: tuple[float, ...]
    fft_magnitude_db: tuple[float, ...]
    psd_db_per_hz: tuple[float, ...]
    waterfall_frequencies_hz: tuple[float, ...]
    waterfall_times_s: tuple[float, ...]
    waterfall_db_per_hz: tuple[tuple[float, ...], ...]
    features: RFFeatureVector

    def as_dict(self) -> dict[str, object]:
        return {
            "timestamp_ns": self.timestamp_ns,
            "sample_count": self.sample_count,
            "sample_rate_hz": self.sample_rate_hz,
            "center_frequency_hz": self.center_frequency_hz,
            "frequencies_hz": list(self.frequencies_hz),
            "fft_magnitude_db": list(self.fft_magnitude_db),
            "psd_db_per_hz": list(self.psd_db_per_hz),
            "waterfall_frequencies_hz": list(self.waterfall_frequencies_hz),
            "waterfall_times_s": list(self.waterfall_times_s),
            "waterfall_db_per_hz": [list(row) for row in self.waterfall_db_per_hz],
            "features": asdict(self.features),
        }


class SpectrumDSPPipeline:
    """Convert one I/Q frame into bounded, browser-ready spectrum products."""

    def __init__(
        self,
        *,
        sample_rate_hz: float,
        center_frequency_hz: float,
        window: WindowName = "hann",
        max_spectrum_bins: int = 1024,
        max_waterfall_frequency_bins: int = 256,
        max_waterfall_time_bins: int = 64,
    ) -> None:
        if sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz must be positive")
        if max_spectrum_bins < 16:
            raise ValueError("max_spectrum_bins must be at least 16")
        if max_waterfall_frequency_bins < 16 or max_waterfall_time_bins < 2:
            raise ValueError("waterfall limits are too small")
        self.sample_rate_hz = float(sample_rate_hz)
        self.center_frequency_hz = float(center_frequency_hz)
        self.window = window
        self.max_spectrum_bins = max_spectrum_bins
        self.max_waterfall_frequency_bins = max_waterfall_frequency_bins
        self.max_waterfall_time_bins = max_waterfall_time_bins

    def process(self, samples: Sequence[complex] | np.ndarray) -> DSPFrame:
        values = np.asarray(samples, dtype=np.complex128)
        if values.ndim != 1 or values.size < 8:
            raise ValueError("at least 8 one-dimensional I/Q samples are required")

        fft = compute_fft(
            values,
            sample_rate_hz=self.sample_rate_hz,
            center_frequency_hz=self.center_frequency_hz,
            window=self.window,
        )
        psd = compute_psd(
            values,
            sample_rate_hz=self.sample_rate_hz,
            center_frequency_hz=self.center_frequency_hz,
            window=self.window,
        )
        spectrogram = compute_spectrogram(
            values,
            sample_rate_hz=self.sample_rate_hz,
            center_frequency_hz=self.center_frequency_hz,
            window=self.window,
            nperseg=min(256, values.size),
        )
        features = extract_rf_features(
            values,
            sample_rate_hz=self.sample_rate_hz,
            center_frequency_hz=self.center_frequency_hz,
        )

        fft_db = 20.0 * np.log10(np.maximum(fft.magnitude, np.finfo(float).tiny))
        frequencies, fft_db_values, psd_values = _downsample_triplet(
            fft.frequencies_hz,
            fft_db,
            psd.power_db_per_hz,
            self.max_spectrum_bins,
        )
        wf_frequencies, wf_power = _downsample_rows(
            spectrogram.frequencies_hz,
            spectrogram.power_db_per_hz,
            self.max_waterfall_frequency_bins,
        )
        wf_times, wf_power = _downsample_columns(
            spectrogram.times_s,
            wf_power,
            self.max_waterfall_time_bins,
        )

        return DSPFrame(
            timestamp_ns=time.time_ns(),
            sample_count=int(values.size),
            sample_rate_hz=self.sample_rate_hz,
            center_frequency_hz=self.center_frequency_hz,
            frequencies_hz=tuple(float(value) for value in frequencies),
            fft_magnitude_db=tuple(float(value) for value in fft_db_values),
            psd_db_per_hz=tuple(float(value) for value in psd_values),
            waterfall_frequencies_hz=tuple(float(value) for value in wf_frequencies),
            waterfall_times_s=tuple(float(value) for value in wf_times),
            waterfall_db_per_hz=tuple(
                tuple(float(value) for value in row) for row in wf_power
            ),
            features=features,
        )


def _indices(length: int, maximum: int) -> np.ndarray:
    if length <= maximum:
        return np.arange(length)
    return np.linspace(0, length - 1, maximum, dtype=int)


def _downsample_triplet(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    maximum: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    index = _indices(x.size, maximum)
    return x[index], y[index], z[index]


def _downsample_rows(
    frequencies: np.ndarray,
    values: np.ndarray,
    maximum: int,
) -> tuple[np.ndarray, np.ndarray]:
    index = _indices(frequencies.size, maximum)
    return frequencies[index], values[index, :]


def _downsample_columns(
    times: np.ndarray,
    values: np.ndarray,
    maximum: int,
) -> tuple[np.ndarray, np.ndarray]:
    index = _indices(times.size, maximum)
    return times[index], values[:, index]
