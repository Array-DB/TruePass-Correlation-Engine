# TruePass Architecture

TruePass is a defensive multimodal telemetry, anomaly-detection, evidence-preservation, and forensic-correlation platform. Its engineering flow is **Observe → Timestamp → Normalize → Correlate → Score → Preserve Evidence → Alert**.

## Layers

1. **Collectors** observe local processes, sockets, Wi-Fi, Bluetooth, and receive-only SDR sources. Collectors are passive/read-only by default.
2. **Canonical events** normalize timestamps, provenance, source, severity, confidence, and feature metadata.
3. **Signal processing** converts I/Q samples into FFT/PSD/spectrogram representations and versioned RF features.
4. **Detection** builds baselines, computes anomaly distances, and produces clustering observations. Unknown clusters are never automatic attacker labels.
5. **Correlation** orders events in time, calculates explainable cross-domain relationships, scores candidate incidents, and builds event/entity graphs.
6. **Evidence** stores deterministic canonical event bytes in a SHA-256 hash chain, aggregates evidence into Merkle roots, signs commitments, and can optionally hand commitments to an external timestamp anchor.
7. **Persistence/retrieval** uses PostgreSQL as canonical relational storage and pgvector as an optional similarity-retrieval aid.
8. **Operator surfaces** expose FastAPI endpoints, metrics, alerting, and a local dashboard.
9. **Research modules** for voice and EEG are isolated from the trusted authentication/response path and are labeled experimental.

## Trust boundaries

RF anomaly, voice classification, EEG classification, similarity hits, and correlation scores are observations or candidate explanations. They do not independently establish causation, identity, compromise, or human intent. TruePass does not expose SDR transmit operations or autonomous neuromodulation.
