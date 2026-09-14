from pathlib import Path
from truepass.vectors.search import PostgresVectorStore


def test_pgvector_literal_and_migration_contract() -> None:
    assert PostgresVectorStore._literal([1, 2.5, -3]) == "[1,2.5,-3]"
    migration = Path("migrations/versions/0003_phase9_pgvector.py").read_text(encoding="utf-8")
    assert "CREATE EXTENSION IF NOT EXISTS vector" in migration
    assert "vector_cosine_ops" in migration
