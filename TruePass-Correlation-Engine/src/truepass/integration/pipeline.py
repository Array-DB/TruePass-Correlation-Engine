"""Synthetic end-to-end TruePass integration pipeline.

The pipeline intentionally uses synthetic/read-only observations so CI can exercise
correlation, persistence, evidence chaining, Merkle verification, and API exposure
without RF hardware or privileged host access.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from truepass.api.server import create_app
from truepass.api.state import RuntimeState
from truepass.correlation.engine import TemporalCorrelationEngine
from truepass.database.models import Base, IncidentRecord
from truepass.database.repositories import EventRepository
from truepass.evidence.ledger import FileEvidenceLedger
from truepass.evidence.merkle import MerkleTree
from truepass.detection.baseline import RFBaselineTrainer
from truepass.sdr.sources import SDRConfig, SyntheticIQSource
from truepass.spectrum.features import extract_rf_features
from truepass.incidents.scoring import IncidentScorer
from truepass.models.events import Event, EventSource, EventType, Provenance, Severity


@dataclass(frozen=True, slots=True)
class IntegrationResult:
    events: int
    correlation_score: float
    incident_score: float
    incident_id: str
    ledger_verified: bool
    merkle_verified: bool
    api_incident_visible: bool


class SyntheticIntegrationPipeline:
    """Run the Phase-30/35 synthetic flow with an isolated local SQLite database."""

    def _event(self, *, source: EventSource, event_type: EventType, timestamp_ns: int,
               features: dict[str, object] | None = None,
               severity: Severity = Severity.INFO) -> Event:
        return Event(
            timestamp_ns=timestamp_ns,
            received_timestamp_ns=timestamp_ns + 1_000,
            source=source,
            sensor_id="synthetic-ci",
            host="truepass-ci-host",
            event_type=event_type,
            severity=severity,
            confidence=0.95,
            features=features or {},
            metadata={"synthetic": True, "authorized": True},
            provenance=Provenance(collector="synthetic-e2e", method="generated"),
        )

    def run(self) -> IntegrationResult:
        base = 1_800_000_000_000_000_000
        sdr_config = SDRConfig(sample_rate=2_000_000.0, center_frequency=100_000_000.0, buffer_size=4096)
        baseline_features = []
        for seed in range(6):
            source = SyntheticIQSource(sdr_config, tone_hz=100_000.0, noise_amplitude=0.02, seed=seed)
            baseline_features.append(
                extract_rf_features(
                    source.read_samples(4096),
                    sample_rate_hz=sdr_config.sample_rate,
                    center_frequency_hz=sdr_config.center_frequency,
                )
            )
        now = datetime.now(UTC)
        baseline = RFBaselineTrainer().fit(
            baseline_features,
            sensor_id="synthetic-ci",
            frequency_band_hz=(99_000_000.0, 101_000_000.0),
            training_start=now - timedelta(minutes=5),
            training_end=now,
            model_id="synthetic-e2e-baseline",
        )
        anomaly_source = SyntheticIQSource(
            sdr_config, tone_hz=350_000.0, noise_amplitude=0.15, seed=999
        )
        anomaly_features = extract_rf_features(
            anomaly_source.read_samples(4096),
            sample_rate_hz=sdr_config.sample_rate,
            center_frequency_hz=sdr_config.center_frequency,
        )
        baseline_distance = baseline.anomaly_score(anomaly_features)
        normalized_anomaly = min(1.0, baseline_distance / 10.0)
        rf = self._event(
            source=EventSource.SDR,
            event_type=EventType.RF_ANOMALY,
            timestamp_ns=base,
            severity=Severity.MEDIUM,
            features={
                "anomaly_score": normalized_anomaly,
                "baseline_distance": baseline_distance,
                "peak_frequency_hz": anomaly_features.peak_frequency_hz,
                "feature_schema_version": anomaly_features.feature_schema_version,
            },
        )
        wifi = self._event(
            source=EventSource.WIFI,
            event_type=EventType.WIFI_EVENT,
            timestamp_ns=base + 30_000_000,
            features={"ssid": "synthetic-lab", "state": "changed"},
        )
        process = self._event(
            source=EventSource.PROCESS,
            event_type=EventType.PROCESS_STARTED,
            timestamp_ns=base + 55_000_000,
            features={"pid": 4242, "name": "synthetic-agent"},
        )
        socket = self._event(
            source=EventSource.NETWORK,
            event_type=EventType.NETWORK_CONNECTION,
            timestamp_ns=base + 80_000_000,
            features={"pid": 4242, "remote_ip": "192.0.2.10", "remote_port": 443},
        )
        events = [rf, wifi, process, socket]

        correlation = TemporalCorrelationEngine(window_ms=250).correlate(rf, events)
        assessment = IncidentScorer().score(rf, correlation)

        engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(engine)
        incident_id = uuid4()
        with Session(engine) as session:
            repo = EventRepository(session)
            for event in events:
                repo.add(event)
            session.add(
                IncidentRecord(
                    id=incident_id,
                    created_timestamp_ns=base + 100_000_000,
                    severity=assessment.severity.value,
                    score=assessment.score,
                    confidence=assessment.confidence,
                    explanation={
                        "candidate_explanations": list(assessment.candidate_explanations),
                        "evidence_ids": list(assessment.evidence_ids),
                        "causation_established": False,
                    },
                )
            )
            session.commit()
            if session.get(IncidentRecord, incident_id) is None:
                raise RuntimeError("incident persistence failed")

        with TemporaryDirectory(prefix="truepass-e2e-") as tmp:
            ledger = FileEvidenceLedger(Path(tmp) / "ledger.jsonl")
            records = [ledger.append(event) for event in events]
            ledger_ok = ledger.verify().valid
            tree = MerkleTree([bytes.fromhex(record.event_hash) for record in records])
            proof = tree.proof(0)
            merkle_ok = MerkleTree.verify(proof, tree.root_hex)

        runtime = RuntimeState()
        for event in events:
            runtime.add_event(event)
        runtime.incidents.append(
            {
                "incident_id": str(incident_id),
                "score": assessment.score,
                "severity": assessment.severity.value,
                "confidence": assessment.confidence,
                "evidence_ids": list(assessment.evidence_ids),
            }
        )
        client = TestClient(create_app(runtime))
        response = client.get("/incidents")
        response.raise_for_status()
        api_visible = any(item.get("incident_id") == str(incident_id) for item in response.json())

        return IntegrationResult(
            events=len(events),
            correlation_score=correlation.score,
            incident_score=assessment.score,
            incident_id=str(incident_id),
            ledger_verified=ledger_ok,
            merkle_verified=merkle_ok,
            api_incident_visible=api_visible,
        )
