"""Unified read-only host telemetry snapshot."""

from __future__ import annotations

import socket
from dataclasses import asdict, dataclass

from truepass.collectors.bluetooth import BluetoothCollector, BluetoothState
from truepass.collectors.network import NetworkCollector, NetworkInventory
from truepass.collectors.processes import ProcessCollector, ProcessSnapshot
from truepass.collectors.wifi import WiFiCollector, WiFiState


@dataclass(frozen=True, slots=True)
class HostTelemetrySnapshot:
    host: str
    processes: tuple[ProcessSnapshot, ...]
    network: NetworkInventory
    wifi: WiFiState
    bluetooth: BluetoothState

    def as_dict(self) -> dict[str, object]:
        return {
            "host": self.host,
            "processes": [asdict(value) for value in self.processes],
            "network": {
                "sockets": [asdict(value) for value in self.network.sockets],
                "interfaces": [asdict(value) for value in self.network.interfaces],
            },
            "wifi": asdict(self.wifi),
            "bluetooth": asdict(self.bluetooth),
        }


class HostTelemetryCollector:
    """Aggregate existing passive collectors into one point-in-time inventory."""

    def __init__(self, *, host: str | None = None) -> None:
        self.host = host or socket.gethostname()
        self.processes = ProcessCollector(host=self.host)
        self.network = NetworkCollector(host=self.host)
        self.wifi = WiFiCollector(host=self.host)
        self.bluetooth = BluetoothCollector(host=self.host)

    def snapshot(self) -> HostTelemetrySnapshot:
        processes = tuple(sorted(self.processes.snapshot().values(), key=lambda item: item.pid))
        return HostTelemetrySnapshot(
            host=self.host,
            processes=processes,
            network=self.network.inventory(),
            wifi=self.wifi.snapshot(),
            bluetooth=self.bluetooth.snapshot(),
        )
