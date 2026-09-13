"""Versioned RF baseline learning and comparison."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Iterable

import numpy as np

from truepass.spectrum.features import FEATURE_SCHEMA_VERSION, RFFeatureVector


@dataclass(frozen=True, slots=True)
class RFBaselineModel:
    model_id: str
    sensor_id: str
    frequency_band_hz: tuple[float, float]
    hour_bucket: int | None
    created_at: str
    training_start: str
    training_end: str
    feature_schema_version: str
    sample_count: int
    mean: tuple[float, ...]
    std: tuple[float, ...]

    def z_scores(self, feature: RFFeatureVector) -> np.ndarray:
        values = feature.numeric_vector()
        mean = np.asarray(self.mean)
        std = np.asarray(self.std)
        if values.shape != mean.shape:
            raise ValueError("feature vector does not match baseline schema")
        return np.abs((values - mean) / np.maximum(std, 1e-9))

    def anomaly_score(self, feature: RFFeatureVector) -> float:
        """Return an interpretable mean absolute z-distance (not a probability)."""
        return float(np.mean(self.z_scores(feature)))

    def to_dict(self) -> dict[str, object]:
        return {
            "model_id": self.model_id,
            "sensor_id": self.sensor_id,
            "frequency_band_hz": list(self.frequency_band_hz),
            "hour_bucket": self.hour_bucket,
            "created_at": self.created_at,
            "training_start": self.training_start,
            "training_end": self.training_end,
            "feature_schema_version": self.feature_schema_version,
            "sample_count": self.sample_count,
            "mean": list(self.mean),
            "std": list(self.std),
        }


class RFBaselineTrainer:
    """Fit sensor/band/time-aware statistical RF baselines."""

    def fit(
        self,
        features: Iterable[RFFeatureVector],
        *,
        sensor_id: str,
        frequency_band_hz: tuple[float, float],
        training_start: datetime,
        training_end: datetime,
        hour_bucket: int | None = None,
        model_id: str | None = None,
    ) -> RFBaselineModel:
        rows = [feature.numeric_vector() for feature in features]
        if len(rows) < 2:
            raise ValueError("at least two feature vectors are required to build a baseline")
        matrix = np.vstack(rows)
        if hour_bucket is not None and not 0 <= hour_bucket <= 23:
            raise ValueError("hour_bucket must be 0..23")
        low, high = frequency_band_hz
        if low >= high:
            raise ValueError("frequency_band_hz must be an increasing range")
        now = datetime.now(UTC)
        baseline_id = model_id or f"rf-{sensor_id}-{int(now.timestamp())}"
        return RFBaselineModel(
            model_id=baseline_id,
            sensor_id=sensor_id,
            frequency_band_hz=(float(low), float(high)),
            hour_bucket=hour_bucket,
            created_at=now.isoformat(),
            training_start=training_start.astimezone(UTC).isoformat(),
            training_end=training_end.astimezone(UTC).isoformat(),
            feature_schema_version=FEATURE_SCHEMA_VERSION,
            sample_count=matrix.shape[0],
            mean=tuple(float(v) for v in np.mean(matrix, axis=0)),
            std=tuple(float(v) for v in np.std(matrix, axis=0, ddof=0)),
        )

class RollingRFBaseline:
    """Fixed-size rolling statistics for online baseline monitoring."""

    def __init__(self, *, max_samples: int = 256) -> None:
        from collections import deque

        if max_samples < 2:
            raise ValueError("max_samples must be at least 2")
        self.max_samples = max_samples
        self._rows: deque[np.ndarray] = deque(maxlen=max_samples)

    @property
    def sample_count(self) -> int:
        return len(self._rows)

    def update(self, feature: RFFeatureVector) -> None:
        self._rows.append(feature.numeric_vector())

    def statistics(self) -> tuple[np.ndarray, np.ndarray]:
        if len(self._rows) < 2:
            raise RuntimeError("at least two observations are required")
        matrix = np.vstack(tuple(self._rows))
        return np.mean(matrix, axis=0), np.std(matrix, axis=0, ddof=0)

    def anomaly_score(self, feature: RFFeatureVector) -> float:
        mean, std = self.statistics()
        z = np.abs((feature.numeric_vector() - mean) / np.maximum(std, 1e-9))
        return float(np.mean(z))
