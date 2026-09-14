# Evidence Model

Each canonical event is serialized as deterministic UTF-8 JSON. The file evidence ledger chains records as:

`event_hash = SHA256(previous_hash_bytes || canonical_event_bytes)`

Verification checks sequence continuity, previous-hash linkage, event hash recomputation, canonical JSON validity, and event-ID consistency.

Merkle trees aggregate evidence digests into batch commitments and support inclusion proofs. Ed25519 signatures can authenticate 32-byte commitments. Optional external timestamp anchors receive commitments only, never raw event content or PII.

Relational event/evidence records are canonical. Vector indexes, dashboards, and ML state are derived views and can be rebuilt.
