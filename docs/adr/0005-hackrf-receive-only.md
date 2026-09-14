# ADR 0005 — HackRF integration is receive-only

## Decision

TruePass creates only SoapySDR RX streams for HackRF One. It exposes capture and device discovery but no transmit API.

## Rationale

TruePass is a defensive observation and forensic-correlation platform. Receive-only integration preserves the project's read-only-first boundary while allowing real RF telemetry to flow through the same DSP, feature, baseline and correlation pipeline as synthetic/file sources.
