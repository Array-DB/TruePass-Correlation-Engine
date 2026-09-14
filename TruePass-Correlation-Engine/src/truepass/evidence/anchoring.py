"""Optional timestamp anchoring for cryptographic commitments only.

The core never creates a Bitcoin wallet or derives keys from identity data.
A Bitcoin broadcaster must be explicitly injected by the deployment operator.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import inspect
import json
from pathlib import Path
from typing import Awaitable, Callable, Protocol


@dataclass(frozen=True, slots=True)
class AnchorReceipt:
    provider: str
    digest_hex: str
    anchored_at: str
    reference: str | None = None
    status: str = "recorded"


class TimestampAnchor(Protocol):
    async def anchor(self, digest: bytes) -> AnchorReceipt: ...


def _validate_digest(digest: bytes) -> str:
    if len(digest) != 32:
        raise ValueError("anchor digest must be exactly 32 bytes")
    return digest.hex()


class NoOpAnchor:
    async def anchor(self, digest: bytes) -> AnchorReceipt:
        digest_hex = _validate_digest(digest)
        return AnchorReceipt("noop", digest_hex, datetime.now(UTC).isoformat(), status="not_broadcast")


class FileAnchor:
    """Append offline timestamp receipts to JSONL for test/lab deployments."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    async def anchor(self, digest: bytes) -> AnchorReceipt:
        digest_hex = _validate_digest(digest)
        receipt = AnchorReceipt("file", digest_hex, datetime.now(UTC).isoformat(), reference=str(self.path))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(receipt), sort_keys=True, separators=(",", ":")) + "\n")
        return receipt


BroadcastFunction = Callable[[bytes], str | Awaitable[str]]


class BitcoinAnchor:
    """Provider-neutral Bitcoin anchoring boundary.

    ``broadcaster`` receives the 32-byte commitment and must return a transaction
    identifier/reference. TruePass itself does not manage funds or private keys.
    """

    def __init__(self, broadcaster: BroadcastFunction, *, provider_name: str = "bitcoin") -> None:
        self._broadcaster = broadcaster
        self._provider_name = provider_name

    async def anchor(self, digest: bytes) -> AnchorReceipt:
        digest_hex = _validate_digest(digest)
        result = self._broadcaster(digest)
        reference = await result if inspect.isawaitable(result) else result
        if not reference:
            raise RuntimeError("Bitcoin broadcaster returned an empty reference")
        return AnchorReceipt(self._provider_name, digest_hex, datetime.now(UTC).isoformat(), str(reference), "submitted")
