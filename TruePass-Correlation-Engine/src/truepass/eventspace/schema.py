"""Public event-space schema exports.

The canonical implementation lives in :mod:`truepass.models.events`; this module
provides the event-space import path described by the architecture document.
"""

from truepass.models.events import Event, EventSource, EventType, Provenance, Severity

__all__ = ["Event", "EventSource", "EventType", "Provenance", "Severity"]
