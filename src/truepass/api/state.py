"""Runtime state used by the API and local dashboard.

Production persistence can swap these collections for repositories without changing
route contracts. Realtime streams are bounded through :class:`RealtimeHub`.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from truepass.api.realtime import RealtimeHub
from truepass.age import AgeService
from truepass.alerting import AlertEngine, DEFAULT_RULES
from truepass.identity import ContextAssertionFactor, IdentityPolicy, IdentityVerifier
from truepass.privacy import GovernancePolicy, DEFAULT_POLICIES
from truepass.models.events import Event
from truepass.vectors.search import InMemoryVectorIndex
from truepass.scan import ScanService
from truepass.detection.rf_intelligence import RFIntelligenceEngine


@dataclass(slots=True)
class RuntimeState:
    events: list[Event] = field(default_factory=list)
    incidents: list[dict[str, object]] = field(default_factory=list)
    sensors: dict[str, dict[str, object]] = field(default_factory=dict)
    vector_index: InMemoryVectorIndex = field(default_factory=lambda: InMemoryVectorIndex(8))
    ledger_verified: bool = True
    baselines: list[dict[str, object]] = field(default_factory=list)
    latest_spectrum: dict[str, object] | None = None
    hub: RealtimeHub = field(default_factory=RealtimeHub)
    scan: ScanService = field(default_factory=ScanService)
    age: AgeService = field(default_factory=AgeService)
    alert_engine: AlertEngine = field(default_factory=lambda: AlertEngine(DEFAULT_RULES))
    identity_verifier: IdentityVerifier = field(default_factory=lambda: IdentityVerifier(
        [ContextAssertionFactor("session", "session_verified"), ContextAssertionFactor("operator", "operator_verified")],
        IdentityPolicy(threshold=0.5, minimum_factors=1),
    ))
    privacy: GovernancePolicy = field(default_factory=lambda: GovernancePolicy(DEFAULT_POLICIES))
    alert_log: list[dict[str, object]] = field(default_factory=list)
    audit_log: list[dict[str, object]] = field(default_factory=list)
    rf_intelligence: RFIntelligenceEngine = field(default_factory=RFIntelligenceEngine)
    rf_feature_history: list[list[float]] = field(default_factory=list)
    telemetry: object | None = None
    spectrum_stream: object | None = None
    max_events: int = 5000
    settings: dict[str, object] = field(default_factory=lambda: {
        "retention_profile": "default",
        "rf_anomaly_threshold": 0.75,
        "incident_threshold": 0.70,
        "scan_scope": "local-host",
    })

    def add_event(self, event: Event) -> None:
        self.events.append(event)
        if len(self.events) > self.max_events:
            del self.events[:-self.max_events]
        self.sensors.setdefault(event.sensor_id, {
            "sensor_id": event.sensor_id,
            "source": event.source.value,
            "host": event.host,
            "status": "observed",
        })

    async def publish_event(self, event: Event) -> None:
        self.add_event(event)
        self.age.append(event)
        verification = self.age.ledger.verify()
        self.ledger_verified = verification.valid
        payload = event.model_dump(mode="json")
        await self.hub.publish("events", payload)
        for alert in self.alert_engine.evaluate(event):
            item = {
                "alert_id": alert.alert_id, "rule_id": alert.rule_id, "event_id": alert.event_id,
                "severity": alert.severity.value, "reason": alert.reason, "created_ns": alert.created_ns,
            }
            self.alert_log.append(item)
            if len(self.alert_log) > 2000:
                del self.alert_log[:-2000]
            await self.hub.publish("alerts", item)

    async def publish_incident(self, incident: dict[str, object]) -> None:
        self.incidents.append(incident)
        await self.hub.publish("incidents", incident)

    async def publish_spectrum(self, frame: dict[str, object]) -> None:
        self.latest_spectrum = frame
        await self.hub.publish("spectrum", frame)
