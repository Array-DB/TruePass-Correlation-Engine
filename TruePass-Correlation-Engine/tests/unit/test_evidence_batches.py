from truepass.evidence.batches import EvidenceBatchBuilder
from truepass.evidence.ledger import LedgerRecord
from truepass.evidence.signing import Ed25519EvidenceSigner


def record(sequence: int, digest_byte: str) -> LedgerRecord:
    return LedgerRecord(
        sequence=sequence,
        event_id=f"event-{sequence}",
        previous_hash="00" * 32,
        event_hash=digest_byte * 64,
        timestamp_ns=sequence,
        canonical_event="{}",
    )


def test_signed_evidence_batch_proof_round_trip() -> None:
    records = [record(1, "1"), record(2, "2"), record(3, "3")]
    signer = Ed25519EvidenceSigner.generate(key_id="batch-test")
    builder = EvidenceBatchBuilder()
    batch = builder.build(records, signer=signer)
    proof = builder.proof(records, 2)
    assert batch.leaf_count == 3
    assert builder.verify_proof(batch, proof)
    assert builder.verify_signature(batch) is True


def test_batch_requires_contiguous_records() -> None:
    builder = EvidenceBatchBuilder()
    try:
        builder.build([record(1, "1"), record(3, "3")])
    except ValueError as exc:
        assert "contiguous" in str(exc)
    else:
        raise AssertionError("expected ValueError")
