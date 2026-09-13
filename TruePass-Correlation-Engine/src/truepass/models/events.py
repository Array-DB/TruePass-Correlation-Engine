"""Canonical event models used across every TruePass telemetry domain."""

from __future__ import annotations

import hashlib
import json
import socket
import time
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EventSource(StrEnum):
    """Originating telemetry domain."""

    SYSTEM = "system"
    PROCESS = "process"
    NETWORK = "network"
    WIFI = "wifi"
    BLUETOOTH = "bluetooth"
    AUTH = "auth"
    SDR = "sdr"
    CORRELATION = "correlation"
    EVIDENCE = "evidence"


class EventType(StrEnum):
    """Canonical event types required by the TruePass event envelope."""

    PROCESS_STARTED = "process_started"
    PROCESS_STOPPED = "process_stopped"
    NETWORK_CONNECTION = "network_connection"
    LISTENING_PORT = "listening_port"
    DNS_EVENT = "dns_event"
    WIFI_EVENT = "wifi_event"
    BLUETOOTH_EVENT = "bluetooth_event"
    AUTH_EVENT = "auth_event"
    RF_OBSERVATION = "rf_observation"
    RF_ANOMALY = "rf_anomaly"
    INCIDENT = "incident"
    EVIDENCE_RECORD = "evidence_record"


class Severity(StrEnum):
    """Human-readable security severity without implying causation."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Provenance(BaseModel):
    """How, where, and by which component an observation was produced."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    collector: str
    collector_version: str = "1.0.0"
    method: str
    platform: str | None = None
    clock: str = "system_wall_clock"


class Event(BaseModel):
    """Common immutable envelope for normalized TruePass observations."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: UUID = Field(default_factory=uuid4)
    timestamp_ns: int = Field(default_factory=time.time_ns, ge=0)
    received_timestamp_ns: int = Field(default_factory=time.time_ns, ge=0)
    source: EventSource
    sensor_id: str = Field(min_length=1, max_length=255)
    host: str = Field(default_factory=socket.gethostname, min_length=1, max_length=255)
    event_type: EventType
    severity: Severity = Severity.INFO
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    features: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    provenance: Provenance
    correlation_id: UUID | None = None

    @field_validator("received_timestamp_ns")
    @classmethod
    def received_timestamp_must_be_positive(cls, value: int) -> int:
        if value < 0:
            raise ValueError("received_timestamp_ns must be non-negative")
        return value

    def canonical_bytes(self) -> bytes:
        """Return deterministic UTF-8 JSON bytes suitable for evidence hashing."""

        payload = self.model_dump(mode="json", exclude_none=False)
        return json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")

    def sha256(self) -> str:
        """Return the SHA-256 digest of the canonical event representation."""

        return hashlib.sha256(self.canonical_bytes()).hexdigest()
