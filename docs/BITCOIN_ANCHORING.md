# Optional Bitcoin Timestamp Anchoring

Phase 21 treats Bitcoin as an optional external timestamp/commitment layer. TruePass never derives a wallet key from PII, biometrics, behavior, EEG, emotion, timestamps, or evidence.

Only a 32-byte commitment such as a Merkle root is submitted. `NoOpAnchor` supports deployments with anchoring disabled, `FileAnchor` provides an offline receipt trail, and `BitcoinAnchor` accepts an explicitly injected broadcaster/provider. The core does not hold funds or silently broadcast transactions.
