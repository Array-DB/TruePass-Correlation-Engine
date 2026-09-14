"""Merkle evidence batches with optional Ed25519 signatures."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence
from uuid import uuid4

from truepass.evidence.ledger import LedgerRecord
from truepass.evidence.merkle import MerkleProof, MerkleTree
from truepass.evidence.signing import EvidenceSigner, SignatureEnvelope, verify_signature


@dataclass(frozen=True, slots=True)
class EvidenceBatch:
    batch_id: str
    first_sequence: int
    last_sequence: int
    leaf_count: int
    root_hash: str
    signature: SignatureEnvelope | None

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        return payload


class EvidenceBatchBuilder:
    def build(self, records: Sequence[LedgerRecord], *, signer: EvidenceSigner | None = None) -> EvidenceBatch:
        if not records:
            raise ValueError("at least one ledger record is required")
        ordered = sorted(records, key=lambda item: item.sequence)
        expected = list(range(ordered[0].sequence, ordered[-1].sequence + 1))
        if [record.sequence for record in ordered] != expected:
            raise ValueError("ledger records must form one contiguous sequence")
        tree = MerkleTree([bytes.fromhex(record.event_hash) for record in ordered])
        signature = signer.sign_digest(bytes.fromhex(tree.root_hex)) if signer is not None else None
        return EvidenceBatch(
            batch_id=str(uuid4()),
            first_sequence=ordered[0].sequence,
            last_sequence=ordered[-1].sequence,
            leaf_count=len(ordered),
            root_hash=tree.root_hex,
            signature=signature,
        )

    @staticmethod
    def proof(records: Sequence[LedgerRecord], sequence: int) -> MerkleProof:
        ordered = sorted(records, key=lambda item: item.sequence)
        index = next((index for index, record in enumerate(ordered) if record.sequence == sequence), None)
        if index is None:
            raise KeyError(sequence)
        return MerkleTree([bytes.fromhex(record.event_hash) for record in ordered]).proof(index)

    @staticmethod
    def verify_proof(batch: EvidenceBatch, proof: MerkleProof) -> bool:
        return MerkleTree.verify(proof, batch.root_hash)

    @staticmethod
    def verify_signature(batch: EvidenceBatch) -> bool | None:
        if batch.signature is None:
            return None
        return batch.signature.digest_hex == batch.root_hash and verify_signature(batch.signature)
