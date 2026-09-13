# Voice / Echo Research Module

Phase 26 is intentionally outside the trusted security core. `truepass.research.voice` defines small protocol boundaries for speech-to-text and constrained intent classification, then combines their confidence values into an explicitly experimental `VoiceObservation`.

The module does not claim that voice proves identity. Replay detection, synthetic-voice detection, speaker verification, device identity, and challenge-response can be attached as research telemetry, but authentication decisions remain in the separate identity architecture. No microphone capture is enabled by default.
