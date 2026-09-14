"""Explainable temporal correlation across TruePass event domains."""
from __future__ import annotations
from dataclasses import dataclass
from math import exp, prod
from typing import Iterable
from truepass.models.events import Event

@dataclass(frozen=True, slots=True)
class CorrelationReason:
    code: str
    weight: float
    contribution: float
    detail: str

@dataclass(frozen=True, slots=True)
class CorrelationResult:
    score: float
    confidence: float
    reasons: tuple[CorrelationReason, ...]
    evidence_ids: tuple[str, ...]

class TemporalCorrelationEngine:
    """Scores relationships without claiming causation."""
    def __init__(self, *, window_ms: float = 500.0) -> None:
        if window_ms <= 0: raise ValueError("window_ms must be positive")
        self.window_ns = int(window_ms * 1_000_000)

    def correlate(self, anchor: Event, candidates: Iterable[Event]) -> CorrelationResult:
        candidates = tuple(candidates)
        reasons: list[CorrelationReason] = []
        evidence = [str(anchor.event_id)]
        for event in candidates:
            if event.event_id == anchor.event_id: continue
            delta = abs(event.timestamp_ns - anchor.timestamp_ns)
            if delta > self.window_ns: continue
            evidence.append(str(event.event_id))
            proximity = exp(-3.0 * delta / self.window_ns)
            contribution = 0.35 * proximity
            reasons.append(CorrelationReason("time_proximity",0.35,contribution,f"{delta/1_000_000:.3f} ms apart"))
            if event.host == anchor.host:
                reasons.append(CorrelationReason("same_host",0.20,0.20,f"shared host {anchor.host}"))
            if event.sensor_id == anchor.sensor_id:
                reasons.append(CorrelationReason("same_sensor",0.05,0.05,f"shared sensor {anchor.sensor_id}"))
            if event.source != anchor.source:
                reasons.append(CorrelationReason("cross_domain",0.20,0.20,f"{anchor.source.value} ↔ {event.source.value}"))
            a_pid = anchor.features.get("pid") or anchor.metadata.get("pid")
            e_pid = event.features.get("pid") or event.metadata.get("pid")
            if a_pid is not None and a_pid == e_pid:
                reasons.append(CorrelationReason("same_process",0.20,0.20,f"shared PID {a_pid}"))
        # Combine independent pieces of evidence without naïvely summing arbitrary
        # weights into immediate saturation. This remains a ranking score, not a
        # calibrated probability of compromise.
        score = 0.0 if not reasons else 1.0 - prod(1.0 - min(max(r.contribution, 0.0), 0.95) for r in reasons)
        independent_domains = len({anchor.source, *(e.source for e in candidates if abs(e.timestamp_ns-anchor.timestamp_ns) <= self.window_ns)})
        confidence = min(1.0, 0.35 + 0.15 * independent_domains + 0.5 * score)
        return CorrelationResult(score, confidence, tuple(reasons), tuple(dict.fromkeys(evidence)))
