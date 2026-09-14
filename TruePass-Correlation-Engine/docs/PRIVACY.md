# Privacy and Data Governance

Phase 29 separates TruePass data into six logical domains: **identity, biometrics, behavior, security, telemetry, and forensics**. `GovernancePolicy` applies explicit retention windows and sensitivity labels and can calculate when local records become eligible for deletion.

Default policy values are conservative starting points, not legal advice or jurisdiction-specific requirements. Biometrics and behavioral research are optional and restricted. Raw biometric media should be minimized in favor of protected templates when a deployment enables biometrics, with explicit consent and deletion controls.

Public-chain anchoring never contains raw PII. Only cryptographic evidence commitments may leave the private evidence domain. External immutable commitments cannot themselves be deleted, so they must never encode personal data directly.
