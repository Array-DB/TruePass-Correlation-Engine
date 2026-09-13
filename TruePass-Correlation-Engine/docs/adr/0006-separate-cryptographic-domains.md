# ADR 0006: Separate identity, evidence signing, and anchoring domains

## Decision

TruePass keeps identity verification, evidence signing, and optional Bitcoin anchoring as independent cryptographic domains.

Identity factors can authorize an operation but never provide entropy for a signing or wallet key. Evidence signing uses a dedicated Ed25519 key. External anchoring receives only a cryptographic commitment such as a Merkle root.

## Consequences

A compromise or privacy issue in one domain does not automatically expose the others, and public timestamp anchors contain no raw PII.
