# Security

TruePass is designed for systems and spectrum you are authorized to monitor. It is defensive and read-only by default.

Security controls include deterministic evidence serialization, SHA-256 hash chaining, Merkle inclusion proofs, Ed25519 commitment signing, replay protection, bounded clock-skew assessment, constant-time API secret comparison, secret redaction, non-root containers, dropped container capabilities, and optional API-key authentication.

The product does not expose active RF transmission, exploitation, credential theft, autonomous blocking, or neuromodulation. Evidence integrity proves that stored evidence has not changed under the checked mechanism; it does not prove that the original observation was correct.

See `THREAT_MODEL.md`, `PRIVACY.md`, and `CRYPTOGRAPHIC_SIGNING.md` for detailed boundaries.
