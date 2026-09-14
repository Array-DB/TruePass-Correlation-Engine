"""Read-only local process telemetry and snapshot change detection."""

from __future__ import annotations

import platform
import socket
import time
from dataclasses import dataclass
from typing import Any

import psutil

from truepass.models.events import Event, EventSource, EventType, Provenance, Severity
from truepass.monitoring.metrics import COLLECTOR_ERRORS_TOTAL, EVENTS_TOTAL


@dataclass(frozen=True, slots=True)
class ProcessSnapshot:
    pid: int
    ppid: int | None
    name: str | None
    executable: str | None
    username: str | None
    create_time_ns: int | None
    cpu_percent: float | None
    memory_rss: int | None
    command_line: tuple[str, ...] | None
    sockets: tuple[dict[str, Any], ...]


class ProcessCollector:
    """Collect local process state without modifying the monitored host."""

    def __init__(
        self,
        *,
        sensor_id: str = "process-local",
        include_command_line: bool = False,
        include_sockets: bool = True,
        host: str | None = None,
    ) -> None:
        self.sensor_id = sensor_id
        self.include_command_line = include_command_line
        self.include_sockets = include_sockets
        self.host = host or socket.gethostname()
        self._previous: dict[int, ProcessSnapshot] | None = None

    def snapshot(self) -> dict[int, ProcessSnapshot]:
        result: dict[int, ProcessSnapshot] = {}
        attrs = ["pid", "ppid", "name", "exe", "username", "create_time", "cpu_percent", "memory_info"]
        if self.include_command_line:
            attrs.append("cmdline")

        for proc in psutil.process_iter(attrs=attrs, ad_value=None):
            try:
                info = proc.info
                memory = info.get("memory_info")
                command_line: tuple[str, ...] | None = None
                if self.include_command_line:
                    raw_cmdline = info.get("cmdline")
                    if isinstance(raw_cmdline, list):
                        command_line = tuple(str(part) for part in raw_cmdline)
                sockets = self._collect_sockets(proc) if self.include_sockets else ()
                create_time = info.get("create_time")
                result[proc.pid] = ProcessSnapshot(
                    pid=proc.pid,
                    ppid=_as_int_or_none(info.get("ppid")),
                    name=_as_str_or_none(info.get("name")),
                    executable=_as_str_or_none(info.get("exe")),
                    username=_as_str_or_none(info.get("username")),
                    create_time_ns=int(float(create_time) * 1_000_000_000) if create_time else None,
                    cpu_percent=_as_float_or_none(info.get("cpu_percent")),
                    memory_rss=int(memory.rss) if memory is not None else None,
                    command_line=command_line,
                    sockets=sockets,
                )
            except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess) as exc:
                COLLECTOR_ERRORS_TOTAL.labels("processes", type(exc).__name__).inc()
                continue
        return result

    def poll(self) -> list[Event]:
        """Return normalized start/stop events since the previous snapshot.

        The first call establishes a baseline and emits no historical start events.
        """

        current = self.snapshot()
        if self._previous is None:
            self._previous = current
            return []

        previous = self._previous
        self._previous = current
        events: list[Event] = []

        for pid in sorted(current.keys() - previous.keys()):
            event = self._event_from_snapshot(EventType.PROCESS_STARTED, current[pid])
            EVENTS_TOTAL.labels(event.source.value, event.event_type.value).inc()
            events.append(event)

        for pid in sorted(previous.keys() - current.keys()):
            event = self._event_from_snapshot(EventType.PROCESS_STOPPED, previous[pid])
            EVENTS_TOTAL.labels(event.source.value, event.event_type.value).inc()
            events.append(event)

        return events

    def _event_from_snapshot(self, event_type: EventType, snapshot: ProcessSnapshot) -> Event:
        features: dict[str, Any] = {
            "pid": snapshot.pid,
            "ppid": snapshot.ppid,
            "name": snapshot.name,
            "executable": snapshot.executable,
            "username": snapshot.username,
            "process_create_time_ns": snapshot.create_time_ns,
            "cpu_percent": snapshot.cpu_percent,
            "memory_rss": snapshot.memory_rss,
            "socket_count": len(snapshot.sockets),
            "sockets": list(snapshot.sockets),
        }
        if self.include_command_line and snapshot.command_line is not None:
            features["command_line"] = list(snapshot.command_line)

        return Event(
            timestamp_ns=time.time_ns(),
            received_timestamp_ns=time.time_ns(),
            source=EventSource.PROCESS,
            sensor_id=self.sensor_id,
            host=self.host,
            event_type=event_type,
            severity=Severity.INFO,
            confidence=1.0,
            features=features,
            metadata={"read_only": True},
            provenance=Provenance(
                collector="processes",
                method="psutil.process_iter",
                platform=platform.platform(),
            ),
        )

    @staticmethod
    def _collect_sockets(proc: psutil.Process) -> tuple[dict[str, Any], ...]:
        sockets: list[dict[str, Any]] = []
        try:
            connections = proc.net_connections(kind="inet")
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            return ()
        for connection in connections:
            local = _address_to_dict(connection.laddr)
            remote = _address_to_dict(connection.raddr)
            sockets.append(
                {
                    "family": int(connection.family),
                    "type": int(connection.type),
                    "local": local,
                    "remote": remote,
                    "status": connection.status,
                }
            )
        return tuple(sockets)


def _address_to_dict(address: Any) -> dict[str, Any] | None:
    if not address:
        return None
    ip = getattr(address, "ip", None)
    port = getattr(address, "port", None)
    if ip is None and isinstance(address, tuple) and len(address) >= 2:
        ip, port = address[0], address[1]
    return {"ip": str(ip), "port": int(port)}


def _as_int_or_none(value: Any) -> int | None:
    return int(value) if value is not None else None


def _as_float_or_none(value: Any) -> float | None:
    return float(value) if value is not None else None


def _as_str_or_none(value: Any) -> str | None:
    return str(value) if value not in (None, "") else None
