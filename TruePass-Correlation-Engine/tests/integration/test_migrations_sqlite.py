from sqlalchemy import create_engine, inspect

from truepass.database.models import Base


def test_schema_can_be_created_for_local_integration() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    tables = set(inspect(engine).get_table_names())
    assert {"events", "incidents", "evidence_records", "evidence_roots", "baselines"} <= tables
