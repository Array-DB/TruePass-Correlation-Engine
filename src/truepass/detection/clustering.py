"""Unsupervised RF clustering without treating unknown clusters as attackers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True, slots=True)
class ClusterResult:
    labels: tuple[int, ...]
    cluster_count: int
    model_id: str
    reason: str


class DBSCANClusterer:
    def __init__(self, *, eps: float = 0.8, min_samples: int = 5, model_id: str = "dbscan-v1") -> None:
        self.eps = eps
        self.min_samples = min_samples
        self.model_id = model_id

    def fit_predict(self, samples: Sequence[Sequence[float]] | np.ndarray) -> ClusterResult:
        matrix = np.asarray(samples, dtype=np.float64)
        if matrix.ndim != 2 or matrix.shape[0] < 2:
            raise ValueError("samples must be a 2D matrix with at least two rows")
        normalized = StandardScaler().fit_transform(matrix)
        labels = DBSCAN(eps=self.eps, min_samples=self.min_samples).fit_predict(normalized)
        unique = {int(label) for label in labels if int(label) >= 0}
        return ClusterResult(
            labels=tuple(int(label) for label in labels),
            cluster_count=len(unique),
            model_id=self.model_id,
            reason="cluster labels describe similarity only; noise/unknown observations require correlation",
        )


class AdaptiveKMeansClusterer:
    """X-means-compatible adaptive K selection using KMeans plus a BIC-style criterion."""

    def __init__(self, *, min_clusters: int = 1, max_clusters: int = 8, random_state: int = 0) -> None:
        if min_clusters < 1 or max_clusters < min_clusters:
            raise ValueError("invalid cluster bounds")
        self.min_clusters = min_clusters
        self.max_clusters = max_clusters
        self.random_state = random_state
        self.model_id = "adaptive-kmeans-bic-v1"

    @staticmethod
    def _bic(matrix: np.ndarray, labels: np.ndarray, centers: np.ndarray) -> float:
        n, dimensions = matrix.shape
        k = centers.shape[0]
        residual = float(np.sum((matrix - centers[labels]) ** 2))
        variance = max(residual / max(n - k, 1), 1e-12)
        log_likelihood = -0.5 * n * dimensions * np.log(2 * np.pi * variance) - residual / (2 * variance)
        parameters = k * (dimensions + 1)
        return float(-2 * log_likelihood + parameters * np.log(n))

    def fit_predict(self, samples: Sequence[Sequence[float]] | np.ndarray) -> ClusterResult:
        matrix = np.asarray(samples, dtype=np.float64)
        if matrix.ndim != 2 or matrix.shape[0] < 2:
            raise ValueError("samples must be a 2D matrix with at least two rows")
        normalized = StandardScaler().fit_transform(matrix)
        upper = min(self.max_clusters, normalized.shape[0])
        best: tuple[float, KMeans, np.ndarray] | None = None
        for k in range(self.min_clusters, upper + 1):
            model = KMeans(n_clusters=k, random_state=self.random_state, n_init="auto")
            labels = model.fit_predict(normalized)
            score = self._bic(normalized, labels, model.cluster_centers_)
            if best is None or score < best[0]:
                best = (score, model, labels)
        assert best is not None
        _, model, labels = best
        return ClusterResult(
            labels=tuple(int(label) for label in labels),
            cluster_count=int(model.n_clusters),
            model_id=self.model_id,
            reason="adaptive cluster count selected by BIC-style criterion; clusters are observations, not threat labels",
        )
