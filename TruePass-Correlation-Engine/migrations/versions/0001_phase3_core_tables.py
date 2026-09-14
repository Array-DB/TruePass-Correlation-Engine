"""Create Phase 3 core persistence tables."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_phase3"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("timestamp_ns", sa.BigInteger(), nullable=False),
        sa.Column("received_timestamp_ns", sa.BigInteger(), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("sensor_id", sa.String(255), nullable=False),
        sa.Column("host", sa.String(255), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("features", sa.JSON(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("provenance", sa.JSON(), nullable=False),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("canonical_sha256", sa.String(64), nullable=False),
    )
    for name, column in (
        ("ix_events_timestamp_ns", "timestamp_ns"),
        ("ix_events_event_type", "event_type"),
        ("ix_events_source", "source"),
        ("ix_events_sensor_id", "sensor_id"),
        ("ix_events_host", "host"),
        ("ix_events_correlation_id", "correlation_id"),
    ):
        op.create_index(name, "events", [column])

    op.create_table(
        "incidents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_timestamp_ns", sa.BigInteger(), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("explanation", sa.JSON(), nullable=False),
    )
    op.create_table(
        "evidence_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sequence", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("digest", sa.String(64), nullable=False),
        sa.Column("previous_digest", sa.String(64), nullable=True),
        sa.Column("created_timestamp_ns", sa.BigInteger(), nullable=False),
    )
    op.create_index("ix_evidence_records_event_id", "evidence_records", ["event_id"])
    op.create_table(
        "evidence_roots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("first_sequence", sa.BigInteger(), nullable=False),
        sa.Column("last_sequence", sa.BigInteger(), nullable=False),
        sa.Column("leaf_count", sa.BigInteger(), nullable=False),
        sa.Column("root_hash", sa.String(64), nullable=False),
        sa.Column("created_timestamp_ns", sa.BigInteger(), nullable=False),
    )
    op.create_table(
        "sensor_registry",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("sensor_id", sa.String(255), nullable=False, unique=True),
        sa.Column("sensor_type", sa.String(64), nullable=False),
        sa.Column("host", sa.String(255), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
    )
    op.create_table(
        "baselines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("baseline_type", sa.String(64), nullable=False),
        sa.Column("sensor_id", sa.String(255), nullable=True),
        sa.Column("created_timestamp_ns", sa.BigInteger(), nullable=False),
        sa.Column("model_data", sa.JSON(), nullable=False),
    )
    op.create_index("ix_baselines_baseline_type", "baselines", ["baseline_type"])
    op.create_index("ix_baselines_sensor_id", "baselines", ["sensor_id"])
    op.create_table(
        "identity_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("external_subject_id", sa.String(255), nullable=False, unique=True),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("policy_data", sa.JSON(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("identity_profiles")
    op.drop_index("ix_baselines_sensor_id", table_name="baselines")
    op.drop_index("ix_baselines_baseline_type", table_name="baselines")
    op.drop_table("baselines")
    op.drop_table("sensor_registry")
    op.drop_table("evidence_roots")
    op.drop_index("ix_evidence_records_event_id", table_name="evidence_records")
    op.drop_table("evidence_records")
    op.drop_table("incidents")
    for name in (
        "ix_events_correlation_id",
        "ix_events_host",
        "ix_events_sensor_id",
        "ix_events_source",
        "ix_events_event_type",
        "ix_events_timestamp_ns",
    ):
        op.drop_index(name, table_name="events")
    op.drop_table("events")
