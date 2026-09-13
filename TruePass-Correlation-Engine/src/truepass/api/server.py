"""FastAPI service for TruePass operator and integration workflows."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from truepass.api.dependencies import api_key_dependency
from truepass.api.state import RuntimeState
from truepass.alerting import AlertEngine, DEFAULT_RULES
from truepass.correlation.engine import TemporalCorrelationEngine
from truepass.eventspace.timeline import Timeline
from truepass.models.events import Event, EventSource, EventType


def create_app(state: RuntimeState | None = None, *, api_key: str | None = None) -> FastAPI:
    runtime = state or RuntimeState()
    dependencies = [Depends(api_key_dependency(api_key))]
    app = FastAPI(title="TruePass API", version="1.0.0", description="Defensive telemetry, correlation, and evidence API", dependencies=dependencies)
    app.state.truepass = runtime

    @app.get("/health", tags=["system"])
    def health() -> dict[str, object]:
        return {"status": "ok", "events": len(runtime.events), "ledger_verified": runtime.ledger_verified}

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> PlainTextResponse:
        return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)

    @app.post("/events", response_model=Event, status_code=201, tags=["events"])
    def create_event(event: Event) -> Event:
        runtime.add_event(event)
        return event

    @app.get("/events", response_model=list[Event], tags=["events"])
    def list_events(
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=500)] = 100,
        source: EventSource | None = None,
        event_type: EventType | None = None,
    ) -> list[Event]:
        items = runtime.events
        if source is not None:
            items = [e for e in items if e.source == source]
        if event_type is not None:
            items = [e for e in items if e.event_type == event_type]
        return items[offset : offset + limit]

    @app.get("/events/{event_id}", response_model=Event, tags=["events"])
    def get_event(event_id: str) -> Event:
        for event in runtime.events:
            if str(event.event_id) == event_id:
                return event
        raise HTTPException(404, "event not found")

    @app.get("/incidents", tags=["incidents"])
    def incidents(offset: int = 0, limit: int = 100) -> list[dict[str, object]]:
        if offset < 0 or not 1 <= limit <= 500:
            raise HTTPException(422, "invalid pagination")
        return runtime.incidents[offset : offset + limit]

    @app.get("/sensors", tags=["sensors"])
    def sensors() -> list[dict[str, object]]:
        return sorted(runtime.sensors.values(), key=lambda item: str(item["sensor_id"]))

    @app.get("/timeline/{event_id}", tags=["timeline"])
    def timeline(event_id: str, before_ms: float = 500.0, after_ms: float = 500.0) -> list[Event]:
        timeline = Timeline(runtime.events)
        try:
            return list(timeline.around(UUID(event_id), before_ms=before_ms, after_ms=after_ms))
        except (KeyError, ValueError) as exc:
            raise HTTPException(404 if isinstance(exc, KeyError) else 422, str(exc)) from exc

    @app.get("/correlation/{event_id}", tags=["correlation"])
    def correlation(event_id: str, window_ms: float = 500.0) -> dict[str, object]:
        anchor = next((e for e in runtime.events if str(e.event_id) == event_id), None)
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
            "reasons": [r.__dict__ if hasattr(r, "__dict__") else {"code": r.code, "weight": r.weight, "contribution": r.contribution, "detail": r.detail} for r in result.reasons],
            "causation_established": False,
        }

    @app.get("/evidence", tags=["evidence"])
    def evidence() -> dict[str, object]:
        return {"ledger_verified": runtime.ledger_verified, "event_count": len(runtime.events)}

    @app.get("/baselines", tags=["baselines"])
    def baselines() -> list[dict[str, object]]:
        return []

    @app.post("/similarity", tags=["similarity"])
    def similarity(vector: list[float], limit: int = 5) -> list[dict[str, object]]:
        try:
            hits = runtime.vector_index.search(vector, limit=limit)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        return [{"item_id": h.item_id, "similarity": h.similarity} for h in hits]

    @app.get("/system", tags=["system"])
    def system() -> dict[str, object]:
        return {
            "api": "healthy",
            "event_count": len(runtime.events),
            "sensor_count": len(runtime.sensors),
            "incident_count": len(runtime.incidents),
            "ledger": "verified" if runtime.ledger_verified else "failed",
        }

    @app.get("/alerts", tags=["alerts"])
    def alerts(limit: int = 100) -> list[dict[str, object]]:
        if not 1 <= limit <= 500:
            raise HTTPException(422, "invalid limit")
        engine = AlertEngine(DEFAULT_RULES)
        output: list[dict[str, object]] = []
        for event in runtime.events:
            for alert in engine.evaluate(event):
                output.append({
                    "alert_id": alert.alert_id,
                    "rule_id": alert.rule_id,
                    "event_id": alert.event_id,
                    "severity": alert.severity.value,
                    "reason": alert.reason,
                    "created_ns": alert.created_ns,
                })
        return output[-limit:]

    @app.get("/dashboard/summary", tags=["dashboard"])
    def dashboard_summary() -> dict[str, object]:
        anomaly_count = sum(1 for e in runtime.events if e.event_type == EventType.RF_ANOMALY)
        return {
            "health": "healthy" if runtime.ledger_verified else "degraded",
            "events": len(runtime.events),
            "sensors": len(runtime.sensors),
            "incidents": len(runtime.incidents),
            "rf_anomalies": anomaly_count,
            "ledger_verified": runtime.ledger_verified,
            "recent_events": [e.model_dump(mode="json") for e in runtime.events[-20:]],
        }

    @app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
    def dashboard() -> HTMLResponse:
        path = Path(__file__).resolve().parents[1] / "dashboard" / "index.html"
        return HTMLResponse(path.read_text(encoding="utf-8"))

    return app


app = create_app(api_key=os.getenv("TRUEPASS_API_KEY"))
