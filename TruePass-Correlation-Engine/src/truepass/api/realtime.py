"""Bounded asynchronous broadcast channels for realtime operator streams."""
from __future__ import annotations

import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import AsyncIterator


class RealtimeHub:
    def __init__(self, *, queue_size: int = 16) -> None:
        if queue_size < 1:
            raise ValueError("queue_size must be positive")
        self.queue_size = queue_size
        self._channels: dict[str, set[asyncio.Queue[dict[str, object]]]] = defaultdict(set)
        self._lock = asyncio.Lock()

    @asynccontextmanager
    async def subscribe(self, channel: str) -> AsyncIterator[asyncio.Queue[dict[str, object]]]:
        queue: asyncio.Queue[dict[str, object]] = asyncio.Queue(maxsize=self.queue_size)
        async with self._lock:
            self._channels[channel].add(queue)
        try:
            yield queue
        finally:
            async with self._lock:
                self._channels[channel].discard(queue)

    async def publish(self, channel: str, payload: dict[str, object]) -> None:
        async with self._lock:
            queues = tuple(self._channels.get(channel, ()))
        for queue in queues:
            if queue.full():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
            queue.put_nowait(payload)

    async def subscriber_count(self, channel: str) -> int:
        async with self._lock:
            return len(self._channels.get(channel, ()))
