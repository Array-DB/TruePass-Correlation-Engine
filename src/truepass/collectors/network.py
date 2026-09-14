"""Passive local network, interface, and listening-port telemetry."""

from __future__ import annotations

import platform
import socket
import time
from dataclasses import asdict, dataclass
from typing import Any

import psutil

from truepass.models.events import Event, EventSource, EventType, Provenance, Severity
from truepass.monitoring.metrics import COLLECTOR_ERRORS_TOTAL, EVENTS_TOTAL


@dataclass(frozen=True, slots=True)
class NetworkSocketSnapshot:
    family: int
    type: int
    local_ip: str
    local_port: int
    remote_ip: str | None
    remote_port: int | None
    status: str
    pid: int | None
    process_name: str | None = None


@dataclass(frozen=True, slots=True)
class NetworkInterfaceSnapshot:
    name: str
    is_up: bool
    mtu: int
    speed_mbps: int
    addresses: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NetworkInventory:
    sockets: tuple[NetworkSocketSnapshot, ...]
    interfaces: tuple[NetworkInterfaceSnapshot, ...]


class NetworkCollector:
    """Observe local sockets and interfaces without active scanning."""

    def __init__(self, *, sensor_id: str = "network-local", host: str | None = None) -> None:
        self.sensor_id = sensor_id
        self.host = host or socket.gethostname()
        self._previous: set[NetworkSocketSnapshot] | None = None
        self._previous_interfaces: tuple[NetworkInterfaceSnapshot, ...] | None = None

    def snapshot(self) -> set[NetworkSocketSnapshot]:
        out: set[NetworkSocketSnapshot] = set()
        try:
            connections = psutil.net_connections(kind="inet")
        except (psutil.AccessDenied, OSError) as exc:
            COLLECTOR_ERRORS_TOTAL.labels("network", type(exc).__name__).inc()
            return out

        process_names: dict[int, str | None] = {}
        for connection in connections:
            if not connection.laddr:
                continue
            local_ip, local_port = _addr(connection.laddr)
            remote_ip, remote_port = _addr(connection.raddr) if connection.raddr else (None, None)
            process_name: str | None = None
            if connection.pid is not None:
                if connection.pid not in process_names:
                    try:
                        process_names[connection.pid] = psutil.Process(connection.pid).name()
                    except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
                        process_names[connection.pid] = None
                process_name = process_names[connection.pid]
            out.add(
                NetworkSocketSnapshot(
                    int(connection.family),
                    int(connection.type),
                    local_ip,
                    int(local_port),
                    remote_ip,
                    remote_port,
                    connection.status or "NONE",
                    connection.pid,
                    process_name,
                )
            )
        return out

    def snapshot_interfaces(self) -> tuple[NetworkInterfaceSnapshot, ...]:
        addresses = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        result: list[NetworkInterfaceSnapshot] = []
        for name in sorted(set(addresses) | set(stats)):
            stat = stats.get(name)
            address_values = tuple(
                sorted(
                    str(item.address)
                    for item in addresses.get(name, ())
                    if getattr(item, "address", None)
                )
            )
            result.append(
                NetworkInterfaceSnapshot(
                    name=name,
                    is_up=bool(stat.isup) if stat is not None else False,
                    mtu=int(stat.mtu) if stat is not None else 0,
                    speed_mbps=int(stat.speed) if stat is not None else 0,
                    addresses=address_values,
                )
            )
        return tuple(result)

    def inventory(self) -> NetworkInventory:
        return NetworkInventory(
            sockets=tuple(sorted(self.snapshot(), key=_socket_sort_key)),
            interfaces=self.snapshot_interfaces(),
        )

    def poll(self) -> list[Event]:
        current = self.snapshot()
        current_interfaces = self.snapshot_interfaces()
        if self._previous is None:
            self._previous = current
            self._previous_interfaces = current_interfaces
            return []

        previous = self._previous
        previous_interfaces = self._previous_interfaces or ()
        self._previous = current
        self._previous_interfaces = current_interfaces
        events: list[Event] = []

        for item in sorted(current - previous, key=_socket_sort_key):
            events.append(self._socket_event(item, change="opened"))
        for item in sorted(previous - current, key=_socket_sort_key):
            events.append(self._socket_event(item, change="closed"))

        if current_interfaces != previous_interfaces:
            event = Event(
                timestamp_ns=time.time_ns(),
                received_timestamp_ns=time.time_ns(),
                source=EventSource.NETWORK,
                sensor_id=self.sensor_id,
                host=self.host,
                event_type=EventType.NETWORK_CONNECTION,
                severity=Severity.INFO,
                confidence=1.0,
                features={
                    "kind": "interface_state_change",
                    "previous": [asdict(value) for value in previous_interfaces],
                    "current": [asdict(value) for value in current_interfaces],
                    "passive": True,
                },
                metadata={"authorized_local_observation": True},
                provenance=Provenance(
                    collector="network",
                    method="psutil.net_if_addrs/net_if_stats",
                    platform=platform.platform(),
                ),
            )
            EVENTS_TOTAL.labels(event.source.value, event.event_type.value).inc()
            events.append(event)
        return events

    def _socket_event(self, snapshot: NetworkSocketSnapshot, *, change: str) -> Event:
        listening = snapshot.status.upper() == "LISTEN"
        event = Event(
            timestamp_ns=time.time_ns(),
            received_timestamp_ns=time.time_ns(),
            source=EventSource.NETWORK,
            sensor_id=self.sensor_id,
            host=self.host,
            event_type=EventType.LISTENING_PORT if listening else EventType.NETWORK_CONNECTION,
            severity=Severity.INFO,
            confidence=1.0,
            features={
                "kind": "socket",
                "change": change,
                "family": snapshot.family,
                "socket_type": snapshot.type,
                "local_ip": snapshot.local_ip,
                "local_port": snapshot.local_port,
                "remote_ip": snapshot.remote_ip,
                "remote_port": snapshot.remote_port,
                "status": snapshot.status,
                "pid": snapshot.pid,
                "process_name": snapshot.process_name,
                "passive": True,
            },
            metadata={"authorized_local_observation": True},
            provenance=Provenance(
                collector="network",
                method="psutil.net_connections",
                platform=platform.platform(),
            ),
        )
        EVENTS_TOTAL.labels(event.source.value, event.event_type.value).inc()
        return event


def _socket_sort_key(value: NetworkSocketSnapshot) -> tuple[object, ...]:
    return (
        value.local_port,
        value.pid or -1,
        value.remote_ip or "",
        value.remote_port or -1,
        value.status,
    )


def _addr(address: Any) -> tuple[str, int]:
    return str(getattr(address, "ip", address[0])), int(getattr(address, "port", address[1]))
