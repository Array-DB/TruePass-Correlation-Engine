# TruePass Threat Model

Phase 28 hardens the platform against threats identified in the master plan while retaining a read-only defensive architecture.

| Threat | Current mitigation |
|---|---|
| Event replay | Bounded `ReplayGuard` rejects duplicate tokens/identifiers |
| Clock manipulation / bad synchronization | Explicit clock-skew assessment and Phase 14 clock-quality metadata |
| Secret leakage | Secret-redaction helper, environment-based secrets, no private-key logging |
| API secret timing leakage | Constant-time secret comparison |
| Evidence modification | Hash chain, Merkle proofs, and Ed25519 evidence-root signatures |
| Collector impersonation | Provenance, sensor identity fields, and future deployment authentication hooks |
| Malformed input | Pydantic validation, explicit numerical guards, bounded API pagination |
| Resource exhaustion | Bounded replay cache, bounded API query sizes, bounded rolling RF baseline |
| Privilege escalation | Collectors are read-only and elevated privileges are not assumed by default |
| Active-response misuse | No exploitation, RF transmission, firmware manipulation, or autonomous interference |

Remaining production work includes deployment-specific mTLS/service identity, OS sandboxing, dependency/SBOM policy, database row/role separation, secret-manager integration, and load/DoS testing.
