# ADR 0003: Minimize process telemetry by default

## Status
Accepted

## Decision
Process command lines are excluded by default because they can contain tokens, passwords, URLs, or other secrets. Socket metadata is best-effort and read-only.

## Consequences
Operators must explicitly enable command-line capture. Permission failures are treated as missing telemetry rather than reasons to elevate privileges automatically.
