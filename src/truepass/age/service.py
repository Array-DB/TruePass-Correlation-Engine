"""TRUE-PASS-AGE: ledger browsing, chain verification and evidence proofs."""
from __future__ import annotations

from dataclasses import asdict
import os
from pathlib import Path
import tempfile

from truepass.evidence.batches import EvidenceBatch, EvidenceBatchBuilder
from truepass.evidence.ledger import FileEvidenceLedger, LedgerRecord
from truepass.evidence.signing import Ed25519EvidenceSigner
from truepass.models.events import Event


class AgeService:
    """Own the local evidence chain and produce signed Merkle commitments.

    AGE remains local-first: a deployment can set ``TRUEPASS_LEDGER_PATH`` to a
    persistent location. Otherwise each runtime gets an isolated temporary ledger.
    """

    def __init__(self, ledger_path: str | Path | None = None) -> None:
        configured = ledger_path or os.getenv("TRUEPASS_LEDGER_PATH")
        if configured is None:
            root = Path(tempfile.mkdtemp(prefix="truepass-age-"))
            configured = root / "ledger.jsonl"
        self.ledger = FileEvidenceLedger(configured)
        self.builder = EvidenceBatchBuilder()
        self.signer = Ed25519EvidenceSigner.generate(key_id="truepass-age-runtime")
        self._batches: dict[str, EvidenceBatch] = {}

    @property
    def path(self) -> Path:
        return self.ledger.path

    def append(self, event: Event) -> LedgerRecord:
        return self.ledger.append(event)

    def records(self, *, offset: int = 0, limit: int = 100) -> list[dict[str, object]]:
        records = self.ledger.records()
        return [asdict(record) for record in records[offset : offset + limit]]

    def status(self) -> dict[str, object]:
        verification = self.ledger.verify()
        records = self.ledger.records()
        return {
            "valid": verification.valid,
            "records": verification.records,
            "error": verification.error,
            "head_hash": records[-1].event_hash if records else None,
            "canonicalization_version": records[-1].canonicalization_version if records else "1",
            "signed_batches": len(self._batches),
        }

    def verify_record(self, sequence: int) -> dict[str, object]:
        record = self.ledger.get_record(sequence)
        if record is None:
            raise KeyError(sequence)
        verification = self.ledger.verify()
        # Full-chain verification is intentional: a record cannot be trusted if an
        # earlier link is broken even when its own serialized row looks intact.
        return {
            "sequence": sequence,
            "event_id": record.event_id,
            "event_hash": record.event_hash,
            "chain_valid": verification.valid,
            "chain_error": verification.error,
        }

    def build_batch(self, *, start: int | None = None, end: int | None = None) -> dict[str, object]:
        records = list(self.ledger.records())
        if not records:
            raise ValueError("ledger is empty")
        first = 1 if start is None else start
        last = len(records) if end is None else end
        if first < 1 or last < first or last > len(records):
            raise ValueError("invalid ledger sequence range")
        selected = records[first - 1 : last]
        batch = self.builder.build(selected, signer=self.signer)
        self._batches[batch.batch_id] = batch
        return batch.as_dict()

    def batches(self) -> list[dict[str, object]]:
        return [batch.as_dict() for batch in self._batches.values()]

    def batch(self, batch_id: str) -> EvidenceBatch:
        try:
            return self._batches[batch_id]
        except KeyError as exc:
            raise KeyError(batch_id) from exc

    def proof(self, batch_id: str, sequence: int) -> dict[str, object]:
        batch = self.batch(batch_id)
        records = list(self.ledger.records())[batch.first_sequence - 1 : batch.last_sequence]
        proof = self.builder.proof(records, sequence)
        return {
            "batch_id": batch_id,
            "sequence": sequence,
            "root_hash": batch.root_hash,
            "leaf_hex": proof.leaf_hex,
            "index": proof.index,
            "steps": [asdict(step) for step in proof.steps],
            "verified": self.builder.verify_proof(batch, proof),
        }

    def verify_batch(self, batch_id: str) -> dict[str, object]:
        batch = self.batch(batch_id)
        return {
            "batch_id": batch_id,
            "root_hash": batch.root_hash,
            "signature_present": batch.signature is not None,
            "signature_valid": self.builder.verify_signature(batch),
            "signature": asdict(batch.signature) if batch.signature else None,
        }
