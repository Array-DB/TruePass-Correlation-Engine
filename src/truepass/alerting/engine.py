"""Explainable alert generation with deduplication and cooldowns."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time
from collections.abc import Callable, Iterable
from truepass.models.events import Event, EventType, Severity

@dataclass(frozen=True, slots=True)
class AlertRule:
    rule_id: str
    description: str
    minimum_severity: Severity = Severity.MEDIUM
    event_types: frozenset[EventType] = field(default_factory=frozenset)
    cooldown_seconds: float = 300.0
    predicate: Callable[[Event], bool] | None = field(default=None, compare=False, repr=False)

    def matches(self, event: Event) -> bool:
        if self.event_types and event.event_type not in self.event_types:
            return False
        return self.predicate(event) if self.predicate is not None else True

@dataclass(frozen=True, slots=True)
class Alert:
    alert_id: str
    rule_id: str
    event_id: str
    severity: Severity
    reason: str
    created_ns: int
    dedup_key: str

class AlertEngine:
    """Evaluates rules without changing monitored systems."""
    def __init__(self, rules: Iterable[AlertRule], *, clock: Callable[[], float] = time.monotonic) -> None:
        self._rules = tuple(rules)
        self._clock = clock
        self._last_emitted: dict[str, float] = {}

    @staticmethod
    def _key(rule: AlertRule, event: Event) -> str:
        material = f"{rule.rule_id}|{event.sensor_id}|{event.host}|{event.event_type.value}"
        return hashlib.sha256(material.encode()).hexdigest()

    def evaluate(self, event: Event) -> list[Alert]:
        now = self._clock()
        emitted: list[Alert] = []
        for rule in self._rules:
            if not rule.matches(event):
                continue
            key = self._key(rule, event)
            previous = self._last_emitted.get(key)
            if previous is not None and now - previous < rule.cooldown_seconds:
                continue
            self._last_emitted[key] = now
            alert_id = hashlib.sha256(f"{key}|{event.event_id}|{now}".encode()).hexdigest()[:24]
            emitted.append(Alert(alert_id, rule.rule_id, str(event.event_id), event.severity, rule.description, time.time_ns(), key))
        return emitted

DEFAULT_RULES = (
    AlertRule("rf-anomaly", "RF anomaly requires investigation with cross-domain evidence.", Severity.MEDIUM, frozenset({EventType.RF_ANOMALY})),
    AlertRule("new-listener", "New listening port observation requires policy review.", Severity.MEDIUM, frozenset({EventType.LISTENING_PORT})),
    AlertRule("incident", "Incident candidate exceeded the configured reporting threshold.", Severity.HIGH, frozenset({EventType.INCIDENT})),
)
