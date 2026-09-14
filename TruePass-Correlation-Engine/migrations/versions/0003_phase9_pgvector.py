"""Phase 9 pgvector persistence.

Revision ID: 0003_phase9
Revises: 0002_phase8
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_phase9"
down_revision = "0002_phase8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        # Keep SQLite migration smoke tests portable; production PostgreSQL gets pgvector.
        return
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute(
        "CREATE TABLE IF NOT EXISTS event_vectors ("
        "item_id TEXT PRIMARY KEY, "
        "embedding vector(32) NOT NULL, "
        "metadata JSONB NOT NULL DEFAULT '{}'::jsonb)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_event_vectors_embedding_hnsw "
        "ON event_vectors USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TABLE IF EXISTS event_vectors")
