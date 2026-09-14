"""Correlation-to-incident orchestration with explicit explanations."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from uuid import uuid4

from truepass.correlation.engine import TemporalCorrelationEngine
from truepass.incidents.scoring import IncidentScorer
from truepass.models.events import Event


@dataclass(frozen=True, slots=True)
class IncidentResult:
    incident_id: str
    anchor_event_id: str
    score: float
    severity: str
    confidence: float
    evidence_ids: tuple[str, ...]
    explanations: tuple[str, ...]
    causation_established: bool = False

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


class IncidentPipeline:
    """Create an incident candidate from an anchor and nearby observations."""

    def __init__(self, *, window_ms: float = 500.0) -> None:
        self.correlator = TemporalCorrelationEngine(window_ms=window_ms)
        self.scorer = IncidentScorer()

    def evaluate(self, anchor: Event, candidates: list[Event] | tuple[Event, ...]) -> IncidentResult:
        correlation = self.correlator.correlate(anchor, candidates)
        assessment = self.scorer.score(anchor, correlation)
        return IncidentResult(
            incident_id=str(uuid4()),
            anchor_event_id=str(anchor.event_id),
            score=assessment.score,
            severity=assessment.severity.value,
            confidence=assessment.confidence,
            evidence_ids=assessment.evidence_ids,
            explanations=assessment.candidate_explanations,
        )
