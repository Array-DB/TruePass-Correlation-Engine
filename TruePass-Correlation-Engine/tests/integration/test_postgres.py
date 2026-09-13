import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from truepass.database.models import Base
from truepass.database.repositories import EventRepository
from truepass.models.events import Event, EventSource, EventType, Provenance


@pytest.mark.postgres
def test_event_round_trip_postgres() -> None:
    url = os.getenv("TRUEPASS_TEST_DATABASE_URL")
    if not url:
        pytest.skip("set TRUEPASS_TEST_DATABASE_URL to run PostgreSQL integration tests")
    engine = create_engine(url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    try:
        event = Event(
            source=EventSource.PROCESS,
            sensor_id="integration",
            host="localhost",
            event_type=EventType.PROCESS_STARTED,
            provenance=Provenance(collector="test", method="integration"),
        )
        with Session(engine) as session:
            repository = EventRepository(session)
            repository.add(event)
            session.commit()
            stored = repository.get(event.event_id)
            assert stored is not None
            assert stored.canonical_sha256 == event.sha256()
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT count(*) FROM events")) == 1
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()
