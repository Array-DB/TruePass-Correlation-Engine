from __future__ import annotations

import numpy as np

from truepass.detection.anomaly import IsolationForestDetector, StatisticalDistanceDetector
from truepass.detection.clustering import AdaptiveKMeansClusterer, DBSCANClusterer


def test_statistical_distance_marks_far_point() -> None:
    rng = np.random.default_rng(7)
    training = rng.normal(0, 0.1, size=(100, 4))
    detector = StatisticalDistanceDetector(threshold=3.0).fit(training)
    result = detector.detect([5.0, 5.0, 5.0, 5.0])
    assert result.is_anomaly
    assert "z-distance" in result.reason


def test_isolation_forest_returns_explanation() -> None:
    rng = np.random.default_rng(2)
    training = rng.normal(0, 0.2, size=(100, 3))
    result = IsolationForestDetector(contamination=0.05).fit(training).detect([8.0, 8.0, 8.0])
    assert result.model_id == "isolation-forest-v1"
    assert "decision_function" in result.reason


def test_clusterers_find_structure_without_threat_labels() -> None:
    rng = np.random.default_rng(3)
    first = rng.normal(-3, 0.1, size=(30, 2))
    second = rng.normal(3, 0.1, size=(30, 2))
    matrix = np.vstack([first, second])

    adaptive = AdaptiveKMeansClusterer(min_clusters=1, max_clusters=4).fit_predict(matrix)
    dbscan = DBSCANClusterer(eps=0.3, min_samples=3).fit_predict(matrix)

    assert adaptive.cluster_count >= 2
    assert dbscan.cluster_count >= 2
    assert "not threat labels" in adaptive.reason
    assert "require correlation" in dbscan.reason
