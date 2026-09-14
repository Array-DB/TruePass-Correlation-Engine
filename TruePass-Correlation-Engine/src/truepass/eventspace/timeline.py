"""Unified State-in-Event-Space timeline retrieval and state snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from uuid import UUID

from truepass.models.events import Event, EventSource


@dataclass(frozen=True, slots=True)
class ClockQuality:
    """Clock metadata carried with event-space analysis."""

    synchronized: bool
    source: str
    max_error_ns: int | None = None


@dataclass(frozen=True, slots=True)
class StateSnapshot:
    anchor_event_id: UUID
    timestamp_ns: int
    events: tuple[Event, ...]
    by_source: dict[EventSource, tuple[Event, ...]]
    clock_quality: ClockQuality


class Timeline:
    """In-memory deterministic timeline for normalized events.

    Database-backed retrieval can use the same API later; this implementation is
    intentionally small and testable for Phase 14.
    """

    def __init__(self, events: Iterable[Event] = (), *, clock_quality: ClockQuality | None = None) -> None:
        self._events = sorted(events, key=lambda event: (event.timestamp_ns, str(event.event_id)))
        self.clock_quality = clock_quality or ClockQuality(
            synchronized=False,
            source="system_wall_clock",
            max_error_ns=None,
        )

    def add(self, event: Event) -> None:
        self._events.append(event)
        self._events.sort(key=lambda item: (item.timestamp_ns, str(item.event_id)))

    def around(self, event_id: UUID, *, before_ms: float = 500, after_ms: float = 500) -> tuple[Event, ...]:
        if before_ms < 0 or after_ms < 0:
            raise ValueError("timeline window values must be non-negative")
        anchor = next((event for event in self._events if event.event_id == event_id), None)
        if anchor is None:
            raise KeyError(f"unknown event_id: {event_id}")
        start = anchor.timestamp_ns - int(before_ms * 1_000_000)
        end = anchor.timestamp_ns + int(after_ms * 1_000_000)
        return tuple(event for event in self._events if start <= event.timestamp_ns <= end)

    def snapshot(self, event_id: UUID, *, before_ms: float = 500, after_ms: float = 500) -> StateSnapshot:
        events = self.around(event_id, before_ms=before_ms, after_ms=after_ms)
        anchor = next(event for event in events if event.event_id == event_id)
        grouped: dict[EventSource, list[Event]] = {}
        for event in events:
            grouped.setdefault(event.source, []).append(event)
        return StateSnapshot(
            anchor_event_id=event_id,
            timestamp_ns=anchor.timestamp_ns,
            events=events,
            by_source={source: tuple(items) for source, items in grouped.items()},
            clock_quality=self.clock_quality,
        )
