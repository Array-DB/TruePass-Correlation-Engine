import asyncio

from truepass.config import AppSettings
from truepass.models.events import EventType
from truepass.runtime.telemetry import TelemetryService


def test_background_telemetry_emits_real_host_observations() -> None:
    async def scenario() -> None:
        settings = AppSettings()
        settings.process_collector.interval_seconds = 3600
        settings.network_collector.interval_seconds = 3600
        settings.wifi_collector.interval_seconds = 3600
        settings.bluetooth_collector.interval_seconds = 3600
        events = []

        async def publish(event):
            events.append(event)

        service = TelemetryService(settings=settings, publish_event=publish, host_interval_seconds=0.05)
        await service.start()
        try:
            await asyncio.sleep(0.14)
            status = service.status()
            assert status["running"] is True
            assert status["latest_host"] is not None
            assert any(event.event_type == EventType.HOST_SNAPSHOT for event in events)
            latest = status["latest_host"]
            assert "cpu_percent" in latest
            assert "memory_percent" in latest
            assert "process_count" in latest
            assert "network_rx_bytes_per_sec" in latest
        finally:
            await service.stop()

    asyncio.run(scenario())
