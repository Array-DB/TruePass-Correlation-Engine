"""Append-only SHA-256 forensic ledger with durable writes and verification."""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator

from truepass.models.events import Event

ZERO_HASH = "0" * 64
CANONICALIZATION_VERSION = "1"

try:  # pragma: no cover - Windows fallback is exercised implicitly by import
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None  # type: ignore[assignment]


@dataclass(frozen=True, slots=True)
class LedgerRecord:
    sequence: int
    event_id: str
    previous_hash: str
    event_hash: str
    timestamp_ns: int
    canonical_event: str
    canonicalization_version: str = CANONICALIZATION_VERSION


@dataclass(frozen=True, slots=True)
class LedgerVerification:
    valid: bool
    records: int
    error: str | None = None


class FileEvidenceLedger:
    """Durable local JSONL evidence chain.

    Writes are serialized in-process and guarded with an advisory file lock on
    platforms that support ``fcntl``. Each successful append is flushed and
    fsynced before returning so a caller can treat the returned record as
    durably committed to the local filesystem.
    """

    _thread_lock = threading.RLock()

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _locked_file(self, mode: str) -> Iterator[object]:
        with self.path.open(mode, encoding="utf-8") as handle:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield handle
            finally:
                if fcntl is not None:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def append(self, event: Event) -> LedgerRecord:
        canonical = event.canonical_bytes()
        with self._thread_lock:
            self.path.touch(exist_ok=True)
            with self._locked_file("r+") as handle:
                handle.seek(0)
                records = self._read_handle(handle)
                previous_hash = records[-1].event_hash if records else ZERO_HASH
                digest = hashlib.sha256(bytes.fromhex(previous_hash) + canonical).hexdigest()
                record = LedgerRecord(
                    sequence=len(records) + 1,
                    event_id=str(event.event_id),
                    previous_hash=previous_hash,
                    event_hash=digest,
                    timestamp_ns=time.time_ns(),
                    canonical_event=canonical.decode("utf-8"),
                )
                handle.seek(0, os.SEEK_END)
                handle.write(
                    json.dumps(
                        asdict(record),
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                handle.flush()
                os.fsync(handle.fileno())
                return record

    def records(self) -> tuple[LedgerRecord, ...]:
        with self._thread_lock:
            return tuple(self._read())

    def get_record(self, sequence: int) -> LedgerRecord | None:
        if sequence < 1:
            return None
        records = self.records()
        if sequence > len(records):
            return None
        return records[sequence - 1]

    def verify(self) -> LedgerVerification:
        try:
            records = self._read()
        except Exception as exc:  # parsing errors are evidence-integrity failures
            return LedgerVerification(False, 0, f"parse_error: {exc}")

        previous_hash = ZERO_HASH
        for index, record in enumerate(records, 1):
            if record.sequence != index:
                return LedgerVerification(False, len(records), f"sequence_mismatch_at_{index}")
            if record.canonicalization_version != CANONICALIZATION_VERSION:
                return LedgerVerification(
                    False,
                    len(records),
                    f"canonicalization_version_unsupported_at_{index}",
                )
            if record.previous_hash != previous_hash:
                return LedgerVerification(False, len(records), f"previous_hash_mismatch_at_{index}")
            try:
                previous_bytes = bytes.fromhex(previous_hash)
            except ValueError:
                return LedgerVerification(False, len(records), f"previous_hash_invalid_at_{index}")
            expected = hashlib.sha256(
                previous_bytes + record.canonical_event.encode("utf-8")
            ).hexdigest()
            if record.event_hash != expected:
                return LedgerVerification(False, len(records), f"event_hash_mismatch_at_{index}")
            try:
                payload = json.loads(record.canonical_event)
                event_id = str(payload["event_id"])
            except (json.JSONDecodeError, KeyError, TypeError):
                return LedgerVerification(False, len(records), f"canonical_event_invalid_at_{index}")
            if event_id != record.event_id:
                return LedgerVerification(False, len(records), f"event_id_mismatch_at_{index}")
            previous_hash = record.event_hash
        return LedgerVerification(True, len(records))

    def _read(self) -> list[LedgerRecord]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            return self._read_handle(handle)

    @staticmethod
    def _read_handle(handle: object) -> list[LedgerRecord]:
        lines = handle.readlines()
        return [
            LedgerRecord(**json.loads(line))
            for line in lines
            if isinstance(line, str) and line.strip()
        ]
