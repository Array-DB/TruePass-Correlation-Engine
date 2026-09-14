from __future__ import annotations

from truepass.collectors.host import HostTelemetryCollector
from truepass.collectors.network import NetworkInterfaceSnapshot, NetworkInventory
from truepass.collectors.wifi import WiFiState
from truepass.collectors.bluetooth import BluetoothState


def test_host_snapshot_aggregates_collectors(monkeypatch) -> None:
    collector = HostTelemetryCollector(host="test-host")
    monkeypatch.setattr(collector.processes, "snapshot", lambda: {})
    monkeypatch.setattr(
        collector.network,
        "inventory",
        lambda: NetworkInventory((), (NetworkInterfaceSnapshot("lo", True, 65536, 0, ("127.0.0.1",)),)),
    )
    monkeypatch.setattr(collector.wifi, "snapshot", lambda: WiFiState())
    monkeypatch.setattr(collector.bluetooth, "snapshot", lambda: BluetoothState())
    payload = collector.snapshot().as_dict()
    assert payload["host"] == "test-host"
    assert payload["network"]["interfaces"][0]["name"] == "lo"
