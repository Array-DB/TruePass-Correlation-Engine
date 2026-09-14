"""SQLAlchemy persistence models for TruePass phases 1-4."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Float, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    pass


class EventRecord(Base):
    __tablename__ = "events"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    timestamp_ns: Mapped[int] = mapped_column(BigInteger, nullable=False)
    received_timestamp_ns: Mapped[int] = mapped_column(BigInteger, nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    sensor_id: Mapped[str] = mapped_column(String(255), nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    features: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)
    provenance: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    correlation_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    canonical_sha256: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        Index("ix_events_timestamp_ns", "timestamp_ns"),
        Index("ix_events_event_type", "event_type"),
        Index("ix_events_source", "source"),
        Index("ix_events_sensor_id", "sensor_id"),
        Index("ix_events_host", "host"),
        Index("ix_events_correlation_id", "correlation_id"),
    )


class IncidentRecord(Base):
    __tablename__ = "incidents"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    created_timestamp_ns: Mapped[int] = mapped_column(BigInteger, nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    explanation: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    event_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    sequence: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    digest: Mapped[str] = mapped_column(String(64), nullable=False)
    previous_digest: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_timestamp_ns: Mapped[int] = mapped_column(BigInteger, nullable=False)
    canonicalization_version: Mapped[str] = mapped_column(String(16), nullable=False, default="1")


class EvidenceRoot(Base):
    __tablename__ = "evidence_roots"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    first_sequence: Mapped[int] = mapped_column(BigInteger, nullable=False)
    last_sequence: Mapped[int] = mapped_column(BigInteger, nullable=False)
    leaf_count: Mapped[int] = mapped_column(BigInteger, nullable=False)
    root_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_timestamp_ns: Mapped[int] = mapped_column(BigInteger, nullable=False)


class SensorRegistry(Base):
    __tablename__ = "sensor_registry"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    sensor_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    sensor_type: Mapped[str] = mapped_column(String(64), nullable=False)
    host: Mapped[str | None] = mapped_column(String(255), nullable=True)
    enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)


class BaselineRecord(Base):
    __tablename__ = "baselines"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    baseline_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    sensor_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    created_timestamp_ns: Mapped[int] = mapped_column(BigInteger, nullable=False)
    model_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class IdentityProfile(Base):
    __tablename__ = "identity_profiles"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    external_subject_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    policy_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
