"""Versioned measurable RF feature extraction."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence

import numpy as np

from .psd import compute_psd

FEATURE_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True, slots=True)
class RFFeatureVector:
    """Measurable RF descriptors; no semantic or human-intent inference."""

    center_frequency_hz: float
    peak_frequency_hz: float
    occupied_bandwidth_hz: float
    peak_power_db_per_hz: float
    average_power_db_per_hz: float
    noise_floor_db_per_hz: float
    spectral_entropy: float
    spectral_centroid_hz: float
    spectral_flatness: float
    frequency_drift_hz: float
    amplitude_mean: float
    amplitude_std: float
    amplitude_peak: float
    duty_cycle: float
    burst_duration_s: float
    sample_count: int
    feature_schema_version: str = FEATURE_SCHEMA_VERSION

    def numeric_vector(self) -> np.ndarray:
        """Return stable numerical order for ML/baseline components."""
        return np.asarray(
            [
                self.occupied_bandwidth_hz,
                self.peak_power_db_per_hz,
                self.average_power_db_per_hz,
                self.noise_floor_db_per_hz,
                self.spectral_entropy,
                self.spectral_centroid_hz - self.center_frequency_hz,
                self.spectral_flatness,
                self.frequency_drift_hz,
                self.amplitude_mean,
                self.amplitude_std,
                self.amplitude_peak,
                self.duty_cycle,
                self.burst_duration_s,
            ],
            dtype=np.float64,
        )

    def as_dict(self) -> dict[str, float | int | str]:
        return asdict(self)


def _occupied_bandwidth(frequencies: np.ndarray, power: np.ndarray, fraction: float = 0.99) -> float:
    total = float(np.sum(power))
    if total <= 0 or frequencies.size < 2:
        return 0.0
    cumulative = np.cumsum(power) / total
    low_idx = int(np.searchsorted(cumulative, (1 - fraction) / 2))
    high_idx = int(np.searchsorted(cumulative, 1 - (1 - fraction) / 2))
    high_idx = min(high_idx, frequencies.size - 1)
    return float(abs(frequencies[high_idx] - frequencies[low_idx]))


def extract_rf_features(
    samples: Sequence[complex] | np.ndarray,
    *,
    sample_rate_hz: float,
    center_frequency_hz: float,
    duty_threshold_sigma: float = 2.0,
) -> RFFeatureVector:
    """Extract RF features from one I/Q frame using deterministic statistics."""

    values = np.asarray(samples, dtype=np.complex128)
    if values.ndim != 1 or values.size < 8:
        raise ValueError("at least 8 one-dimensional I/Q samples are required")
    psd = compute_psd(
        values,
        sample_rate_hz=sample_rate_hz,
        center_frequency_hz=center_frequency_hz,
    )
    power = psd.power_w_per_hz
    power_sum = float(np.sum(power))
    probabilities = power / max(power_sum, np.finfo(float).tiny)
    nz = probabilities > 0
    entropy = -float(np.sum(probabilities[nz] * np.log2(probabilities[nz])))
    entropy /= max(float(np.log2(probabilities.size)), np.finfo(float).tiny)

    peak_idx = int(np.argmax(power))
    centroid = float(np.sum(psd.frequencies_hz * probabilities))
    arithmetic_mean = float(np.mean(power))
    geometric_mean = float(np.exp(np.mean(np.log(np.maximum(power, np.finfo(float).tiny)))))
    flatness = geometric_mean / max(arithmetic_mean, np.finfo(float).tiny)

    amplitude = np.abs(values)
    threshold = float(np.median(amplitude) + duty_threshold_sigma * np.std(amplitude))
    active = amplitude > threshold
    duty_cycle = float(np.mean(active))
    burst_duration_s = float(np.count_nonzero(active) / sample_rate_hz)

    # Estimate drift from peak frequency in the first versus second half.
    half = values.size // 2
    first = compute_psd(values[:half], sample_rate_hz=sample_rate_hz, center_frequency_hz=center_frequency_hz)
    second = compute_psd(values[half:], sample_rate_hz=sample_rate_hz, center_frequency_hz=center_frequency_hz)
    first_peak = float(first.frequencies_hz[int(np.argmax(first.power_w_per_hz))])
    second_peak = float(second.frequencies_hz[int(np.argmax(second.power_w_per_hz))])

    return RFFeatureVector(
        center_frequency_hz=float(center_frequency_hz),
        peak_frequency_hz=float(psd.frequencies_hz[peak_idx]),
        occupied_bandwidth_hz=_occupied_bandwidth(psd.frequencies_hz, power),
        peak_power_db_per_hz=float(psd.power_db_per_hz[peak_idx]),
        average_power_db_per_hz=float(10 * np.log10(max(arithmetic_mean, np.finfo(float).tiny))),
        noise_floor_db_per_hz=float(np.median(psd.power_db_per_hz)),
        spectral_entropy=entropy,
        spectral_centroid_hz=centroid,
        spectral_flatness=flatness,
        frequency_drift_hz=second_peak - first_peak,
        amplitude_mean=float(np.mean(amplitude)),
        amplitude_std=float(np.std(amplitude)),
        amplitude_peak=float(np.max(amplitude)),
        duty_cycle=duty_cycle,
        burst_duration_s=burst_duration_s,
        sample_count=int(values.size),
    )
