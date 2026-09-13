# ADR 0001: PostgreSQL as the canonical event store

## Status
Accepted

## Decision
Use PostgreSQL through SQLAlchemy 2.x as the canonical relational persistence layer. Vector search will be added through pgvector in a later phase instead of introducing a second database early.

## Consequences
The production schema can use PostgreSQL UUIDs and later pgvector directly. Integration tests require a disposable PostgreSQL instance rather than silently validating against a database with different semantics.
