"""FastAPI service for TruePass operator and integration workflows."""
from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated
from datetime import UTC, datetime
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, Field

from truepass.alerting import AlertEngine, DEFAULT_RULES
from truepass.api.dependencies import api_key_dependency
from truepass.api.state import RuntimeState
from truepass.correlation.engine import TemporalCorrelationEngine
from truepass.eventspace.timeline import Timeline
from truepass.incidents import IncidentPipeline
from truepass.models.events import Event, EventSource, EventType, Provenance
from truepass.privacy import DataDomain
from truepass.security.hardening import constant_time_secret_matches
from truepass.sdr.sources import SDRConfig, open_sdr_source
from truepass.spectrum.pipeline import SpectrumDSPPipeline
from truepass.detection.clustering import DBSCANClusterer
from truepass.config import AppSettings
from truepass.runtime.telemetry import TelemetryService


class IdentityVerificationRequest(BaseModel):
    subject_id: str = Field(min_length=1, max_length=128)
    session_verified: bool = False
    operator_verified: bool = False


class SettingsPatch(BaseModel):
    retention_profile: str | None = Field(default=None, max_length=64)
    rf_anomaly_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    incident_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    scan_scope: str | None = Field(default=None, pattern="^local-host$")


def create_app(state: RuntimeState | None = None, *, api_key: str | None = None) -> FastAPI:
    runtime = state or RuntimeState()
    dependencies = [Depends(api_key_dependency(api_key))]

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        flag = os.getenv("TRUEPASS_AUTO_COLLECT")
        should_collect = flag != "0" and not (os.getenv("PYTEST_CURRENT_TEST") and flag != "1")
        if should_collect:
            settings = AppSettings.load()
            service = TelemetryService(settings=settings, publish_event=runtime.publish_event)
            runtime.telemetry = service
            await service.start()
        try:
            yield
        finally:
            service = runtime.telemetry
            if service is not None and hasattr(service, "stop"):
                await service.stop()

    app = FastAPI(
        title="TruePass API",
        version="1.0.0",
        description="Defensive telemetry, correlation, evidence, and realtime API",
        dependencies=dependencies,
        lifespan=lifespan,
    )
    app.state.truepass = runtime

    @app.middleware("http")
    async def security_headers(request: Request, call_next):  # type: ignore[no-untyped-def]
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; connect-src 'self' ws: wss:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; img-src 'self' data:",
        )
        if request.url.path.startswith("/api/"):
            response.headers.setdefault("Cache-Control", "no-store")
        return response

    @app.get("/health", tags=["system"])
    @app.get("/api/v1/health", tags=["system"])
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "events": len(runtime.events),
            "incidents": len(runtime.incidents),
            "ledger_verified": runtime.ledger_verified,
            "spectrum_available": runtime.latest_spectrum is not None,
        }

    @app.get("/api/v1/telemetry/status", tags=["system"])
    def telemetry_status() -> dict[str, object]:
        service = runtime.telemetry
        if service is None or not hasattr(service, "status"):
            return {"running": False, "collectors": [], "latest_host": None, "host_history": []}
        return service.status()

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> PlainTextResponse:
        return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)

    @app.post("/events", response_model=Event, status_code=201, tags=["events"])
    @app.post("/api/v1/events", response_model=Event, status_code=201, tags=["events"])
    async def create_event(event: Event) -> Event:
        await runtime.publish_event(event)
        return event

    @app.get("/events", response_model=list[Event], tags=["events"])
    @app.get("/api/v1/events", response_model=list[Event], tags=["events"])
    def list_events(
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=500)] = 100,
        source: EventSource | None = None,
        event_type: EventType | None = None,
    ) -> list[Event]:
        items = runtime.events
        if source is not None:
            items = [event for event in items if event.source == source]
        if event_type is not None:
            items = [event for event in items if event.event_type == event_type]
        return items[offset : offset + limit]

    @app.get("/events/{event_id}", response_model=Event, tags=["events"])
    @app.get("/api/v1/events/{event_id}", response_model=Event, tags=["events"])
    def get_event(event_id: str) -> Event:
        for event in runtime.events:
            if str(event.event_id) == event_id:
                return event
        raise HTTPException(404, "event not found")

    @app.get("/incidents", tags=["incidents"])
    @app.get("/api/v1/incidents", tags=["incidents"])
    def incidents(offset: int = 0, limit: int = 100) -> list[dict[str, object]]:
        if offset < 0 or not 1 <= limit <= 500:
            raise HTTPException(422, "invalid pagination")
        return runtime.incidents[offset : offset + limit]

    @app.post("/api/v1/incidents/evaluate/{event_id}", tags=["incidents"])
    async def evaluate_incident(event_id: str, window_ms: float = 500.0) -> dict[str, object]:
        anchor = next((event for event in runtime.events if str(event.event_id) == event_id), None)
        if anchor is None:
            raise HTTPException(404, "event not found")
        try:
            incident = IncidentPipeline(window_ms=window_ms).evaluate(anchor, tuple(runtime.events)).as_dict()
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        await runtime.publish_incident(incident)
        return incident

    @app.get("/sensors", tags=["sensors"])
    @app.get("/api/v1/sensors", tags=["sensors"])
    def sensors() -> list[dict[str, object]]:
        return sorted(runtime.sensors.values(), key=lambda item: str(item["sensor_id"]))

    @app.get("/timeline/{event_id}", tags=["timeline"])
    @app.get("/api/v1/timeline/{event_id}", tags=["timeline"])
    def timeline(event_id: str, before_ms: float = 500.0, after_ms: float = 500.0) -> list[Event]:
        event_timeline = Timeline(runtime.events)
        try:
            return list(event_timeline.around(UUID(event_id), before_ms=before_ms, after_ms=after_ms))
        except (KeyError, ValueError) as exc:
            raise HTTPException(404 if isinstance(exc, KeyError) else 422, str(exc)) from exc

    @app.get("/correlation/{event_id}", tags=["correlation"])
    @app.get("/api/v1/correlation/{event_id}", tags=["correlation"])
    def correlation(event_id: str, window_ms: float = 500.0) -> dict[str, object]:
        anchor = next((event for event in runtime.events if str(event.event_id) == event_id), None)
        if anchor is None:
            raise HTTPException(404, "event not found")
        try:
            result = TemporalCorrelationEngine(window_ms=window_ms).correlate(anchor, runtime.events)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        return {
            "score": result.score,
            "confidence": result.confidence,
            "evidence_ids": result.evidence_ids,
            "reasons": [
                {"code": reason.code, "weight": reason.weight, "contribution": reason.contribution, "detail": reason.detail}
                for reason in result.reasons
            ],
            "causation_established": False,
        }

    @app.get("/evidence", tags=["evidence"])
    @app.get("/api/v1/evidence", tags=["evidence"])
    def evidence() -> dict[str, object]:
        return {"ledger_verified": runtime.ledger_verified, "event_count": len(runtime.events)}

    @app.get("/baselines", tags=["baselines"])
    @app.get("/api/v1/baselines", tags=["baselines"])
    def baselines() -> list[dict[str, object]]:
        return runtime.baselines

    @app.post("/similarity", tags=["similarity"])
    @app.post("/api/v1/similarity", tags=["similarity"])
    def similarity(vector: list[float], limit: int = 5) -> list[dict[str, object]]:
        try:
            hits = runtime.vector_index.search(vector, limit=limit)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        return [{"item_id": hit.item_id, "similarity": hit.similarity} for hit in hits]

    @app.get("/system", tags=["system"])
    @app.get("/api/v1/system", tags=["system"])
    def system() -> dict[str, object]:
        return {
            "api": "healthy",
            "event_count": len(runtime.events),
            "sensor_count": len(runtime.sensors),
            "incident_count": len(runtime.incidents),
            "ledger": "verified" if runtime.ledger_verified else "failed",
            "realtime": True,
        }

    @app.get("/alerts", tags=["alerts"])
    @app.get("/api/v1/alerts", tags=["alerts"])
    def alerts(limit: int = 100) -> list[dict[str, object]]:
        if not 1 <= limit <= 500:
            raise HTTPException(422, "invalid limit")
        return runtime.alert_log[-limit:]

    @app.get("/api/v1/alerts/summary", tags=["alerts"])
    def alert_summary() -> dict[str, object]:
        severities: dict[str, int] = {}
        for alert in runtime.alert_log:
            key = str(alert.get("severity", "unknown"))
            severities[key] = severities.get(key, 0) + 1
        return {"total": len(runtime.alert_log), "by_severity": severities}

    @app.get("/api/v1/spectrum", tags=["spectrum"])
    def latest_spectrum() -> dict[str, object]:
        if runtime.latest_spectrum is None:
            raise HTTPException(404, "no spectrum frame available")
        return runtime.latest_spectrum

    @app.post("/api/v1/spectrum/capture", tags=["spectrum"])
    async def capture_spectrum(
        device: str = "synthetic",
        sample_rate: float = 2_000_000.0,
        center_frequency: float = 100_000_000.0,
        gain: float = 0.0,
        samples: int = Query(default=4096, ge=256, le=262144),
        serial: str | None = None,
    ) -> dict[str, object]:
        config = SDRConfig(
            sample_rate=sample_rate,
            center_frequency=center_frequency,
            gain=gain,
            buffer_size=samples,
            device=device,
        )
        source = None
        try:
            source = open_sdr_source(config, serial=serial)
            iq = await asyncio.to_thread(source.read_samples, samples)
            if len(iq) < 8:
                raise HTTPException(503, "SDR returned too few samples")
            frame = await asyncio.to_thread(
                SpectrumDSPPipeline(
                    sample_rate_hz=sample_rate,
                    center_frequency_hz=center_frequency,
                ).process,
                iq,
            )
            payload = frame.as_dict()
            payload["source"] = device
            payload["serial"] = serial
            payload["data_origin"] = "synthetic-test" if device.lower().strip() == "synthetic" else "hardware-rx"
            assessment = runtime.rf_intelligence.observe(frame.features)
            payload["rf_assessment"] = {
                "is_anomaly": assessment.is_anomaly,
                "score": assessment.score,
                "reasons": list(assessment.reasons),
                "model_ids": list(assessment.model_ids),
                "sample_count": assessment.sample_count,
            }
            runtime.rf_feature_history.append(frame.features.numeric_vector().tolist())
            if len(runtime.rf_feature_history) > 128:
                del runtime.rf_feature_history[:-128]
            cluster_payload: dict[str, object] = {
                "label": None, "cluster_count": 0, "model_id": "dbscan-v1",
                "reason": "collecting RF feature history",
            }
            if len(runtime.rf_feature_history) >= 5:
                try:
                    clustered = DBSCANClusterer(eps=1.2, min_samples=2).fit_predict(runtime.rf_feature_history)
                    cluster_payload = {
                        "label": clustered.labels[-1],
                        "cluster_count": clustered.cluster_count,
                        "model_id": clustered.model_id,
                        "reason": clustered.reason,
                    }
                except ValueError:
                    pass
            payload["cluster"] = cluster_payload
            await runtime.publish_spectrum(payload)
            if assessment.is_anomaly:
                event = Event(
                    timestamp_ns=int(payload["timestamp_ns"]),
                    source=EventSource.SDR,
                    sensor_id=f"sdr-{device}",
                    host="localhost",
                    event_type=EventType.RF_ANOMALY,
                    severity="medium",
                    confidence=min(1.0, max(0.0, float(assessment.score))),
                    features={
                        "anomaly_score": float(assessment.score),
                        "cluster": cluster_payload,
                        "rf_features": payload["features"],
                    },
                    metadata={"receive_only": True, "device": device, "serial": serial},
                    provenance=Provenance(collector="spectrum-capture", method="dsp-rf-assessment"),
                )
                await runtime.publish_event(event)
            return payload
        except HTTPException:
            raise
        except (RuntimeError, ValueError) as exc:
            raise HTTPException(503, str(exc)) from exc
        finally:
            if source is not None and hasattr(source, "close"):
                await asyncio.to_thread(source.close)  # type: ignore[attr-defined]

    @app.get("/api/v1/verification/dod", tags=["verification"])
    def definition_of_done(include_external: bool = False) -> dict[str, object]:
        from truepass.verification import run_overall_dod_audit
        return run_overall_dod_audit(include_external=include_external).as_dict()

    @app.get("/dashboard/summary", tags=["dashboard"])
    @app.get("/api/v1/dashboard", tags=["dashboard"])
    def dashboard_summary() -> dict[str, object]:
        anomaly_count = sum(1 for event in runtime.events if event.event_type == EventType.RF_ANOMALY)
        now_ns = datetime.now(UTC).timestamp() * 1_000_000_000
        cutoff_ns = int(now_ns - 10_000_000_000)
        recent_10s = [event for event in runtime.events if event.timestamp_ns >= cutoff_ns]
        source_counts: dict[str, int] = {}
        for event in runtime.events:
            source_counts[event.source.value] = source_counts.get(event.source.value, 0) + 1
        telemetry = runtime.telemetry.status() if runtime.telemetry is not None and hasattr(runtime.telemetry, "status") else {"running": False, "collectors": [], "latest_host": None, "host_history": []}
        return {
            "health": "healthy" if runtime.ledger_verified else "degraded",
            "events": len(runtime.events),
            "sensors": len(runtime.sensors),
            "incidents": len(runtime.incidents),
            "rf_anomalies": anomaly_count,
            "ledger_verified": runtime.ledger_verified,
            "spectrum_available": runtime.latest_spectrum is not None,
            "ingest_rate_eps": len(recent_10s) / 10.0,
            "source_counts": source_counts,
            "telemetry": telemetry,
            "recent_events": [event.model_dump(mode="json") for event in runtime.events[-50:]],
        }

    @app.get("/api/v1/live", tags=["live"])
    def live_snapshot(limit: int = 100) -> dict[str, object]:
        if not 1 <= limit <= 500:
            raise HTTPException(422, "invalid limit")
        return {
            "events": [event.model_dump(mode="json") for event in runtime.events[-limit:]],
            "incidents": runtime.incidents[-limit:],
            "spectrum": runtime.latest_spectrum,
        }

    @app.post("/api/v1/scan/sessions", tags=["scan"])
    def start_scan(authorization_acknowledged: bool = False, scope: str = "local-host") -> dict[str, object]:
        try:
            session = runtime.scan.start(
                authorization_acknowledged=authorization_acknowledged,
                scope=scope,
            )
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        return session.summary()

    @app.get("/api/v1/scan/sessions", tags=["scan"])
    def scan_sessions() -> list[dict[str, object]]:
        return [session.summary() for session in runtime.scan.sessions.values()]

    def _scan_session(session_id: str):
        try:
            return runtime.scan.get(session_id)
        except KeyError as exc:
            raise HTTPException(404, str(exc)) from exc

    @app.get("/api/v1/scan/sessions/{session_id}", tags=["scan"])
    def scan_session(session_id: str) -> dict[str, object]:
        return _scan_session(session_id).summary()

    @app.post("/api/v1/scan/sessions/{session_id}/refresh", tags=["scan"])
    def refresh_scan(session_id: str) -> dict[str, object]:
        _scan_session(session_id)
        return runtime.scan.refresh(session_id)

    @app.post("/api/v1/scan/sessions/{session_id}/stop", tags=["scan"])
    def stop_scan(session_id: str) -> dict[str, object]:
        _scan_session(session_id)
        return runtime.scan.stop(session_id).summary()

    @app.get("/api/v1/scan/sessions/{session_id}/hosts", tags=["scan"])
    def scan_hosts(session_id: str) -> list[dict[str, object]]:
        _scan_session(session_id)
        return runtime.scan.hosts(session_id)

    @app.get("/api/v1/scan/sessions/{session_id}/ports", tags=["scan"])
    def scan_ports(session_id: str) -> list[dict[str, object]]:
        _scan_session(session_id)
        return runtime.scan.ports(session_id)

    @app.get("/api/v1/scan/sessions/{session_id}/processes", tags=["scan"])
    def scan_processes(session_id: str) -> list[dict[str, object]]:
        _scan_session(session_id)
        return runtime.scan.processes(session_id)

    @app.get("/api/v1/scan/sessions/{session_id}/connections", tags=["scan"])
    def scan_connections(session_id: str) -> list[dict[str, object]]:
        _scan_session(session_id)
        return runtime.scan.connections(session_id)

    @app.get("/api/v1/scan/sessions/{session_id}/devices", tags=["scan"])
    def scan_devices(session_id: str) -> dict[str, object]:
        _scan_session(session_id)
        return runtime.scan.devices(session_id)

    @app.get("/api/v1/scan/sessions/{session_id}/diff", tags=["scan"])
    def scan_diff(session_id: str) -> dict[str, object]:
        _scan_session(session_id)
        return runtime.scan.diff(session_id)

    @app.get("/api/v1/scan/sessions/{session_id}/report", tags=["scan"])
    def scan_report(session_id: str) -> dict[str, object]:
        _scan_session(session_id)
        return runtime.scan.report(session_id)

    @app.get("/api/v1/ledger/status", tags=["age"])
    def ledger_status() -> dict[str, object]:
        return runtime.age.status()

    @app.get("/api/v1/ledger/records", tags=["age"])
    def ledger_records(offset: int = 0, limit: int = 100) -> list[dict[str, object]]:
        if offset < 0 or not 1 <= limit <= 500:
            raise HTTPException(422, "invalid pagination")
        return runtime.age.records(offset=offset, limit=limit)

    @app.get("/api/v1/ledger/records/{sequence}", tags=["age"])
    def ledger_record(sequence: int) -> dict[str, object]:
        try:
            return runtime.age.verify_record(sequence)
        except KeyError as exc:
            raise HTTPException(404, "ledger record not found") from exc

    @app.post("/api/v1/ledger/batches", tags=["age"])
    def create_evidence_batch(start: int | None = None, end: int | None = None) -> dict[str, object]:
        try:
            return runtime.age.build_batch(start=start, end=end)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get("/api/v1/ledger/batches", tags=["age"])
    def evidence_batches() -> list[dict[str, object]]:
        return runtime.age.batches()

    @app.get("/api/v1/ledger/batches/{batch_id}/verify", tags=["age"])
    def verify_evidence_batch(batch_id: str) -> dict[str, object]:
        try:
            return runtime.age.verify_batch(batch_id)
        except KeyError as exc:
            raise HTTPException(404, "evidence batch not found") from exc

    @app.get("/api/v1/evidence/{sequence}/proof", tags=["age"])
    def evidence_proof(sequence: int, batch_id: str) -> dict[str, object]:
        try:
            return runtime.age.proof(batch_id, sequence)
        except KeyError as exc:
            raise HTTPException(404, "batch or ledger sequence not found") from exc

    @app.get("/api/v1/merkle/{batch_id}", tags=["age"])
    def merkle_batch(batch_id: str) -> dict[str, object]:
        try:
            batch = runtime.age.batch(batch_id)
        except KeyError as exc:
            raise HTTPException(404, "evidence batch not found") from exc
        return {
            "batch_id": batch.batch_id,
            "first_sequence": batch.first_sequence,
            "last_sequence": batch.last_sequence,
            "leaf_count": batch.leaf_count,
            "root_hash": batch.root_hash,
        }

    @app.get("/api/v1/anchors", tags=["age"])
    def anchors() -> dict[str, object]:
        return {
            "automatic_external_anchoring": False,
            "status": "not-configured",
            "note": "External timestamp anchoring is opt-in and requires an explicitly injected provider.",
        }

    @app.post("/api/v1/identity/verify", tags=["identity"])
    def verify_identity(request: IdentityVerificationRequest) -> dict[str, object]:
        decision = runtime.identity_verifier.verify(
            request.subject_id,
            {"session_verified": request.session_verified, "operator_verified": request.operator_verified},
        )
        result = {
            "subject_id": decision.subject_id,
            "authorized": decision.authorized,
            "score": decision.score,
            "reason": decision.reason,
            "factors": [
                {"factor_id": item.factor_id, "verified": item.verified, "confidence": item.confidence, "reason": item.reason}
                for item in decision.results
            ],
        }
        runtime.audit_log.append({"action": "identity.verify", "subject_id": request.subject_id, "authorized": decision.authorized, "timestamp": datetime.now(UTC).isoformat()})
        return result

    @app.get("/api/v1/models", tags=["management"])
    def models() -> list[dict[str, object]]:
        return [
            {"id": "rf-baseline", "type": "statistical", "state": "available"},
            {"id": "isolation-forest", "type": "anomaly", "state": "available"},
            {"id": "dbscan", "type": "clustering", "state": "available"},
            {"id": "temporal-correlation", "type": "correlation", "state": "available"},
        ]

    @app.get("/api/v1/settings", tags=["management"])
    def get_settings() -> dict[str, object]:
        return dict(runtime.settings)

    @app.patch("/api/v1/settings", tags=["management"])
    def patch_settings(patch: SettingsPatch) -> dict[str, object]:
        changes = patch.model_dump(exclude_none=True)
        runtime.settings.update(changes)
        runtime.audit_log.append({"action": "settings.update", "keys": sorted(changes), "timestamp": datetime.now(UTC).isoformat()})
        return dict(runtime.settings)

    @app.get("/api/v1/privacy/policies", tags=["privacy"])
    def privacy_policies() -> list[dict[str, object]]:
        policies = []
        for policy in runtime.privacy.policies():
            policies.append({
                "domain": policy.domain.value, "days": policy.days, "sensitivity": policy.sensitivity.value,
                "deletion_supported": policy.deletion_supported, "purpose": policy.purpose,
            })
        return policies

    @app.get("/api/v1/privacy/retention/{domain}", tags=["privacy"])
    def retention_decision(domain: DataDomain, created_at: datetime) -> dict[str, object]:
        try:
            decision = runtime.privacy.decision(domain, created_at)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        return {"delete": decision.delete, "reason": decision.reason, "expires_at": decision.expires_at.isoformat()}

    @app.get("/api/v1/security/status", tags=["security"])
    def security_status() -> dict[str, object]:
        return {
            "api_key_configured": api_key is not None,
            "websocket_auth_required": api_key is not None,
            "scan_scope": runtime.settings.get("scan_scope"),
            "ledger_verified": runtime.age.status()["valid"],
            "security_headers": True,
            "external_anchoring_automatic": False,
        }

    @app.get("/api/v1/audit", tags=["security"])
    def audit_log(limit: int = 100) -> list[dict[str, object]]:
        if not 1 <= limit <= 500:
            raise HTTPException(422, "invalid limit")
        return runtime.audit_log[-limit:]

    @app.get("/api/v1/incidents/{incident_id}", tags=["incidents"])
    def incident_detail(incident_id: str) -> dict[str, object]:
        for incident in runtime.incidents:
            if str(incident.get("incident_id") or incident.get("id")) == incident_id:
                return incident
        raise HTTPException(404, "incident not found")

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    @app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
    @app.get("/live", response_class=HTMLResponse, include_in_schema=False)
    @app.get("/spectrum", response_class=HTMLResponse, include_in_schema=False)
    @app.get("/scan", response_class=HTMLResponse, include_in_schema=False)
    @app.get("/incidents", response_class=HTMLResponse, include_in_schema=False)
    @app.get("/incidents/view", response_class=HTMLResponse, include_in_schema=False)
    @app.get("/timeline", response_class=HTMLResponse, include_in_schema=False)
    @app.get("/verification", response_class=HTMLResponse, include_in_schema=False)
    @app.get("/age", response_class=HTMLResponse, include_in_schema=False)
    @app.get("/alerts/view", response_class=HTMLResponse, include_in_schema=False)
    @app.get("/settings", response_class=HTMLResponse, include_in_schema=False)
    def dashboard() -> HTMLResponse:
        path = Path(__file__).resolve().parents[1] / "dashboard" / "index.html"
        return HTMLResponse(path.read_text(encoding="utf-8"))

    async def websocket_stream(websocket: WebSocket, channel: str) -> None:
        if api_key is not None:
            candidate = websocket.headers.get("x-truepass-api-key") or websocket.query_params.get("api_key")
            if candidate is None or not constant_time_secret_matches(candidate, api_key):
                await websocket.close(code=1008, reason="authentication required")
                return
        await websocket.accept()
        try:
            async with runtime.hub.subscribe(channel) as queue:
                await websocket.send_json({"type": "connected", "channel": channel})
                while True:
                    try:
                        payload = await asyncio.wait_for(queue.get(), timeout=20.0)
                        await websocket.send_json({"type": "data", "channel": channel, "data": payload})
                    except TimeoutError:
                        await websocket.send_json({"type": "heartbeat", "channel": channel})
        except WebSocketDisconnect:
            return

    @app.websocket("/ws/events")
    async def ws_events(websocket: WebSocket) -> None:
        await websocket_stream(websocket, "events")

    @app.websocket("/ws/spectrum")
    async def ws_spectrum(websocket: WebSocket) -> None:
        await websocket_stream(websocket, "spectrum")

    @app.websocket("/ws/incidents")
    async def ws_incidents(websocket: WebSocket) -> None:
        await websocket_stream(websocket, "incidents")

    @app.websocket("/ws/alerts")
    async def ws_alerts(websocket: WebSocket) -> None:
        await websocket_stream(websocket, "alerts")

    @app.websocket("/ws/system")
    async def ws_system(websocket: WebSocket) -> None:
        await websocket_stream(websocket, "system")

    return app


app = create_app(api_key=os.getenv("TRUEPASS_API_KEY"))
