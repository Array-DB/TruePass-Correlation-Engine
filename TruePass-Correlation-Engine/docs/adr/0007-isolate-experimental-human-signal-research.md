# ADR 0007 — Isolate experimental human-signal research

## Decision
Voice and EEG research live beneath `truepass.research` and do not participate directly in trusted identity, evidence, or automated-response decisions.

## Rationale
Voice anti-spoofing and constrained EEG classifiers can produce useful research observations, but their uncertainty and privacy implications require stronger separation than ordinary telemetry. Keeping them out of the security core prevents experimental inference from being misrepresented as identity proof, malicious intent, or unrestricted thought decoding.

## Consequences
Research outputs are explicitly marked experimental. Voice alone cannot authenticate a user. EEG uses constrained classifiers only. No stimulation functionality is provided.
