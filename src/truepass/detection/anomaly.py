"""Common anomaly-detector interface and initial detector implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from sklearn.ensemble import IsolationForest


@dataclass(frozen=True, slots=True)
class DetectionResult:
    score: float
    model_id: str
    reason: str
    confidence: float | None
    is_anomaly: bool


class StatisticalDistanceDetector:
    """Z-distance detector using a training population."""

    def __init__(self, *, threshold: float = 3.0, model_id: str = "statistical-distance-v1") -> None:
        self.threshold = threshold
        self.model_id = model_id
        self._mean: np.ndarray | None = None
        self._std: np.ndarray | None = None

    def fit(self, samples: Sequence[Sequence[float]] | np.ndarray) -> "StatisticalDistanceDetector":
        matrix = np.asarray(samples, dtype=np.float64)
        if matrix.ndim != 2 or matrix.shape[0] < 2:
            raise ValueError("training samples must be a 2D matrix with at least two rows")
        self._mean = np.mean(matrix, axis=0)
        self._std = np.maximum(np.std(matrix, axis=0), 1e-9)
        return self

    def detect(self, sample: Sequence[float] | np.ndarray) -> DetectionResult:
        if self._mean is None or self._std is None:
            raise RuntimeError("detector must be fit before detect")
        vector = np.asarray(sample, dtype=np.float64)
        z = np.abs((vector - self._mean) / self._std)
        score = float(np.max(z))
        return DetectionResult(
            score=score,
            model_id=self.model_id,
            reason=f"maximum absolute z-distance={score:.3f}; threshold={self.threshold:.3f}",
            confidence=None,
            is_anomaly=score >= self.threshold,
        )


class IsolationForestDetector:
    """Isolation Forest wrapper that returns transparent model metadata."""

    def __init__(
        self,
        *,
        contamination: float | str = "auto",
        random_state: int = 0,
        model_id: str = "isolation-forest-v1",
    ) -> None:
        self.model_id = model_id
        self._model = IsolationForest(contamination=contamination, random_state=random_state)
        self._fitted = False

    def fit(self, samples: Sequence[Sequence[float]] | np.ndarray) -> "IsolationForestDetector":
        matrix = np.asarray(samples, dtype=np.float64)
        if matrix.ndim != 2 or matrix.shape[0] < 2:
            raise ValueError("training samples must be a 2D matrix with at least two rows")
        self._model.fit(matrix)
        self._fitted = True
        return self

    def detect(self, sample: Sequence[float] | np.ndarray) -> DetectionResult:
        if not self._fitted:
            raise RuntimeError("detector must be fit before detect")
        vector = np.asarray(sample, dtype=np.float64).reshape(1, -1)
        decision = float(self._model.decision_function(vector)[0])
        prediction = int(self._model.predict(vector)[0])
        anomaly_score = -decision
        return DetectionResult(
            score=anomaly_score,
            model_id=self.model_id,
            reason=f"IsolationForest decision_function={decision:.6f}",
            confidence=None,
            is_anomaly=prediction == -1,
        )
