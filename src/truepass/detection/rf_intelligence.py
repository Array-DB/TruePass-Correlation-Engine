"""Integrated RF baseline and anomaly assessment service."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque

import numpy as np

from truepass.detection.anomaly import DetectionResult, IsolationForestDetector, StatisticalDistanceDetector
from truepass.spectrum.features import RFFeatureVector


@dataclass(frozen=True, slots=True)
class RFAssessment:
    is_anomaly: bool
    score: float
    reasons: tuple[str, ...]
    model_ids: tuple[str, ...]
    sample_count: int


class RFIntelligenceEngine:
    """Online RF assessment that learns expected numeric feature behavior.

    Unknown/anomalous observations remain observations; this class never labels an
    attacker or asserts causation.
    """

    def __init__(self, *, warmup_samples: int = 16, history_size: int = 256, z_threshold: float = 4.0) -> None:
        if warmup_samples < 4:
            raise ValueError("warmup_samples must be at least 4")
        if history_size < warmup_samples:
            raise ValueError("history_size must be >= warmup_samples")
        self.warmup_samples = warmup_samples
        self._history: Deque[np.ndarray] = deque(maxlen=history_size)
        self._stat = StatisticalDistanceDetector(threshold=z_threshold)
        self._forest = IsolationForestDetector(random_state=0)
        self._fitted = False

    @property
    def sample_count(self) -> int:
        return len(self._history)

    def observe(self, feature: RFFeatureVector, *, learn: bool = True) -> RFAssessment:
        vector = feature.numeric_vector()
        if not self._fitted and len(self._history) >= self.warmup_samples:
            matrix = np.vstack(tuple(self._history))
            self._stat.fit(matrix)
            self._forest.fit(matrix)
            self._fitted = True

        results: list[DetectionResult] = []
        if self._fitted:
            results = [self._stat.detect(vector), self._forest.detect(vector)]

        if learn:
            self._history.append(vector)
            # Refit periodically so the bounded baseline can adapt without every-frame cost.
            if self._fitted and len(self._history) % self.warmup_samples == 0:
                matrix = np.vstack(tuple(self._history))
                self._stat.fit(matrix)
                self._forest.fit(matrix)

        if not results:
            return RFAssessment(False, 0.0, ("baseline warm-up in progress",), (), len(self._history))

        anomaly_votes = sum(1 for result in results if result.is_anomaly)
        score = max(float(result.score) for result in results)
        return RFAssessment(
            is_anomaly=anomaly_votes >= 1,
            score=score,
            reasons=tuple(result.reason for result in results),
            model_ids=tuple(result.model_id for result in results),
            sample_count=len(self._history),
        )
