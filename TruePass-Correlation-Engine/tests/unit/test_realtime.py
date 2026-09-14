import asyncio
from truepass.api.realtime import RealtimeHub


def test_realtime_hub_is_bounded_and_delivers_latest() -> None:
    async def run() -> None:
        hub = RealtimeHub(queue_size=1)
        async with hub.subscribe("spectrum") as queue:
            await hub.publish("spectrum", {"frame": 1})
            await hub.publish("spectrum", {"frame": 2})
            assert await queue.get() == {"frame": 2}
    asyncio.run(run())
