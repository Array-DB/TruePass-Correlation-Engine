"""Background passive telemetry orchestration for the local TruePass runtime.

The service starts the existing read-only collectors when the API starts and emits
small host-state observations at a fixed cadence so the operator UI reflects real
machine activity even when no process/socket transition happens during a window.
"""
from __future__ import annotations

import asyncio
import platform
import socket
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Awaitable, Callable

import psutil

from truepass.collectors.bluetooth import BluetoothCollector
from truepass.collectors.network import NetworkCollector
from truepass.collectors.processes import ProcessCollector
from truepass.collectors.wifi import WiFiCollector
from truepass.config import AppSettings
from truepass.models.events import Event, EventSource, EventType, Provenance, Severity

PublishEvent = Callable[[Event], Awaitable[None]]


@dataclass(slots=True)
class CollectorStatus:
    name: str
    sensor_id: str
    running: bool = False
    last_poll_ns: int | None = None
    last_event_ns: int | None = None
    events_emitted: int = 0
    errors: int = 0
    last_error: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "sensor_id": self.sensor_id,
            "running": self.running,
            "last_poll_ns": self.last_poll_ns,
            "last_event_ns": self.last_event_ns,
            "events_emitted": self.events_emitted,
            "errors": self.errors,
            "last_error": self.last_error,
        }


@dataclass(slots=True)
class TelemetryService:
    settings: AppSettings
    publish_event: PublishEvent
    host_interval_seconds: float = 2.0
    _tasks: list[asyncio.Task[None]] = field(default_factory=list)
    _stopping: asyncio.Event = field(default_factory=asyncio.Event)
    _statuses: dict[str, CollectorStatus] = field(default_factory=dict)
    _history: deque[dict[str, object]] = field(default_factory=lambda: deque(maxlen=180))

    async def start(self) -> None:
        if self._tasks:
            return
        self._stopping.clear()
        p = self.settings.process_collector
        n = self.settings.network_collector
        w = self.settings.wifi_collector
        b = self.settings.bluetooth_collector
        collectors = [
            ("process", ProcessCollector(sensor_id=p.sensor_id, include_command_line=p.include_command_line, include_sockets=p.include_sockets), p.interval_seconds),
            ("network", NetworkCollector(sensor_id=n.sensor_id), n.interval_seconds),
            ("wifi", WiFiCollector(sensor_id=w.sensor_id), w.interval_seconds),
            ("bluetooth", BluetoothCollector(sensor_id=b.sensor_id), b.interval_seconds),
        ]
        for name, collector, interval in collectors:
            sensor_id = str(getattr(collector, "sensor_id", name))
            self._statuses[name] = CollectorStatus(name=name, sensor_id=sensor_id, running=True)
            # Prime change-detection baselines before entering the loop.
            try:
                await asyncio.to_thread(collector.poll)
                self._statuses[name].last_poll_ns = time.time_ns()
            except Exception as exc:  # collectors are best-effort and should not kill the API
                status = self._statuses[name]
                status.errors += 1
                status.last_error = f"{type(exc).__name__}: {exc}"
            self._tasks.append(asyncio.create_task(self._collector_loop(name, collector, float(interval)), name=f"truepass-{name}-collector"))
        self._statuses["host"] = CollectorStatus(name="host", sensor_id="host-local", running=True)
        self._tasks.append(asyncio.create_task(self._host_loop(), name="truepass-host-telemetry"))

    async def stop(self) -> None:
        self._stopping.set()
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        for status in self._statuses.values():
            status.running = False

    def status(self) -> dict[str, object]:
        return {
            "running": bool(self._tasks) and not self._stopping.is_set(),
            "collectors": [self._statuses[key].as_dict() for key in sorted(self._statuses)],
            "latest_host": self._history[-1] if self._history else None,
            "host_history": list(self._history),
        }

    async def _collector_loop(self, name: str, collector: object, interval: float) -> None:
        status = self._statuses[name]
        while not self._stopping.is_set():
            try:
                await asyncio.sleep(interval)
                events = await asyncio.to_thread(getattr(collector, "poll"))
                now = time.time_ns()
                status.last_poll_ns = now
                status.last_error = None
                for event in events:
                    await self.publish_event(event)
                    status.events_emitted += 1
                    status.last_event_ns = event.timestamp_ns
            except asyncio.CancelledError:
                break
            except Exception as exc:
                status.errors += 1
                status.last_error = f"{type(exc).__name__}: {exc}"
                await asyncio.sleep(min(5.0, max(0.5, interval)))
        status.running = False

    async def _host_loop(self) -> None:
        status = self._statuses["host"]
        # Prime CPU counters so subsequent cpu_percent readings are meaningful.
        await asyncio.to_thread(psutil.cpu_percent, None)
        last_net = psutil.net_io_counters()
        last_time = time.monotonic()
        while not self._stopping.is_set():
            try:
                await asyncio.sleep(self.host_interval_seconds)
                now_ns = time.time_ns()
                now_mono = time.monotonic()
                elapsed = max(0.001, now_mono - last_time)
                cpu = await asyncio.to_thread(psutil.cpu_percent, None)
                memory = psutil.virtual_memory()
                swap = psutil.swap_memory()
                disk = psutil.disk_usage("/")
                net = psutil.net_io_counters()
                process_count = len(psutil.pids())
                try:
                    connections = len(psutil.net_connections(kind="inet"))
                except (psutil.AccessDenied, PermissionError):
                    connections = -1
                rx_rate = max(0.0, (net.bytes_recv - last_net.bytes_recv) / elapsed)
                tx_rate = max(0.0, (net.bytes_sent - last_net.bytes_sent) / elapsed)
                sample: dict[str, object] = {
                    "timestamp_ns": now_ns,
                    "cpu_percent": float(cpu),
                    "memory_percent": float(memory.percent),
                    "memory_used": int(memory.used),
                    "memory_total": int(memory.total),
                    "swap_percent": float(swap.percent),
                    "disk_percent": float(disk.percent),
                    "network_rx_bytes_per_sec": float(rx_rate),
                    "network_tx_bytes_per_sec": float(tx_rate),
                    "process_count": int(process_count),
                    "connection_count": int(connections),
                }
                self._history.append(sample)
                event = Event(
                    timestamp_ns=now_ns,
                    received_timestamp_ns=time.time_ns(),
                    source=EventSource.SYSTEM,
                    sensor_id="host-local",
                    host=socket.gethostname(),
                    event_type=EventType.HOST_SNAPSHOT,
                    severity=Severity.INFO,
                    confidence=1.0,
                    features=sample,
                    metadata={"read_only": True, "periodic": True},
                    provenance=Provenance(
                        collector="host-telemetry",
                        method="psutil",
                        platform=platform.platform(),
                    ),
                )
                await self.publish_event(event)
                status.last_poll_ns = now_ns
                status.last_event_ns = now_ns
                status.events_emitted += 1
                status.last_error = None
                last_net = net
                last_time = now_mono
            except asyncio.CancelledError:
                break
            except Exception as exc:
                status.errors += 1
                status.last_error = f"{type(exc).__name__}: {exc}"
                await asyncio.sleep(1.0)
        status.running = False
