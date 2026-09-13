"""Repository abstractions that keep persistence outside collectors."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from truepass.database.models import EventRecord
from truepass.models.events import Event

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from truepass.database.models import BaselineRecord
    from truepass.detection.baseline import RFBaselineModel


class EventRepository:
    """Persist and retrieve canonical event envelopes."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, event: Event) -> EventRecord:
        record = EventRecord(
            id=event.event_id,
            timestamp_ns=event.timestamp_ns,
            received_timestamp_ns=event.received_timestamp_ns,
            source=event.source.value,
            sensor_id=event.sensor_id,
            host=event.host,
            event_type=event.event_type.value,
            severity=event.severity.value,
            confidence=event.confidence,
            features=event.features,
            metadata_json=event.metadata,
            provenance=event.provenance.model_dump(mode="json"),
            correlation_id=event.correlation_id,
            canonical_sha256=event.sha256(),
        )
        self._session.add(record)
        return record

    def get(self, event_id: UUID) -> EventRecord | None:
        return self._session.get(EventRecord, event_id)

    def recent(self, limit: int = 100) -> Sequence[EventRecord]:
        statement = select(EventRecord).order_by(EventRecord.timestamp_ns.desc()).limit(limit)
        return self._session.scalars(statement).all()

class BaselineRepository:
    """Persist versioned baseline models in the canonical relational store."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add_rf_baseline(self, baseline: "RFBaselineModel") -> "BaselineRecord":
        from datetime import datetime

        from truepass.database.models import BaselineRecord

        created = datetime.fromisoformat(baseline.created_at)
        record = BaselineRecord(
            baseline_type="rf",
            sensor_id=baseline.sensor_id,
            created_timestamp_ns=int(created.timestamp() * 1_000_000_000),
            model_data=baseline.to_dict(),
        )
        self._session.add(record)
        return record
