# ADR 0002: Deterministic canonical event serialization

## Status
Accepted

## Decision
Every normalized event has a deterministic UTF-8 JSON representation with sorted keys, compact separators, explicit nulls, and JSON-mode Pydantic conversion.

## Consequences
The same logical event produces the same bytes and SHA-256 digest, providing a stable foundation for the append-only forensic ledger and Merkle-tree phases.
