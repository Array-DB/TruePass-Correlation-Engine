"""Authorized passive host observation sessions for TruePass-Scan.

This module deliberately performs no active port probing or remote exploitation. A scan
session snapshots telemetry already available from the local/authorized host collectors.
"""
from __future__ import annotations

import socket
import time
from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4

from truepass.collectors.host import HostTelemetryCollector, HostTelemetrySnapshot


@dataclass(slots=True)
class ScanSession:
    session_id: str
    host: str
    created_ns: int
    authorization_acknowledged: bool
    scope: str
    status: str = "active"
    stopped_ns: int | None = None
    baseline: dict[str, Any] | None = None
    latest: dict[str, Any] | None = None

    def summary(self) -> dict[str, Any]:
        latest = self.latest or {}
        network = latest.get("network", {}) if isinstance(latest, dict) else {}
        return {
            "session_id": self.session_id,
            "host": self.host,
            "created_ns": self.created_ns,
            "authorization_acknowledged": self.authorization_acknowledged,
            "scope": self.scope,
            "status": self.status,
            "stopped_ns": self.stopped_ns,
            "process_count": len(latest.get("processes", [])) if isinstance(latest, dict) else 0,
            "socket_count": len(network.get("sockets", [])) if isinstance(network, dict) else 0,
            "interface_count": len(network.get("interfaces", [])) if isinstance(network, dict) else 0,
        }


@dataclass(slots=True)
class ScanService:
    """Manage in-memory passive observation sessions for one TruePass runtime."""

    sessions: dict[str, ScanSession] = field(default_factory=dict)

    def start(self, *, authorization_acknowledged: bool, scope: str = "local-host") -> ScanSession:
        if not authorization_acknowledged:
            raise ValueError("authorization acknowledgement is required")
        if scope != "local-host":
            raise ValueError("this build supports passive local-host scope only")
        host = socket.gethostname()
        session = ScanSession(
            session_id=str(uuid4()),
            host=host,
            created_ns=time.time_ns(),
            authorization_acknowledged=True,
            scope=scope,
        )
        self.sessions[session.session_id] = session
        self.refresh(session.session_id, establish_baseline=True)
        return session

    def get(self, session_id: str) -> ScanSession:
        try:
            return self.sessions[session_id]
        except KeyError as exc:
            raise KeyError("scan session not found") from exc

    def stop(self, session_id: str) -> ScanSession:
        session = self.get(session_id)
        session.status = "stopped"
        session.stopped_ns = time.time_ns()
        return session

    def refresh(self, session_id: str, *, establish_baseline: bool = False) -> dict[str, Any]:
        session = self.get(session_id)
        snapshot = HostTelemetryCollector(host=session.host).snapshot().as_dict()
        if establish_baseline or session.baseline is None:
            session.baseline = snapshot
        session.latest = snapshot
        return snapshot

    def hosts(self, session_id: str) -> list[dict[str, Any]]:
        session = self.get(session_id)
        latest = self._latest(session)
        return [{"host": session.host, "scope": session.scope, "local": True,
                 "process_count": len(latest.get("processes", []))}]

    def ports(self, session_id: str) -> list[dict[str, Any]]:
        latest = self._latest(self.get(session_id))
        network = latest.get("network", {})
        sockets = network.get("sockets", []) if isinstance(network, dict) else []
        return [item for item in sockets if str(item.get("status", "")).upper() == "LISTEN"]

    def processes(self, session_id: str) -> list[dict[str, Any]]:
        latest = self._latest(self.get(session_id))
        return list(latest.get("processes", []))

    def connections(self, session_id: str) -> list[dict[str, Any]]:
        latest = self._latest(self.get(session_id))
        network = latest.get("network", {})
        return list(network.get("sockets", [])) if isinstance(network, dict) else []

    def devices(self, session_id: str) -> dict[str, Any]:
        latest = self._latest(self.get(session_id))
        return {
            "interfaces": latest.get("network", {}).get("interfaces", []),
            "wifi": latest.get("wifi", {}),
            "bluetooth": latest.get("bluetooth", {}),
        }

    def diff(self, session_id: str) -> dict[str, Any]:
        session = self.get(session_id)
        baseline = session.baseline or {}
        latest = self._latest(session)
        return {
            "processes": _keyed_diff(baseline.get("processes", []), latest.get("processes", []), "pid"),
            "sockets": _record_diff(
                baseline.get("network", {}).get("sockets", []),
                latest.get("network", {}).get("sockets", []),
            ),
            "interfaces_changed": baseline.get("network", {}).get("interfaces", [])
            != latest.get("network", {}).get("interfaces", []),
            "wifi_changed": baseline.get("wifi") != latest.get("wifi"),
            "bluetooth_changed": baseline.get("bluetooth") != latest.get("bluetooth"),
        }

    def report(self, session_id: str) -> dict[str, Any]:
        session = self.get(session_id)
        return {"session": session.summary(), "inventory": self._latest(session), "diff": self.diff(session_id)}

    @staticmethod
    def _latest(session: ScanSession) -> dict[str, Any]:
        if session.latest is None:
            return {}
        return session.latest


def _keyed_diff(before: list[dict[str, Any]], after: list[dict[str, Any]], key: str) -> dict[str, Any]:
    left = {item.get(key): item for item in before}
    right = {item.get(key): item for item in after}
    added_keys = sorted(set(right) - set(left), key=lambda value: str(value))
    removed_keys = sorted(set(left) - set(right), key=lambda value: str(value))
    changed_keys = sorted(
        (value for value in set(left) & set(right) if left[value] != right[value]),
        key=lambda value: str(value),
    )
    return {
        "added": [right[value] for value in added_keys],
        "removed": [left[value] for value in removed_keys],
        "changed": [{"before": left[value], "after": right[value]} for value in changed_keys],
    }


def _record_diff(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> dict[str, Any]:
    def frozen(item: dict[str, Any]) -> tuple[tuple[str, str], ...]:
        return tuple(sorted((str(k), repr(v)) for k, v in item.items()))
    left = {frozen(item): item for item in before}
    right = {frozen(item): item for item in after}
    return {
        "added": [right[key] for key in sorted(set(right) - set(left))],
        "removed": [left[key] for key in sorted(set(left) - set(right))],
    }
