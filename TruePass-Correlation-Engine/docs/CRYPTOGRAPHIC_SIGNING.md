# Cryptographic Signing

Phase 20 signs 32-byte evidence commitments with Ed25519. Signing keys are a separate cryptographic domain from identity verification and wallet/private-key generation.

`Ed25519EvidenceSigner.generate()` is suitable for ephemeral/test use. Production deployments should load a protected PEM key or implement a hardware/HSM-backed signer through the `EvidenceSigner` protocol. Private keys are never logged or embedded in evidence events.

Verification uses the public key carried in the `SignatureEnvelope` and rejects modified digests or signatures.
