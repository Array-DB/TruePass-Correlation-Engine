"""Small in-memory runtime used by the API and local dashboard.

Production persistence can swap this service for repositories without changing
route contracts.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from truepass.models.events import Event
from truepass.vectors.search import InMemoryVectorIndex


@dataclass(slots=True)
class RuntimeState:
    events: list[Event] = field(default_factory=list)
    incidents: list[dict[str, object]] = field(default_factory=list)
    sensors: dict[str, dict[str, object]] = field(default_factory=dict)
    vector_index: InMemoryVectorIndex = field(default_factory=lambda: InMemoryVectorIndex(8))
    ledger_verified: bool = True

    def add_event(self, event: Event) -> None:
        self.events.append(event)
        self.sensors.setdefault(event.sensor_id, {"sensor_id": event.sensor_id, "source": event.source.value, "host": event.host, "status": "observed"})
