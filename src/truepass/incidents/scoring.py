"""Transparent incident scoring with evidence-backed explanations."""
from __future__ import annotations
from dataclasses import dataclass
from truepass.correlation.engine import CorrelationResult
from truepass.models.events import Event, Severity

@dataclass(frozen=True, slots=True)
class IncidentAssessment:
    score: float
    severity: Severity
    confidence: float
    evidence_ids: tuple[str, ...]
    candidate_explanations: tuple[str, ...]

class IncidentScorer:
    def score(self, anchor: Event, correlation: CorrelationResult) -> IncidentAssessment:
        novelty = float(anchor.features.get("anomaly_score", anchor.metadata.get("anomaly_score", 0.0)) or 0.0)
        novelty = max(0.0, min(1.0, novelty))
        asset = float(anchor.metadata.get("asset_sensitivity", 0.5) or 0.5)
        asset = max(0.0, min(1.0, asset))
        score = min(1.0, 0.55*correlation.score + 0.30*novelty + 0.15*asset)
        severity = Severity.INFO if score < .2 else Severity.LOW if score < .4 else Severity.MEDIUM if score < .65 else Severity.HIGH if score < .85 else Severity.CRITICAL
        explanations = tuple(r.detail for r in correlation.reasons[:8]) or ("insufficient correlated evidence",)
        return IncidentAssessment(score,severity,min(1.0,correlation.confidence),correlation.evidence_ids,explanations)
