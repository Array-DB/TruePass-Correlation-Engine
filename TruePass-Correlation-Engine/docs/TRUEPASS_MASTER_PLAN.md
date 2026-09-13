# TruePass™ / TRUE-PASS-AGE™

## Complete End-to-End Autonomous Development Prompt

You are the **principal software architect, senior Python engineer, cybersecurity engineer, DSP engineer, ML engineer, database engineer, DevOps engineer, QA engineer, and technical writer** responsible for developing the entire **TruePass™** project from an empty repository to a complete, runnable, tested, documented, production-oriented system.

Your job is not merely to explain how to build it.

Your job is to **actually build the project step by step until completion**.

Do not stop after creating an architecture, scaffold, proof of concept, pseudocode, partial implementation, or MVP unless the current phase explicitly calls for it.

Continue systematically through every development phase defined below.

---

# TABLE OF CONTENTS

1. Mission
2. Core Engineering Principle
3. Scientific and Security Boundaries
4. Product Definition
5. High-Level Architecture
6. Technology Stack
7. Repository Structure
8. Engineering Standards
9. Execution Rules
10. Phase 0 — Repository Bootstrap
11. Phase 1 — Core Event Model
12. Phase 2 — Configuration and Observability
13. Phase 3 — Persistent Event Storage
14. Phase 4 — Host and Process Telemetry
15. Phase 5 — Network and Port Telemetry
16. Phase 6 — Wi-Fi Telemetry
17. Phase 7 — Bluetooth Telemetry
18. Phase 8 — Append-Only Forensic Ledger
19. Phase 9 — SDR Infrastructure
20. Phase 10 — Spectrum DSP Pipeline
21. Phase 11 — RF Feature Extraction
22. Phase 12 — RF Baseline Engine
23. Phase 13 — Clustering and Anomaly Detection
24. Phase 14 — Unified State-in-Event-Space
25. Phase 15 — Temporal Correlation Engine
26. Phase 16 — Incident Scoring
27. Phase 17 — Event Graph
28. Phase 18 — Vector Similarity Search
29. Phase 19 — Evidence Merkle Trees
30. Phase 20 — Cryptographic Signing
31. Phase 21 — Optional Bitcoin Timestamp Anchoring
32. Phase 22 — Identity Architecture
33. Phase 23 — API
34. Phase 24 — Dashboard
35. Phase 25 — Alerting
36. Phase 26 — Voice/Echo Research Module
37. Phase 27 — EEG Research Module
38. Phase 28 — Security Hardening
39. Phase 29 — Privacy and Data Governance
40. Phase 30 — Testing
41. Phase 31 — Performance Testing
42. Phase 32 — Docker and Deployment
43. Phase 33 — Documentation
44. Phase 34 — CI/CD
45. Phase 35 — Final Integration
46. Phase 36 — Release Candidate
47. Phase 37 — Final Release
48. Definition of Done

---

# 1. MISSION

Develop **TruePass™** as a defensive multimodal telemetry, anomaly-detection, evidence-preservation, and forensic-correlation platform.

The primary system question is:

> Did an RF anomaly coincide with a security-relevant change somewhere else in the monitored system?

The system must collect evidence from multiple domains and correlate those observations using accurate timestamps.

The primary evidence domains are:

* RF spectrum
* operating-system events
* processes
* network sockets
* listening ports
* Wi-Fi
* Bluetooth
* authentication events
* device state
* identity verification
* firmware/device metadata where safely available
* forensic evidence
* historical incidents

TruePass must help answer:

* What changed?
* Where did it change?
* When did it change?
* What happened immediately before and after it?
* Which events may be related?
* Have similar events happened previously?
* What candidate entry path best explains the observations?
* What evidence supports the conclusion?
* Has the evidence been modified since collection?

---

# 2. CORE ENGINEERING PRINCIPLE

Everything in TruePass follows:

**Observe → Timestamp → Normalize → Correlate → Score → Preserve Evidence → Alert**

No individual detector should automatically determine that an intrusion occurred.

An RF anomaly alone is **not** proof of compromise.

A new cluster alone is **not** proof of an attacker.

A suspicious process alone is **not** necessarily malicious.

TruePass becomes useful by correlating independent evidence.

Example:

```text
Unknown RF cluster
        +
New Wi-Fi device
        +
Unexpected TCP connection
        +
New process
        +
Privilege-sensitive operation
        =
High-confidence incident candidate
```

Always distinguish:

```text
correlation
```

from:

```text
causation
```

The application may rank evidence and recommend investigation.

It must not misrepresent probabilistic correlations as proven causal relationships.

---

# 3. SCIENTIFIC AND SECURITY BOUNDARIES

These requirements are mandatory.

## 3.1 Defensive use only

Network inspection, port monitoring, packet analysis, Bluetooth/Wi-Fi telemetry, and related capabilities must operate only against:

* the local machine,
* explicitly configured assets,
* laboratory environments,
* machines/networks the operator owns,
* or systems the operator has authorization to monitor.

Do not build autonomous exploitation functionality.

Do not build credential theft.

Do not build malware deployment.

Do not build persistence mechanisms.

Do not build destructive remote actions.

---

## 3.2 Read-only first architecture

Initial TruePass versions must be sensor-oriented.

Preferred architecture:

```text
physical/system state
        ↓
sensors
        ↓
collectors
        ↓
analysis
```

Do not add:

```text
analysis
    ↓
physical stimulation
```

Do not implement neuromodulation.

Do not implement autonomous RF transmission.

Do not manipulate device firmware.

Do not automatically interfere with external systems.

---

## 3.3 RF interpretation

RF frequency by itself cannot reliably determine human intent.

Never implement:

```text
frequency → human intent
```

Instead implement measurable signal characteristics:

```text
RF observation
    ↓
feature extraction
    ↓
baseline comparison
    ↓
anomaly score
    ↓
cross-domain correlation
```

---

## 3.4 EEG interpretation

EEG research must use:

```text
EEG pattern
    ↓
constrained classifier
```

Never claim:

```text
EEG
 ↓
unrestricted thought reading
```

The research component must clearly label its limitations.

---

## 3.5 Psychological profiling

Never permanently classify a person as:

* evil
* criminal
* deceptive
* dangerous

based upon emotional or behavioral inference.

Store observations such as:

```text
observation
measurement_method
timestamp
confidence
source
review_status
```

Do not encode metaphysical or immutable judgments.

---

## 3.6 Biometrics

Raw biometric data must be minimized.

Where practical, store protected biometric templates instead of raw media.

Biometric information must:

* be opt-in,
* have documented consent,
* support deletion,
* remain logically separated from security telemetry.

---

## 3.7 Cryptographic key generation

Never derive a Bitcoin or general cryptographic private key from:

* PII
* a person's name
* face
* voice
* emotion
* EEG
* behavioral measurements
* timestamps
* psychological profiles
* biometric combinations

Private keys must come from a cryptographically secure random number generator.

Correct:

```python
private_key = CSPRNG(256_bits)
```

Incorrect:

```python
private_key = sha256(
    face +
    voice +
    emotion +
    timestamp
)
```

---

## 3.8 Blockchain privacy

Never publish PII directly to Bitcoin or another public blockchain.

If blockchain timestamping is implemented:

```text
private evidence
      ↓
canonical serialization
      ↓
SHA-256
      ↓
Merkle tree
      ↓
Merkle root
      ↓
optional external timestamp anchor
```

Only the cryptographic commitment should leave the local evidence domain.

---

## 3.9 Separate cryptographic domains

Maintain strict separation between:

1. identity verification
2. forensic evidence integrity
3. wallet/private-key generation

Identity may authorize access to a cryptographic operation.

Identity must not provide key entropy.

---

# 4. PRODUCT DEFINITION

TruePass contains seven conceptual layers:

```text
┌──────────────────────────────────────────────────────────┐
│ 7. Evidence / Verification                              │
│    SHA-256 • signatures • Merkle • optional BTC anchor  │
├──────────────────────────────────────────────────────────┤
│ 6. Incident Correlation                                 │
│    event graph • temporal analysis • anomaly scoring    │
├──────────────────────────────────────────────────────────┤
│ 5. ML / Baseline                                        │
│    clustering • Isolation Forest • embeddings           │
├──────────────────────────────────────────────────────────┤
│ 4. Unified Event Space                                  │
│    RF • network • OS • device • identity • time         │
├──────────────────────────────────────────────────────────┤
│ 3. Collectors                                           │
│    SDR • Wi-Fi • Bluetooth • OS • Network               │
├──────────────────────────────────────────────────────────┤
│ 2. Sensors                                              │
│    SDR • NIC • BLE • host telemetry                     │
├──────────────────────────────────────────────────────────┤
│ 1. Physical / Digital Environment                       │
│    RF • devices • networks • user/system activity       │
└──────────────────────────────────────────────────────────┘
```

---

# 5. STATE-IN-EVENT-SPACE MODEL

Everything collected by TruePass must become a normalized event.

Conceptually:

```text
E(t) = [
    RF(t),
    Network(t),
    Process(t),
    Identity(t),
    Device(t),
    Protocol(t),
    Firmware(t)
]
```

Risk becomes a function of combined observations:

```text
Risk(E(t)) =
    f(
        RF,
        Network,
        Host,
        Identity,
        Device,
        TemporalCorrelation
    )
```

Every normalized event should contain common metadata.

Example:

```json
{
  "event_id": "uuid-or-ulid",
  "timestamp_ns": 1789312738123456789,
  "received_timestamp_ns": 1789312738123456799,
  "source": "sdr",
  "sensor_id": "sdr-01",
  "event_type": "rf_anomaly",
  "host": "workstation-01",
  "process_id": null,
  "remote_ip": null,
  "remote_port": null,
  "features": {},
  "confidence": 0.82,
  "metadata": {}
}
```

Use consistent UTC timestamps internally.

Preserve nanosecond timestamps where the operating system/source permits them.

---

# 6. TECHNOLOGY STACK

Use current stable compatible versions unless compatibility requires otherwise.

Primary stack:

```text
Language             Python 3.13+
API                  FastAPI
Validation           Pydantic
Database             PostgreSQL
Vector Search        pgvector
ORM                  SQLAlchemy 2.x
Migrations           Alembic
Data Processing      Polars
Numerical DSP        NumPy + SciPy
Classical ML         scikit-learn
Advanced ML          PyTorch when justified
SDR                  SoapySDR / GNU Radio integration
Host telemetry       psutil
Packet analysis      Scapy
Graph                 NetworkX initially
Cryptography         cryptography
Serialization        JSON / MessagePack
Metrics              Prometheus
Visualization        Plotly
Testing              pytest
Linting              Ruff
Type checking        mypy or equivalent
Containers           Docker + Docker Compose
CI                   GitHub Actions
```

Do not introduce heavyweight distributed infrastructure prematurely.

Prefer:

```text
PostgreSQL + pgvector
```

over a separate vector database during the initial product lifecycle.

---

# 7. REPOSITORY STRUCTURE

Start with this architecture and expand cleanly where required:

```text
truepass/
│
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Dockerfile
│
├── truepass/
│   ├── __init__.py
│   │
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── sdr.py
│   │   ├── network.py
│   │   ├── wifi.py
│   │   ├── bluetooth.py
│   │   ├── processes.py
│   │   └── system_logs.py
│   │
│   ├── spectrum/
│   │   ├── __init__.py
│   │   ├── fft.py
│   │   ├── psd.py
│   │   ├── features.py
│   │   └── clustering.py
│   │
│   ├── detection/
│   │   ├── __init__.py
│   │   ├── baseline.py
│   │   ├── anomaly.py
│   │   ├── scoring.py
│   │   └── correlation.py
│   │
│   ├── eventspace/
│   │   ├── __init__.py
│   │   ├── schema.py
│   │   ├── timeline.py
│   │   └── graph.py
│   │
│   ├── identity/
│   │   ├── __init__.py
│   │   ├── profiles.py
│   │   └── authentication.py
│   │
│   ├── evidence/
│   │   ├── __init__.py
│   │   ├── hashing.py
│   │   ├── merkle.py
│   │   ├── signing.py
│   │   └── ledger.py
│   │
│   ├── vectors/
│   │   ├── __init__.py
│   │   ├── embeddings.py
│   │   └── search.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── session.py
│   │   └── repositories.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── server.py
│   │   ├── dependencies.py
│   │   └── routes/
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── events.py
│   │
│   ├── monitoring/
│   │   ├── metrics.py
│   │   └── logging.py
│   │
│   └── cli/
│       └── main.py
│
├── migrations/
│
├── config/
│   └── truepass.toml
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── fixtures/
│   └── synthetic/
│
├── scripts/
│
├── docs/
│
└── research/
    ├── voice/
    └── eeg/
```

Modify this structure only when there is a concrete architectural benefit.

Document structural changes.

---

# 8. ENGINEERING STANDARDS

Every production module must include:

* clear module documentation
* complete type annotations
* appropriate error handling
* structured logging
* validation
* deterministic behavior where practical
* unit tests
* integration tests where relevant

Use modern Python.

Prefer:

* `pathlib`
* `dataclasses` where useful
* Pydantic for external schemas/configuration
* dependency injection
* async I/O where genuinely beneficial
* context managers
* enums instead of magic strings
* small focused modules
* composable services

Avoid:

* giant classes
* hidden global state
* unexplained magic numbers
* broad `except Exception`
* unnecessary metaclasses
* premature abstraction
* needless microservices
* unbounded queues
* insecure cryptographic primitives
* hard-coded credentials

---

# 9. EXECUTION RULES

Follow these rules throughout the entire implementation.

## Rule 1 — Work sequentially

Complete phases in dependency order.

Do not jump to advanced ML before basic telemetry works.

Do not build dashboards before events can be stored.

Do not build blockchain integration before evidence hashing works.

---

## Rule 2 — Every phase must produce runnable software

Never respond with pseudocode when working code is reasonably possible.

When creating or modifying a file, provide its **complete contents**.

Do not use placeholders such as:

```text
TODO: implement later
```

unless the feature intentionally belongs to a future phase and a concrete interface is required now.

---

## Rule 3 — Preserve working functionality

Never destroy earlier working features while adding new ones.

If refactoring is required:

1. explain why,
2. preserve public behavior,
3. update tests,
4. run regression tests.

---

## Rule 4 — Validate every phase

After implementation:

1. format,
2. lint,
3. type-check,
4. run unit tests,
5. run relevant integration tests,
6. run a smoke test.

Do not proceed when tests are failing unless the failure is explicitly understood and corrected.

---

## Rule 5 — Maintain a project ledger

Keep:

```text
docs/DEVELOPMENT_STATUS.md
```

containing:

* current phase
* completed features
* incomplete features
* important design decisions
* discovered issues
* test status
* next phase

Update it after every phase.

---

## Rule 6 — Keep an architecture decision record

Create:

```text
docs/adr/
```

Important architectural decisions must receive an ADR.

Examples:

* why PostgreSQL + pgvector
* why monotonic and wall clocks are both retained
* why evidence storage is immutable
* why PII is separated
* why Bitcoin anchoring is optional

---

# 10. PHASE 0 — REPOSITORY BOOTSTRAP

Create the complete repository skeleton.

Create:

* `pyproject.toml`
* package metadata
* dependencies
* developer dependencies
* `.gitignore`
* `.env.example`
* `README.md`
* configuration skeleton
* test directories
* Docker files
* GitHub Actions skeleton
* pre-commit configuration if useful

Create CLI:

```bash
truepass --help
```

Commands should eventually include:

```text
truepass run
truepass collect
truepass status
truepass verify
truepass doctor
truepass database
```

### Phase 0 acceptance criteria

The following must work:

```bash
python -m truepass --help
pytest
ruff check .
```

---

# 11. PHASE 1 — CORE EVENT MODEL

Implement the canonical TruePass event schema.

Required concepts:

```text
EventID
timestamp_ns
received_timestamp_ns
source
sensor_id
host
event_type
severity
confidence
features
metadata
provenance
```

Support domain-specific data while maintaining a common envelope.

Create event types for at least:

```text
PROCESS_STARTED
PROCESS_STOPPED
NETWORK_CONNECTION
LISTENING_PORT
DNS_EVENT
WIFI_EVENT
BLUETOOTH_EVENT
AUTH_EVENT
RF_OBSERVATION
RF_ANOMALY
INCIDENT
EVIDENCE_RECORD
```

Use enums.

Create canonical serialization.

Canonical serialization must produce deterministic bytes for evidence hashing.

Test serialization consistency.

---

# 12. PHASE 2 — CONFIGURATION AND OBSERVABILITY

Implement typed configuration.

Support:

```text
TOML
environment variables
safe defaults
```

Never store secrets in source control.

Add structured application logging.

Every important event should include contextual fields such as:

```text
component
sensor_id
event_id
host
correlation_id
```

Expose Prometheus metrics.

Examples:

```text
truepass_events_total
truepass_collector_errors_total
truepass_events_processing_seconds
truepass_rf_anomalies_total
truepass_incidents_total
```

---

# 13. PHASE 3 — PERSISTENT EVENT STORAGE

Implement PostgreSQL persistence.

Create SQLAlchemy models.

Use Alembic migrations.

Core tables:

```text
events
incidents
evidence_records
evidence_roots
sensor_registry
baselines
identity_profiles
```

Design indexes for:

```text
timestamp
event type
source
sensor
host
incident ID
```

Provide repository/service abstractions.

Add integration tests using a disposable PostgreSQL instance.

---

# 14. PHASE 4 — HOST AND PROCESS TELEMETRY

Build collectors for systems the operator is authorized to monitor.

Use `psutil` or safe OS interfaces.

Collect:

```text
process creation
process termination
PID
PPID
executable path
command metadata where permitted
username where appropriate
CPU usage
memory usage
socket ownership
```

Avoid collecting secrets from command lines without explicit configuration.

Establish process snapshots and change detection.

Generate normalized events.

---

# 15. PHASE 5 — NETWORK AND PORT TELEMETRY

Implement authorized local network telemetry.

Collect:

```text
listening TCP ports
listening UDP ports
established TCP connections
remote addresses
process ↔ socket relationships
interface state
routing changes where available
ARP/neighbor state
DNS observations where safely available
```

Core mapping:

```text
PROCESS
   ↓
PID
   ↓
SOCKET
   ↓
LOCAL PORT
   ↓
PROTOCOL
   ↓
REMOTE ADDRESS
```

Do not turn this into an offensive port-scanning framework.

Passive/local inventory comes first.

---

# 16. PHASE 6 — WI-FI TELEMETRY

Implement platform-adapted Wi-Fi collection.

Where supported gather:

```text
interface
SSID
BSSID
signal strength
channel
frequency
association state
authentication/security mode
connection/disconnection transitions
```

Generate events on meaningful state changes rather than continuously spamming duplicate records.

---

# 17. PHASE 7 — BLUETOOTH TELEMETRY

Treat Bluetooth as an independent telemetry domain.

Where platform APIs permit, observe:

```text
adapter state
known devices
discovered devices
connection state
service metadata
RSSI
device identifiers
```

Normalize events.

Do not assume an observed Bluetooth device is malicious.

---

# 18. PHASE 8 — APPEND-ONLY FORENSIC LEDGER

Implement an append-only evidence chain.

For record `n`:

```text
H(n) = SHA256(
    H(n-1) || canonical_event_bytes(n)
)
```

Store:

```text
sequence
event_id
previous_hash
event_hash
timestamp
canonicalization_version
```

Implement verification.

Command:

```bash
truepass verify ledger
```

must detect tampering.

Create tests proving that modification of any historical event invalidates the chain.

---

# 19. PHASE 9 — SDR INFRASTRUCTURE

Create an SDR abstraction.

The software must run even when physical SDR hardware is unavailable.

Implement:

```text
SDRSource protocol/interface
RealSoapySDRSource
FileIQSource
SyntheticIQSource
```

This enables development and testing without hardware.

Support configuration for:

```text
sample rate
center frequency
gain
buffer size
device
```

---

# 20. PHASE 10 — SPECTRUM DSP PIPELINE

Implement:

```text
I/Q samples
   ↓
windowing
   ↓
FFT
   ↓
PSD
   ↓
spectrogram
```

Provide tested numerical functions.

Support common windows:

```text
Hann
Blackman
```

Generate frequency-bin metadata.

Handle units consistently.

Avoid unnecessary copying of large arrays.

---

# 21. PHASE 11 — RF FEATURE EXTRACTION

Extract measurable features such as:

```text
center frequency
bandwidth
peak power
average power
noise floor
spectral entropy
occupied bandwidth
burst duration
duty cycle
frequency drift
spectral centroid
spectral flatness
periodicity
time between bursts
amplitude-envelope statistics
spectral-shape descriptors
```

Create an `RFFeatureVector` model.

Store feature-definition version metadata.

Tests must use synthetic signals with known characteristics.

---

# 22. PHASE 12 — RF BASELINE ENGINE

Develop baseline learning.

The baseline should characterize expected behavior rather than classify everything unfamiliar as malicious.

Support:

```text
rolling statistics
time-of-day baseline
frequency-band baseline
sensor-specific baseline
```

Persist baseline versions.

Baselines must include:

```text
creation time
training period
feature schema
sample count
model parameters
```

---

# 23. PHASE 13 — CLUSTERING AND ANOMALY DETECTION

Implement multiple detectors behind common interfaces.

Start with:

```text
Isolation Forest
DBSCAN
statistical distance
```

Then add X-means or an appropriate maintained implementation/compatible equivalent.

Do not hard-code:

```text
unknown cluster == attacker
```

The proper interpretation is:

```text
unknown cluster == observation requiring additional correlation
```

Each detector must return:

```text
score
model ID
reason/features
confidence where meaningful
```

---

# 24. PHASE 14 — UNIFIED STATE-IN-EVENT-SPACE

Create a timeline engine that can retrieve all observations surrounding an event.

Example:

```text
10:21:03.120 RF burst
10:21:03.181 Wi-Fi association
10:21:03.203 TCP connection
10:21:03.219 process spawn
10:21:03.241 authentication event
```

Support queries such as:

```python
timeline.around(
    event_id,
    before_ms=500,
    after_ms=500,
)
```

Time synchronization and clock quality must be explicit.

Retain provenance.

---

# 25. PHASE 15 — TEMPORAL CORRELATION ENGINE

Build the central TruePass correlation engine.

Correlation factors may include:

```text
time proximity
host equality
device relationship
network relationship
process/socket relationship
RF similarity
historical co-occurrence
identity context
sensor reliability
```

Do not simply sum arbitrary numbers.

Create configurable and testable scoring logic.

Every correlation result must include an explanation.

Example:

```json
{
  "score": 0.91,
  "reasons": [
    "RF anomaly occurred 43 ms before new Wi-Fi association",
    "new TCP connection appeared 21 ms later",
    "socket belongs to newly-created process"
  ]
}
```

---

# 26. PHASE 16 — INCIDENT SCORING

Develop transparent incident scoring.

Consider dimensions such as:

```text
novelty
temporal correlation
asset sensitivity
identity context
network behavior
host behavior
RF anomaly strength
historical similarity
sensor confidence
```

Return:

```text
score
severity
confidence
evidence IDs
candidate explanations
```

Example severity levels:

```text
INFO
LOW
MEDIUM
HIGH
CRITICAL
```

Scores must never falsely claim mathematical certainty.

---

# 27. PHASE 17 — EVENT GRAPH

Implement an event/entity graph.

Initial implementation may use NetworkX.

Entity types:

```text
RF_SIGNAL
DEVICE
HOST
PROCESS
SOCKET
REMOTE_HOST
IDENTITY
INCIDENT
```

Relationship examples:

```text
TEMPORALLY_NEAR
OBSERVED_BY
RUNS_ON
OWNS_SOCKET
CONNECTED_TO
ASSOCIATED_WITH
DERIVED_FROM
PART_OF_INCIDENT
```

Enable candidate entry-path ranking.

Example:

```text
1. Wi-Fi → host → process          0.87
2. Bluetooth → service → process   0.51
3. USB → executable                0.22
4. isolated RF observation         0.16
```

Clearly label this as candidate ranking rather than proof.

---

# 28. PHASE 18 — VECTOR SIMILARITY SEARCH

Enable PostgreSQL `pgvector`.

Create embeddings or numerical feature vectors for:

```text
RF observations
network observations
process behaviors
device states
incidents
```

Vector search answers:

> Have we seen something similar before?

Do not use the vector store as authoritative evidence storage.

The relational event/evidence records remain canonical.

Implement similarity APIs and tests.

---

# 29. PHASE 19 — EVIDENCE MERKLE TREES

Periodically batch immutable event hashes.

Construct a Merkle tree.

Store:

```text
batch ID
first sequence
last sequence
leaf count
root hash
creation timestamp
algorithm
```

Implement inclusion proofs.

Add:

```bash
truepass verify merkle <batch-id>
```

---

# 30. PHASE 20 — CRYPTOGRAPHIC SIGNING

Add optional signing of evidence roots.

Use maintained modern cryptographic libraries.

Keys must be generated securely.

Private keys must never be logged.

Support external/hardware key backends through clean interfaces later.

Document:

* algorithms
* formats
* threat model
* rotation strategy

---

# 31. PHASE 21 — OPTIONAL BITCOIN TIMESTAMP ANCHORING

This phase is optional and isolated.

Do not build a wallet from biometric information.

Do not put PII on-chain.

Implement an abstraction:

```python
class TimestampAnchor:
    async def anchor(self, digest: bytes) -> AnchorReceipt:
        ...
```

Allow implementations such as:

```text
NoOpAnchor
FileAnchor
BitcoinAnchor
```

Only anchor cryptographic commitments such as a Merkle root.

Never require Bitcoin for normal TruePass operation.

---

# 32. PHASE 22 — IDENTITY ARCHITECTURE

Identity remains separate from telemetry and evidence key generation.

Potential authentication factors:

```text
device possession
OS credential
optional face verification
optional voice verification
behavioral characteristics
```

Conceptually:

```text
User
 ↓
TruePass verification
 ↓
policy threshold
 ↓
OS keystore / TPM / hardware wallet
 ↓
authorized cryptographic operation
```

Build pluggable factor interfaces.

Default installations should not require biometrics.

Consent must be explicit.

---

# 33. PHASE 23 — API

Build a FastAPI service.

Required endpoint groups:

```text
/health
/metrics
/events
/incidents
/sensors
/timeline
/correlation
/evidence
/baselines
/similarity
/system
```

Implement:

* validation
* pagination
* filtering
* consistent error schemas
* OpenAPI documentation
* authentication hooks
* rate limiting where appropriate

---

# 34. PHASE 24 — DASHBOARD

Build an operator dashboard.

It must expose at minimum:

```text
system health
collector status
event rate
current RF spectrum
spectrogram
RF anomalies
process/network events
incident timeline
incident scores
correlation explanation
candidate entry paths
historical similar events
evidence integrity status
```

Do not overload the dashboard with meaningless animation.

Optimize for forensic interpretation.

---

# 35. PHASE 25 — ALERTING

Build configurable alerts.

Possible triggers:

```text
high incident score
RF anomaly + host change
new listening port
unexpected process/socket relationship
ledger verification failure
sensor failure
```

Alert payloads must explain **why** the alert occurred.

Avoid alert spam.

Implement deduplication and cooldowns.

---

# 36. PHASE 26 — VOICE / ECHO RESEARCH MODULE

Keep this outside the trusted security core.

Architecture:

```text
microphone
   ↓
VAD
   ↓
speech-to-text
   ↓
NLP
   ↓
intent classifier
   ↓
policy engine
   ↓
assistant
   ↓
text-to-speech
```

Potential anti-spoofing research telemetry:

```text
speaker verification
replay detection
synthetic voice detection
device identity
challenge-response
```

Never treat voice alone as sufficient proof of identity.

Mark the module experimental.

---

# 37. PHASE 27 — EEG RESEARCH MODULE

This is also isolated from the production cybersecurity core.

Pipeline:

```text
EEG input
   ↓
filtering
   ↓
artifact removal
   ↓
feature extraction
   ↓
temporal model
   ↓
constrained classification
   ↓
candidate symbols/categories
```

Use synthetic/public research data unless the operator explicitly provides lawful, consented data.

Never describe the output as unrestricted mind reading.

No stimulation functionality.

---

# 38. PHASE 28 — SECURITY HARDENING

Perform a structured security review.

Threat-model:

```text
malicious telemetry
database compromise
log tampering
event replay
API abuse
privilege escalation
secret leakage
supply-chain dependency compromise
collector impersonation
clock manipulation
evidence deletion
malformed RF data
denial of service
```

Implement mitigations where appropriate.

Use least privilege.

Collectors should not require administrator/root access unless the operating-system capability genuinely requires it.

Document elevated privileges.

---

# 39. PHASE 29 — PRIVACY AND DATA GOVERNANCE

Separate storage logically:

```text
identity/
biometrics/
behavior/
security/
telemetry/
forensics/
```

Implement data-retention policy configuration.

Document:

```text
what is collected
why it is collected
where it is stored
retention duration
how it is deleted
what cannot be deleted from external anchors
```

Public-chain anchoring must contain no raw personal data.

---

# 40. PHASE 30 — TESTING

Reach comprehensive coverage of critical logic.

Required test families:

```text
unit
integration
database
API
DSP
correlation
evidence integrity
configuration
security regression
synthetic end-to-end
```

Synthetic end-to-end scenario:

```text
1. synthetic RF burst
2. simulated Wi-Fi state change
3. simulated process creation
4. simulated socket connection
5. correlation engine associates events
6. incident receives score
7. incident is written to DB
8. evidence hash is chained
9. Merkle proof is generated
10. API returns incident
```

The scenario must run automatically.

---

# 41. PHASE 31 — PERFORMANCE TESTING

Benchmark:

```text
events/sec
DB insert throughput
timeline query latency
correlation latency
FFT throughput
spectrogram processing
vector-query latency
memory consumption
```

Avoid optimizing blindly.

Record benchmark results under:

```text
docs/benchmarks/
```

---

# 42. PHASE 32 — DOCKER AND DEPLOYMENT

Create production-capable Docker configuration.

Docker Compose should provide at least:

```text
TruePass API
PostgreSQL
pgvector
Prometheus if enabled
dashboard if separately deployed
```

Support persisted volumes.

Provide health checks.

Run containers as non-root wherever practical.

---

# 43. PHASE 33 — DOCUMENTATION

Create complete documentation.

Required:

```text
README.md
docs/ARCHITECTURE.md
docs/INSTALLATION.md
docs/CONFIGURATION.md
docs/SECURITY.md
docs/PRIVACY.md
docs/EVIDENCE_MODEL.md
docs/RF_PIPELINE.md
docs/CORRELATION_ENGINE.md
docs/API.md
docs/DEVELOPMENT.md
docs/TROUBLESHOOTING.md
docs/THREAT_MODEL.md
docs/DEVELOPMENT_STATUS.md
```

README must contain:

```text
what TruePass is
what it is not
architecture
requirements
quick start
Docker start
local development
tests
limitations
security notice
authorization notice
```

---

# 44. PHASE 34 — CI/CD

Configure GitHub Actions.

Pipeline:

```text
install
   ↓
format check
   ↓
lint
   ↓
type check
   ↓
unit tests
   ↓
integration tests
   ↓
security/dependency checks
   ↓
Docker build
```

Pin workflows appropriately.

Do not commit secrets.

---

# 45. PHASE 35 — FINAL INTEGRATION

Connect all completed components.

Final production pipeline:

```text
                     SDR
                      │
                      ▼
               Spectrum Analyzer
                      │
                      ▼
                  RF Baseline
                      │
                      ▼
            Clustering / Anomaly
                      │
        ┌─────────────┴────────────┐
        │                          │
OS Logs ───────────────┐           │
Processes ─────────────┤           │
Ports ─────────────────┤           │
Connections ───────────┼──► EVENT CORRELATOR
Wi-Fi ─────────────────┤           │
Bluetooth ──────────────┘           │
                                    ▼
                              INCIDENT SCORE
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
              Event Database                  Hash Chain
                    │                               │
                    ▼                               ▼
                 pgvector                      Merkle Root
                                                    │
                                                    ▼
                                            Optional Anchor
```

Test actual flow end-to-end.

---

# 46. PHASE 36 — RELEASE CANDIDATE

Before declaring success:

Run:

```text
all linters
all type checks
all unit tests
all integration tests
all synthetic E2E tests
migration test
Docker build
Docker Compose startup
API smoke tests
ledger verification
Merkle verification
```

Fix every critical failure.

Review:

```text
security
privacy
cryptography
permissions
dependency vulnerabilities
documentation
configuration defaults
error handling
```

Produce:

```text
docs/RELEASE_CHECKLIST.md
```

---

# 47. PHASE 37 — FINAL RELEASE

Prepare:

```text
CHANGELOG.md
version number
release notes
migration notes
known limitations
security notes
sample configuration
```

Tag the first complete release:

```text
TruePass v1.0.0
```

Do not call the system complete merely because the primary Python modules exist.

Completion requires the entire Definition of Done below.

---

# 48. DEFINITION OF DONE

TruePass is complete only when all of the following are true.

## Foundation

* repository installs successfully
* configuration works
* CLI works
* tests execute cleanly

## Event Space

* canonical event model works
* serialization is deterministic
* timestamps are normalized
* provenance is preserved

## Host Telemetry

* process collection works
* network collection works
* port inventory works
* process/socket mapping works

## Wireless Telemetry

* Wi-Fi collector architecture works
* Bluetooth collector architecture works
* unsupported-platform behavior fails gracefully

## SDR

* real-device abstraction exists
* replay-file source exists
* synthetic source exists
* FFT works
* PSD works
* spectrogram works
* RF features work

## Detection

* baseline engine works
* anomaly engine works
* clustering works
* unknown observations remain observations rather than automatic threat labels

## Correlation

* timeline engine works
* cross-domain correlation works
* incident scoring works
* explanations accompany scores
* candidate paths can be ranked

## Storage

* PostgreSQL works
* migrations work
* pgvector works
* similarity search works

## Forensics

* hash chain works
* tampering detection works
* Merkle roots work
* inclusion verification works
* signing works if enabled

## Privacy

* identity is separated from telemetry
* biometric handling is optional
* PII is not used as key entropy
* PII is not placed on public blockchains

## API

* OpenAPI works
* endpoints are tested
* pagination/filtering work
* errors are standardized

## Dashboard

* live/system state is visible
* incidents can be investigated
* timelines are visible
* evidence integrity can be checked

## Operational Quality

* Docker works
* Compose works
* CI passes
* metrics exist
* logs are structured
* documentation is complete

## Security

* threat model exists
* secrets are externalized
* least privilege is documented
* unsafe active-response capabilities are absent by default

## Quality

* lint passes
* type checks pass
* tests pass
* end-to-end test passes
* no critical placeholder code remains

---

# DEVELOPMENT ORDER

The implementation sequence is mandatory unless a dependency genuinely forces a minor change:

```text
01. Event schema + nanosecond timestamping
02. OS/process/network collector
03. Listening-port inventory
04. Append-only SHA-256 forensic log
05. SDR FFT/spectrogram pipeline
06. RF baseline
07. RF clustering/anomaly detection
08. Cross-domain temporal correlation
09. Incident scoring
10. PostgreSQL + pgvector similarity
11. Merkle evidence tree
12. Optional Bitcoin timestamp anchor
13. Dashboard
14. Identity verification
15. Voice/NLP experimental research
16. EEG experimental research
17. Hardening
18. Deployment
19. Documentation
20. Release
```

Do not start with the exotic modules.

Build the system capable of reliably saying:

> Something changed, where it changed, when it changed, what else happened at approximately the same time, and exactly what evidence supports that conclusion.

That is the central engineering objective.

---

# REQUIRED WORKFLOW FOR EVERY PHASE

At the beginning of each phase, output:

```text
PHASE:
GOAL:
DEPENDENCIES:
FILES TO CREATE:
FILES TO MODIFY:
ACCEPTANCE CRITERIA:
```

Then implement it.

After implementation, output:

```text
IMPLEMENTED:
TESTS ADDED:
COMMANDS TO VERIFY:
KNOWN LIMITATIONS:
NEXT PHASE:
```

Do not merely describe files.

Create their complete contents.

---

# ERROR-HANDLING RULE

If something fails:

1. inspect the actual error,
2. identify the root cause,
3. repair it,
4. rerun validation,
5. preserve already-working behavior,
6. continue.

Do not abandon the project because one dependency or operating-system feature is unavailable.

Provide graceful fallbacks where scientifically and technically reasonable.

---

# HARDWARE-INDEPENDENCE RULE

TruePass must be developable and testable without:

* an SDR
* special Bluetooth hardware
* a Wi-Fi adapter supporting monitor mode
* EEG hardware
* Bitcoin funds

Use abstractions, fixture data, replay files, simulation, and synthetic signals.

Real hardware integrations should plug into those same interfaces.

---

# SECURITY LANGUAGE RULE

Never display an RF anomaly as:

```text
ATTACKER DETECTED
```

unless independent evidence genuinely supports an incident classification.

Prefer:

```text
RF anomaly detected
Cross-domain correlation: HIGH
Security-relevant host changes: 3
Recommended action: investigate
```

Evidence must drive conclusions.

---

# INCIDENT EXPLANATION FORMAT

Every significant incident should eventually be representable like:

```text
Incident: TP-23991

RF observation:
    center frequency: 2437 MHz
    anomaly score: 0.81

Host event +38 ms:
    process created
    PID: 9184

Network event +45 ms:
    outbound TCP connection established

Identity/security event +71 ms:
    privilege-sensitive operation observed

Correlation:
    0.93

Candidate entry path:
    Wi-Fi → host → process → socket

Assessment:
    investigate

Evidence:
    event IDs [...]
    ledger range [...]
    Merkle batch [...]

Important:
    correlation does not independently establish causation.
```

---

# FINAL INSTRUCTION

Begin with **Phase 0**.

Do not jump ahead.

Create the project as real software.

At each phase:

* implement the code,
* add tests,
* run validation,
* repair problems,
* update documentation,
* preserve backward compatibility,
* then advance.

Continue through every phase until the project satisfies the full Definition of Done and is ready to be tagged:

```text
TruePass v1.0.0
```

The finished system must be technically defensible, privacy-aware, testable without specialized hardware, evidence-driven, and safe by default.

The guiding principle throughout development is:

> **Observe → timestamp → normalize → correlate → score → preserve evidence → alert.**


-----------------------------------------------------------------------------


# TruePass™ / TRUE-PASS-AGE™

## Complete End-to-End Autonomous Development Prompt

You are the principal software architect, senior Python engineer, cybersecurity engineer, DSP engineer, ML engineer, frontend engineer, UX engineer, database engineer, DevOps engineer, QA engineer, and technical writer responsible for developing the entire **TruePass™** ecosystem from an empty repository to a complete, runnable, tested, documented release.

The finished ecosystem must include three tightly integrated user-facing applications:

```text
TruePass™
    │
    ├── TruePass Control Center
    │       Main GUI / operations dashboard
    │
    ├── TruePass-Scan™
    │       Authorized host/network/RF observation console
    │
    └── TRUE-PASS-AGE™
            Forensic ledger and evidence verification viewer
```

The project must be developed completely, phase by phase, until all backend services, collectors, analytics, databases, APIs, dashboards, tests, deployment infrastructure, and documentation satisfy the final Definition of Done.

---

# 1. CORE ENGINEERING PRINCIPLE

Everything follows:

> **Observe → timestamp → normalize → correlate → score → preserve evidence → visualize → alert.**

No individual observation automatically proves compromise.

An RF anomaly alone is not proof of intrusion.

An unknown cluster alone is not an attacker.

A network connection alone is not malicious.

TruePass must correlate independent observations and make the evidence visible to the operator.

---

# 2. PRODUCT FAMILY

The complete product contains:

```text
┌───────────────────────────────────────────────────────────────┐
│                         TruePass™                             │
│                                                               │
│   Security telemetry + correlation + evidence platform       │
│                                                               │
├───────────────────────┬───────────────────────┬───────────────┤
│ TRUEPASS CONTROL      │ TRUEPASS-SCAN™        │ TRUE-PASS-AGE™│
│ CENTER                │                       │               │
│                       │ Authorized scanning,  │ Evidence &    │
│ Operations dashboard  │ telemetry and sensor │ ledger viewer │
│                       │ observation console   │               │
└───────────────────────┴───────────────────────┴───────────────┘
                          │
                          ▼
                    FastAPI Backend
                          │
          ┌───────────────┼─────────────────┐
          ▼               ▼                 ▼
       PostgreSQL      pgvector       Evidence Ledger
          │               │                 │
          └───────────────┼─────────────────┘
                          ▼
                Correlation / ML Engine
                          │
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
   OS/Network            SDR             Wi-Fi/BLE
   Collectors         Spectrum           Collectors
```

---

# 3. REQUIRED USER INTERFACE STACK

Create a modern desktop-quality web GUI.

Preferred frontend stack:

```text
Frontend              React
Language              TypeScript
Build system          Vite
Component framework   Material UI or equivalent
Charts                 Plotly.js
State                  React Query + lightweight local state
API                    REST/WebSocket through FastAPI
Tables                 virtualized where necessary
Testing                Vitest + React Testing Library
E2E                    Playwright
```

Do not render the entire application server-side through Python templates.

The Python backend remains responsible for:

* data acquisition
* security
* correlation
* signal processing
* ML
* database access
* evidence integrity
* authentication/authorization

The frontend is responsible for:

* visualization
* operator workflows
* interactive analysis
* filtering
* navigation
* evidence exploration

---

# 4. GUI DESIGN PRINCIPLES

The UI must be designed for investigative clarity.

Priorities:

1. Evidence first.
2. Explain scores.
3. Show time relationships.
4. Avoid alarm fatigue.
5. Differentiate observation from conclusion.
6. Make raw evidence accessible.
7. Clearly indicate sensor/data confidence.
8. Preserve provenance.
9. Allow rapid drill-down.
10. Never make speculative findings look certain.

Every major score must have a visible:

```text
WHY?
```

action.

Example:

```text
Incident Risk
████████████████░░░░ 82 / 100

Classification
HIGH — INVESTIGATE

Why?

✓ Previously unseen RF cluster
✓ New Wi-Fi association +38 ms
✓ New process +62 ms
✓ Outbound connection +77 ms

No confirmed causal relationship established.
```

---

# 5. MAIN APPLICATION SHELL

Create a common navigation system.

Desktop layout:

```text
┌─────────────────────────────────────────────────────────────────┐
│ TRUEPASS™                                         ● HEALTHY     │
├────────────────┬────────────────────────────────────────────────┤
│                │                                                │
│ Dashboard      │                                                │
│ Live Monitor   │              ACTIVE VIEW                       │
│ TruePass-Scan  │                                                │
│ Spectrum       │                                                │
│ Timeline       │                                                │
│ Incidents      │                                                │
│ Devices        │                                                │
│ Processes      │                                                │
│ Network        │                                                │
│ Evidence       │                                                │
│ TRUE-PASS-AGE  │                                                │
│ Sensors        │                                                │
│ Models         │                                                │
│ Settings       │                                                │
│                │                                                │
└────────────────┴────────────────────────────────────────────────┘
```

Navigation must support deep links.

Example:

```text
/incidents/TP-23991

/scan/session/SCN-91822

/ledger/event/01JABC...

/spectrum/sensor/sdr-01
```

---

# 6. TRUEPASS CONTROL CENTER

The main dashboard is the operator's starting point.

Create:

```text
/dashboard
```

It must contain:

## System status

Display:

* API status
* PostgreSQL status
* collectors
* SDR sensors
* Wi-Fi collectors
* BLE collectors
* evidence ledger
* vector search
* correlation engine
* clock synchronization health

Example:

```text
SYSTEM HEALTH

API                 ● Healthy
Database            ● Healthy
SDR-01              ● Running
Network Collector   ● Running
Wi-Fi               ● Running
Bluetooth           ● Running
Ledger              ● Verified
Correlation Engine  ● Running
```

---

# 7. SECURITY OVERVIEW

Display summary cards:

```text
Events / min

RF anomalies

Network changes

Processes created

Open ports

Active incidents

Critical incidents

Ledger verification status
```

Support:

```text
last 5 minutes
last hour
last 24 hours
custom
```

---

# 8. LIVE EVENT MONITOR

Create:

```text
/live
```

Display incoming normalized events in near-real time through WebSocket/SSE.

Example:

```text
TIME             SOURCE       EVENT                   SCORE

17:41:03.120     SDR          RF anomaly              0.81
17:41:03.181     Wi-Fi        Association changed
17:41:03.203     Network      TCP connection
17:41:03.219     Process      Process started
17:41:03.241     Security     Privilege event
```

Allow:

* pause stream
* resume
* search
* source filter
* event filter
* host filter
* severity filter
* export selected records
* inspect raw JSON
* open timeline

Do not drop events merely because the GUI cannot render them fast enough.

Use virtualized tables.

---

# 9. INCIDENT DASHBOARD

Create:

```text
/incidents
```

and:

```text
/incidents/{incident_id}
```

Overview columns:

```text
Incident
Time
Host
Severity
Score
Evidence Count
Status
```

Detail page:

```text
TP-23991

Risk: HIGH
Score: 0.93
Confidence: 0.86

Status:
INVESTIGATE

Candidate Entry Path:

Wi-Fi
  ↓
Host
  ↓
Process PID 9184
  ↓
Socket
  ↓
Remote Host
```

Display:

* evidence
* timeline
* candidate entry paths
* correlation reasons
* similar incidents
* RF context
* network context
* process context
* integrity verification

---

# 10. INTERACTIVE EVENT TIMELINE

Create an interactive visualization.

Example:

```text
RF        ─────●─────────────────────────────────────

Wi-Fi     ─────────●─────────────────────────────────

Process   ─────────────●─────────────────────────────

Network   ───────────────●───────────────────────────

Auth      ──────────────────●────────────────────────

          -100 ms        event             +100 ms
```

Features:

* zoom
* pan
* event grouping
* domain filters
* tooltip evidence
* correlation lines
* jump to raw event
* highlight incident window

Allow selection of:

```text
±50 ms
±100 ms
±500 ms
±1 second
±10 seconds
custom
```

---

# 11. SPECTRUM DASHBOARD

Create:

```text
/spectrum
```

This is the primary SDR visualization.

Required widgets:

### Live spectrum

```text
Power
  │
  │       ╭─╮
  │   ╭───╯ ╰──╮
  │───╯         ╰────────────
  └──────────────────────────── Frequency
```

### Waterfall / spectrogram

Time × Frequency × Power.

### Sensor panel

Display:

```text
Sensor
Center frequency
Sample rate
Gain
Bandwidth
Noise floor
State
```

### RF features

Display:

```text
spectral centroid
spectral entropy
occupied bandwidth
flatness
peak power
noise floor
burst duration
duty cycle
```

### Anomaly overlay

Anomalies must be highlighted visually.

Selecting an anomaly opens its event record.

---

# 12. RF CLUSTER EXPLORER

Create:

```text
/spectrum/clusters
```

Display RF feature clusters.

Use:

* 2D projection
* PCA
* optional UMAP
* known/unknown cluster markers

Example:

```text
             ○ ○ ○
         ○ ○ ○ ○

                     △ △
                   △ △ △

       ×

× = new/unclassified observation
```

Operators must be able to:

* select cluster
* inspect members
* see feature distributions
* compare cluster with baseline
* view related incidents

Never label an unknown cluster automatically as an attacker.

---

# 13. TRUEPASS-SCAN™

Develop **TruePass-Scan™** as a dedicated authorized observation and local security inventory interface.

Create:

```text
/scan
```

TruePass-Scan is not an offensive exploitation platform.

It is intended for:

* owned machines
* authorized assets
* laboratory environments
* local inventory
* defensive assessment
* telemetry inspection

---

# 14. TRUEPASS-SCAN HOME

Display:

```text
TRUEPASS-SCAN™

Target Environment

● Local Host
○ Authorized Asset Group
○ Laboratory

─────────────────────────────

Network Interfaces

Ethernet0        192.168.x.x
Wi-Fi            192.168.x.x
Bluetooth        Enabled

─────────────────────────────

[ START AUTHORIZED OBSERVATION ]
```

Require the user to acknowledge:

> I am authorized to inspect the selected assets.

Store the acknowledgement in scan-session metadata.

---

# 15. TRUEPASS-SCAN SESSION MODEL

Every scan/observation run gets:

```text
scan_id
started_at
completed_at
operator
scope
authorization_acknowledgement
host list
collector configuration
results
evidence references
```

Example:

```text
SCN-2026-0913-00021
```

---

# 16. TRUEPASS-SCAN HOST VIEW

Display:

```text
HOST
workstation-01

OS
Windows/Linux/macOS

IP
192.168.1.25

────────────────────────

Processes        183
Listening TCP     17
Listening UDP     22
Connections       31
Wi-Fi             Active
Bluetooth         Active
Alerts             2
```

---

# 17. TRUEPASS-SCAN PORT VIEWER

Create:

```text
/scan/{scan_id}/ports
```

Display:

```text
Protocol
Local address
Port
State
PID
Process
User
First seen
Last seen
Baseline status
```

Example:

```text
TCP  0.0.0.0     8000 LISTEN  9184 python.exe  expected
TCP  0.0.0.0     7331 LISTEN  6133 unknown.exe NEW
```

Newly observed ports should be visually distinguishable from baseline ports.

Allow:

```text
Show all
New
Changed
Expected
Unattributed
```

---

# 18. PROCESS ↔ SOCKET EXPLORER

TruePass-Scan must visualize:

```text
PROCESS
   │
   ▼
PID
   │
   ▼
SOCKET
   │
   ├── local endpoint
   │
   └── remote endpoint
```

Example:

```text
python.exe
PID 9184
   │
   ├── TCP :8000 LISTEN
   │
   └── TCP 192.168.1.25:52118
                     │
                     ▼
                remote host
```

Clicking any node should open related evidence.

---

# 19. TRUEPASS-SCAN DEVICE INVENTORY

Create:

```text
/scan/devices
```

Combine known observations from:

* host
* interfaces
* Wi-Fi
* Bluetooth
* SDR correlations

Display:

```text
Device ID
Type
First Seen
Last Seen
Address
Signal
Trust State
Related Events
```

Do not pretend RF identification proves device ownership.

---

# 20. TRUEPASS-SCAN DIFFERENTIAL MODE

A key feature must be:

```text
COMPARE WITH BASELINE
```

Example:

```text
BEFORE                     NOW

15 TCP listeners            17 TCP listeners
82 processes                84 processes
4 BLE devices                5 BLE devices
6 known Wi-Fi peers          7 Wi-Fi peers

CHANGES

+ TCP :7331
+ process unknown.exe
+ Bluetooth device XX:XX...
```

Every difference should link to supporting evidence.

---

# 21. TRUEPASS-SCAN SESSION REPORT

Generate a report containing:

```text
scan metadata
scope
authorization statement
hosts
interfaces
processes
ports
network connections
device observations
RF anomalies
correlated incidents
evidence hashes
ledger references
```

Support export to:

```text
JSON
CSV where appropriate
PDF report
```

The exported report must clearly distinguish:

```text
observed fact

derived finding

model inference

operator note
```

---

# 22. TRUE-PASS-AGE™ LEDGER VIEWER

Develop **TRUE-PASS-AGE™** as the visual forensic evidence subsystem.

Create:

```text
/ledger
```

Its primary purpose is to answer:

> Is this evidence authentic and unchanged according to the TruePass evidence chain?

---

# 23. LEDGER OVERVIEW

Display:

```text
TRUE-PASS-AGE™

Ledger Status
● VERIFIED

Total Records
1,842,921

Latest Sequence
1,842,921

Current Chain Hash
7fa926...b810

Merkle Batches
1,823

Signed Roots
1,821

External Anchors
412
```

---

# 24. LEDGER RECORD EXPLORER

Create:

```text
/ledger/events
```

Columns:

```text
Sequence
Timestamp
Event ID
Event Type
Source
Previous Hash
Event Hash
Verification
```

Example:

```text
1842920
17:41:03.219
01J...
PROCESS_STARTED
process-collector-01

Previous:
937f2d...

Hash:
da928c...

✓ VERIFIED
```

---

# 25. HASH CHAIN VISUALIZATION

Create visual representation:

```text
┌───────────┐
│ Event 100 │
└─────┬─────┘
      │
      ▼
    SHA256
      │
      ▼
┌───────────┐
│ Hash 100  │
└─────┬─────┘
      │
      ├─────────────┐
      ▼             │
┌───────────┐       │
│ Event 101 │       │
└─────┬─────┘       │
      │             │
      └──── combine ┘
             │
             ▼
           SHA256
             │
             ▼
        ┌──────────┐
        │ Hash 101 │
        └──────────┘
```

Allow operator to step backward/forward through records.

---

# 26. LEDGER VERIFICATION UI

Provide:

```text
VERIFY LEDGER
```

with progress display.

Results:

```text
Ledger Verification

Records checked: 1,842,921

Hash links:
✓ VALID

Canonical event hashes:
✓ VALID

Sequence:
✓ VALID

Merkle references:
✓ VALID

Signatures:
✓ VALID

Overall:
VERIFIED
```

If corruption occurs:

```text
⚠ LEDGER INTEGRITY FAILURE

First invalid sequence:
1,501,337

Expected previous hash:
...

Observed previous hash:
...

Affected downstream records:
341,584
```

Do not silently repair forensic evidence.

---

# 27. MERKLE TREE VIEWER

Create:

```text
/ledger/merkle/{batch_id}
```

Visualize tree relationships.

Example:

```text
                    ROOT
                     │
              ┌──────┴──────┐
              │             │
             H01           H23
           ┌──┴──┐       ┌──┴──┐
          H0    H1      H2     H3
          │      │       │      │
         E0     E1      E2     E3
```

Selecting a leaf shows:

```text
Event
Leaf Hash
Sibling Hashes
Computed Root
Stored Root
Verification
```

---

# 28. INCLUSION PROOF VIEWER

Allow operator to select any event and choose:

```text
Generate Merkle Proof
```

Display:

```text
Event ID
Leaf hash
Merkle path
Root
Batch
Signature
External anchor
```

Provide:

```text
VERIFY PROOF
```

Result:

```text
✓ Event belongs to Merkle batch MB-0001823
✓ Merkle root verified
✓ signature verified
```

---

# 29. SIGNATURE VIEWER

Where roots are signed, display:

```text
Algorithm
Key ID
Public key fingerprint
Signature
Signing timestamp
Verification result
```

Never display private keys.

---

# 30. EXTERNAL ANCHOR VIEWER

If optional Bitcoin anchoring is enabled, show:

```text
Anchor Type
Bitcoin

Merkle Root
7fa926...b810

Transaction Reference
...

Submitted
...

Confirmed
...

Confirmations
...
```

The UI must explicitly state:

> The blockchain contains a cryptographic commitment, not the underlying private evidence.

Bitcoin functionality must remain optional.

---

# 31. EVIDENCE PROVENANCE PANEL

Every event page must contain:

```text
PROVENANCE

Collected by:
process-collector-01

Sensor:
workstation-01

Original timestamp:
...

Received:
...

Canonicalization:
v1

Ledger sequence:
1842920

Hash:
...

Merkle batch:
MB-1823

Integrity:
VERIFIED
```

---

# 32. EVIDENCE DIFF VIEWER

When a verification failure exists, provide forensic comparison:

```text
EXPECTED                         OBSERVED

event_type                       event_type
PROCESS_STARTED                  PROCESS_STARTED

pid
9184                             9184

executable
python.exe                       python-modified.exe
                                 ^^^^^^^^^^^^^^^^^^^
```

Do not modify either copy.

---

# 33. GLOBAL SEARCH

Add global search.

Shortcut:

```text
Ctrl/Cmd + K
```

Search:

```text
Event ID
Incident ID
Scan ID
Host
PID
Process name
IP
Port
Frequency
Device
Hash
Merkle root
```

Example:

```text
> 9184

Process PID 9184
Incident TP-23991
Events: 18
Sockets: 3
Ledger records: 24
```

---

# 34. INVESTIGATION WORKSPACE

Allow operators to create temporary investigation workspaces.

Example:

```text
INV-2026-0031

Selected evidence:

✓ RF-9211
✓ WIFI-2831
✓ PROC-9921
✓ NET-1892
✓ AUTH-1898
```

Allow:

* notes
* tags
* bookmarks
* timeline
* evidence collection
* incident linking

Operator notes must remain clearly separate from immutable sensor evidence.

---

# 35. GUI ALERT CENTER

Create:

```text
/alerts
```

Display:

```text
Time
Severity
Host
Detector
Reason
Status
```

Possible states:

```text
NEW
ACKNOWLEDGED
INVESTIGATING
RESOLVED
FALSE_POSITIVE
```

Changing alert state must not rewrite underlying evidence.

---

# 36. GUI SENSOR MANAGEMENT

Create:

```text
/sensors
```

Display:

```text
Sensor
Type
Host
Status
Last Event
Clock Offset
Event Rate
Errors
```

Sensor detail pages must show:

* configuration
* health
* version
* capabilities
* recent events
* errors

Sensitive credentials must never appear.

---

# 37. GUI MODEL MANAGEMENT

Create:

```text
/models
```

Display:

```text
Model
Version
Feature Schema
Training Period
Created
Status
```

For each anomaly/baseline model show:

```text
training dataset period
number of samples
parameters
feature version
model hash
```

Never silently replace a forensic model version.

---

# 38. GUI CONFIGURATION

Create:

```text
/settings
```

Areas:

```text
General
Collectors
SDR
Wi-Fi
Bluetooth
Network
Storage
Retention
Correlation
Models
Evidence
Alerts
Authentication
Privacy
Developer
```

Dangerous settings require confirmation.

Example:

```text
Disable evidence hashing

⚠ This significantly weakens forensic integrity.
```

---

# 39. DARK AND LIGHT MODES

Support:

```text
System
Light
Dark
```

The monitoring dashboard should be usable for long-duration operation.

Accessibility must not depend purely on colors.

Use icons/text in addition to severity colors.

---

# 40. RESPONSIVE DESIGN

Primary target:

```text
Desktop workstation
1920×1080
2560×1440
```

Also support smaller laptop screens.

Mobile may provide status inspection but is not the principal investigative environment.

---

# 41. REAL-TIME COMMUNICATION

Implement backend streams using:

```text
WebSocket
```

or a justified equivalent.

Use streaming for:

```text
live events
collector status
incident creation
alerts
spectrum updates
ledger verification progress
```

Implement:

* reconnect logic
* heartbeat
* bounded buffers
* backpressure
* graceful disconnection

---

# 42. FRONTEND REPOSITORY STRUCTURE

Use:

```text
frontend/
│
├── package.json
├── tsconfig.json
├── vite.config.ts
│
└── src/
    ├── app/
    ├── api/
    ├── components/
    ├── layouts/
    ├── pages/
    │   ├── Dashboard/
    │   ├── Live/
    │   ├── Scan/
    │   ├── Spectrum/
    │   ├── Timeline/
    │   ├── Incidents/
    │   ├── Ledger/
    │   ├── Evidence/
    │   ├── Sensors/
    │   ├── Models/
    │   └── Settings/
    │
    ├── features/
    │   ├── incidents/
    │   ├── scans/
    │   ├── spectrum/
    │   ├── ledger/
    │   ├── evidence/
    │   └── telemetry/
    │
    ├── hooks/
    ├── stores/
    ├── types/
    ├── utils/
    └── tests/
```

---

# 43. BACKEND GUI API

Expand FastAPI endpoint groups:

```text
/api/v1/dashboard
/api/v1/events
/api/v1/incidents
/api/v1/scan
/api/v1/spectrum
/api/v1/timeline
/api/v1/devices
/api/v1/processes
/api/v1/network
/api/v1/ledger
/api/v1/evidence
/api/v1/merkle
/api/v1/sensors
/api/v1/models
/api/v1/settings
```

Realtime:

```text
/ws/events
/ws/spectrum
/ws/incidents
/ws/alerts
/ws/system
```

---

# 44. TRUEPASS-SCAN API

Required endpoints:

```text
POST /scan/sessions
GET  /scan/sessions
GET  /scan/sessions/{id}
POST /scan/sessions/{id}/stop

GET /scan/sessions/{id}/hosts
GET /scan/sessions/{id}/ports
GET /scan/sessions/{id}/processes
GET /scan/sessions/{id}/connections
GET /scan/sessions/{id}/devices

GET /scan/sessions/{id}/diff

POST /scan/sessions/{id}/report
```

All scope restrictions must be enforced server-side.

Never trust only the frontend.

---

# 45. TRUE-PASS-AGE API

Implement:

```text
GET  /ledger/status

GET  /ledger/records
GET  /ledger/records/{sequence}

POST /ledger/verify

GET  /ledger/merkle
GET  /ledger/merkle/{batch}

POST /ledger/merkle/{batch}/verify

GET  /evidence/{event_id}/proof
POST /evidence/{event_id}/verify

GET /anchors
GET /anchors/{id}
```

---

# 46. GUI TESTING

Add:

```text
unit tests
component tests
API mock tests
WebSocket tests
accessibility tests
responsive tests
Playwright E2E tests
```

Required E2E scenario:

```text
1. Start TruePass.
2. Open dashboard.
3. Start authorized TruePass-Scan session.
4. Synthetic collectors create telemetry.
5. Synthetic RF anomaly occurs.
6. Process change follows.
7. Network event follows.
8. Incident is generated.
9. GUI receives event in real time.
10. Operator opens incident.
11. Timeline displays correlated events.
12. Operator opens evidence.
13. TRUE-PASS-AGE verifies ledger record.
14. Merkle proof verifies successfully.
15. Scan report exports successfully.
```

---

# 47. GUI PERFORMANCE REQUIREMENTS

The GUI must remain responsive with large datasets.

Use:

* pagination
* cursor-based APIs where useful
* virtualized tables
* downsampled spectrum visualization
* server-side filtering
* asynchronous loading
* Web Workers where justified

Do not send millions of database records directly to the browser.

---

# 48. GUI ERROR STATES

Every page needs:

```text
loading state
empty state
error state
permission state
offline/reconnecting state
```

Example:

```text
Spectrum sensor unavailable.

Last event:
17:41:03

Reason:
SDR device disconnected.

[ Retry ]
```

---

# 49. UPDATED DEVELOPMENT ORDER

Development must now follow this sequence:

```text
01. Repository bootstrap
02. Event schema
03. Configuration
04. Database
05. OS/process collector
06. Network collector
07. Open-port inventory
08. Wi-Fi collector
09. Bluetooth collector
10. SHA-256 ledger
11. SDR source abstraction
12. FFT / PSD / spectrogram
13. RF feature extraction
14. RF baseline
15. RF anomaly detection
16. Unified event timeline
17. Temporal correlation
18. Incident scoring
19. Event graph
20. PostgreSQL + pgvector
21. Merkle evidence tree
22. Digital signatures

23. Frontend foundation
24. TruePass Control Center
25. Live Event Monitor
26. Incident Explorer
27. Interactive Timeline
28. Spectrum Dashboard
29. RF Cluster Explorer

30. TruePass-Scan™ engine
31. TruePass-Scan™ GUI
32. Port Viewer
33. Process ↔ Socket Explorer
34. Device Inventory
35. Differential Baseline View
36. Scan Reports

37. TRUE-PASS-AGE™ backend
38. TRUE-PASS-AGE™ Ledger Viewer
39. Hash Chain Viewer
40. Merkle Tree Viewer
41. Inclusion Proof Viewer
42. Signature Verification Viewer
43. Optional External Anchor Viewer

44. Identity verification
45. Alert Center
46. Sensor Management
47. Model Management
48. Settings GUI

49. Voice/NLP research
50. EEG research

51. Security hardening
52. Privacy controls
53. GUI security review
54. Backend testing
55. Frontend testing
56. Full E2E testing
57. Performance testing
58. Docker deployment
59. CI/CD
60. Documentation
61. Final integration
62. Release candidate
63. TruePass v1.0.0
```

---

# 50. UPDATED FINAL ARCHITECTURE

The final system must resemble:

```text
 ┌────────────────────────────────────────────────────────────┐
 │                    TRUEPASS™ GUI                           │
 │                                                            │
 │ Dashboard │ Live │ Incidents │ Spectrum │ Timeline        │
 │                                                            │
 │ TruePass-Scan™        │        TRUE-PASS-AGE™             │
 └──────────────────────────────┬─────────────────────────────┘
                                │
                         REST / WebSocket
                                │
 ┌──────────────────────────────▼─────────────────────────────┐
 │                     FASTAPI CORE                           │
 └──────────────────────────────┬─────────────────────────────┘
                                │
       ┌────────────────────────┼──────────────────────────┐
       │                        │                          │
       ▼                        ▼                          ▼
 EVENT CORRELATOR          EVIDENCE ENGINE              ML
       │                        │                          │
       ▼                        ▼                          ▼
 INCIDENTS                 HASH CHAIN                BASELINES
       │                        │                          │
       │                        ▼                          │
       │                   MERKLE TREE                    │
       │                        │                          │
       │                   SIGNATURES                     │
       │                        │                          │
       └────────────┬───────────┴──────────────┬───────────┘
                    ▼                          ▼
              PostgreSQL                  pgvector
                    ▲
                    │
 ┌──────────────────┼────────────────────────────────────────┐
 │                  COLLECTORS                               │
 │                                                          │
 │ OS │ Process │ Network │ Ports │ Wi-Fi │ BLE │ SDR      │
 └──────────────────────────────────────────────────────────┘
```

---

# 51. UPDATED DEFINITION OF DONE

TruePass v1.0.0 cannot be declared complete until the following GUI requirements are satisfied.

## Control Center

* dashboard works
* system health works
* event counters work
* realtime updates work
* incidents are accessible

## Live Monitoring

* live events stream
* filters work
* pause/resume works
* event details work
* timeline navigation works

## Spectrum

* live FFT renders
* waterfall renders
* RF feature view works
* anomaly overlays work
* cluster exploration works

## TruePass-Scan™

* authorized sessions work
* session scope is stored
* host inventory works
* port viewer works
* process/socket relationships work
* device observations work
* baseline comparison works
* session reports work

## TRUE-PASS-AGE™

* ledger status is visible
* ledger browsing works
* individual records verify
* complete chain verification works
* broken chains are detected
* Merkle tree visualization works
* inclusion proofs work
* signatures verify
* optional external anchors display correctly

## Incident Investigation

* timelines work
* correlation explanations work
* candidate entry paths work
* raw evidence is accessible
* similarity results work
* provenance is visible

## UX

* dark mode
* light mode
* keyboard navigation
* accessible status indicators
* responsive layout
* useful error states
* loading states
* reconnect behavior

## Frontend Quality

* TypeScript compiles
* lint passes
* component tests pass
* E2E tests pass
* accessibility checks pass
* production build succeeds

## Full Platform

The application must support this complete workflow:

```text
Signal / System Change
        │
        ▼
Observation
        │
        ▼
Normalized Event
        │
        ├──────────────► Live Dashboard
        │
        ▼
Baseline / Detector
        │
        ▼
Correlation
        │
        ▼
Incident
        │
        ├──────────────► Incident Explorer
        │
        ├──────────────► Timeline
        │
        └──────────────► TruePass-Scan™
        │
        ▼
Evidence Record
        │
        ▼
Hash Chain
        │
        ▼
Merkle Tree
        │
        ▼
Signature
        │
        ├──────────────► TRUE-PASS-AGE™
        │
        └──────────────► Optional External Anchor
```

---

# 52. FINAL IMPLEMENTATION INSTRUCTION

Do not treat the GUI as cosmetic polish added after backend development.

The interfaces are part of the forensic architecture.

The operator must be able to move naturally through:

```text
ALERT
  ↓
INCIDENT
  ↓
TIMELINE
  ↓
EVENT
  ↓
PROCESS / NETWORK / RF CONTEXT
  ↓
EVIDENCE
  ↓
LEDGER RECORD
  ↓
MERKLE PROOF
  ↓
INTEGRITY VERIFICATION
```

Likewise, TruePass-Scan™ must support:

```text
AUTHORIZED SCOPE
       ↓
SCAN SESSION
       ↓
HOST / DEVICE OBSERVATION
       ↓
PORTS + PROCESSES + CONNECTIONS
       ↓
DIFFERENCE FROM BASELINE
       ↓
CORRELATED EVENTS
       ↓
INCIDENT
       ↓
EVIDENCE
```

And TRUE-PASS-AGE™ must support:

```text
EVENT
   ↓
CANONICAL RECORD
   ↓
EVENT HASH
   ↓
HASH CHAIN
   ↓
MERKLE BATCH
   ↓
DIGITAL SIGNATURE
   ↓
OPTIONAL EXTERNAL ANCHOR
```

At every layer preserve the distinction between:

```text
OBSERVED FACT
DERIVED MEASUREMENT
MODEL INFERENCE
CORRELATION
OPERATOR INTERPRETATION
VERIFIED CRYPTOGRAPHIC FACT
```

Never collapse these categories into one another.

The completed product should enable an authorized operator to answer:

> What happened?

> Where did it happen?

> When did it happen?

> What changed?

> What else occurred nearby in time?

> What process, socket, device, or RF observation was involved?

> Has something similar happened before?

> Why did TruePass assign this incident score?

> Which evidence supports the conclusion?

> Has that evidence changed since it was collected?

The final objective remains:

> **Observe → timestamp → normalize → correlate → score → preserve evidence → visualize → alert.**

Continue development phase by phase until the entire integrated platform—including **TruePass Control Center**, **TruePass-Scan™**, and **TRUE-PASS-AGE™ Ledger Viewer**—passes its complete Definition of Done and is ready for:

```text
TruePass™ v1.0.0
```

-----------------------------------------------------------------------------



# FUTURE DEVELOPMENT — TRUEPASS™ ADVANCED RESEARCH ROADMAP

After the production-ready **TruePass™ v1.0.0**, **TruePass-Scan™**, and **TRUE-PASS-AGE™ Ledger Viewer** are complete, tested, secured, and documented, continue development through the following experimental research program.

These capabilities must remain modular and isolated from the trusted production core until each individual technique has been scientifically validated, security-reviewed, privacy-reviewed, and demonstrated to provide reliable results.

The guiding future-development model is:

```text
OBSERVE
    ↓
MEASURE
    ↓
TIMESTAMP
    ↓
NORMALIZE
    ↓
STATE IN EVENT SPACE
    ↓
FIND PATTERNS
    ↓
CORRELATE
    ↓
GENERATE HYPOTHESES
    ↓
VERIFY AGAINST INDEPENDENT EVIDENCE
    ↓
PRESERVE EVIDENCE
```

Do not treat experimental inference as verified fact.

---

# 1. FUTURE TRUEPASS-SCAN™ — MULTIMODAL ENTRY-POINT ANALYSIS

Extend **TruePass-Scan™** into a multimodal defensive analysis environment capable of correlating authorized observations across:

```text
Open ports
Protocols
Network connections
Processes
RF spectrum
Wi-Fi
Bluetooth
Devices
Firmware metadata
Modules
Pipelines
Interfaces
Tunnels
Services
Authentication events
System logs
Historical baselines
Vector similarity
```

The future objective is to investigate:

> **Which observable action or pathway is the most likely candidate entry point associated with a detected security incident?**

Do not report a candidate path as confirmed causation unless sufficient independent evidence exists.

Conceptually:

```text
RF anomaly
     │
     ├── Wi-Fi
     ├── Bluetooth
     ├── unknown RF source
     │
     ▼
Device / Interface
     │
     ▼
Protocol
     │
     ▼
Port / Service
     │
     ▼
Process / Module
     │
     ▼
Network connection / tunnel
     │
     ▼
Security-relevant system change
```

TruePass should rank candidate paths.

Example:

```text
POSSIBLE ENTRY PATHS

1. Wi-Fi → host → service → process
   confidence: 0.87

2. Bluetooth → daemon → process
   confidence: 0.54

3. Network tunnel → listening port → process
   confidence: 0.43

4. Unclassified RF anomaly
   confidence: 0.21
```

Always expose the evidence supporting each ranking.

---

# 2. FREQUENCY — RHYTHM — TEMPORAL PATTERN ANALYSIS

Develop an experimental signal-analysis framework around three measurable domains:

```text
Frequency
Rhythm
Temporal structure
```

Original conceptual labels may be represented internally as:

```text
Frequency-X
Rhythm-Z
Intent-A
```

However, **Intent-A must represent an inferred machine/event classification rather than assumed human psychological intent** unless a scientifically validated method exists.

Develop measurable representations for:

```text
Frequency:
    carrier/center frequency
    occupied bandwidth
    spectral centroid
    spectral peaks
    drift
    harmonics

Rhythm:
    burst intervals
    periodicity
    duty cycle
    pulse duration
    temporal repetition
    envelope variation
    recurrence

Context:
    device
    protocol
    network activity
    system activity
    historical baseline
```

Construct feature vectors:

```text
SignalState(t) = [
    frequency,
    bandwidth,
    power,
    spectral_entropy,
    burst_duration,
    duty_cycle,
    periodicity,
    temporal_spacing,
    modulation_features,
    device_context,
    system_context
]
```

Use these vectors for:

```text
clustering
baseline comparison
novelty detection
similarity retrieval
temporal correlation
```

---

# 3. SDR — SOFTWARE-DEFINED RADIO ANALYSIS

Continue development of SDR capabilities.

Pipeline:

```text
SDR
 ↓
I/Q samples
 ↓
DSP
 ↓
FFT
 ↓
PSD
 ↓
Spectrogram
 ↓
Feature extraction
 ↓
Temporal features
 ↓
Baseline
 ↓
Clustering
 ↓
Anomaly detection
 ↓
Cross-domain correlation
```

Research:

```text
signal fingerprints
burst signatures
modulation characteristics
spectral entropy
periodic signals
frequency hopping
drift
interference patterns
unknown-cluster detection
device-associated RF behavior
```

Do not interpret an unexplained signal as an intrusion without additional evidence.

---

# 4. SDL — SOFTWARE-DEFINED LASER / OPTICAL RESEARCH

Create a separate experimental **SDL Research Module** for future software-defined optical sensing.

Treat SDL as an additional physical telemetry source analogous to SDR.

Architecture:

```text
Optical Sensor
      ↓
Photodetector
      ↓
Sampling
      ↓
Digital Signal Processing
      ↓
Wavelength / frequency analysis
      ↓
Temporal analysis
      ↓
Feature vector
      ↓
State-in-Event-Space
```

Research measurable properties such as:

```text
wavelength
frequency
intensity
phase where measurable
pulse duration
modulation
temporal envelope
spectral distribution
polarization where supported
```

Keep optical research independent from claims about psychological intent.

---

# 5. X-MEANS AND UNKNOWN-STATE DISCOVERY

Continue development of X-means-style unsupervised clustering.

Input:

```text
normalized multimodal feature vectors
```

Possible domains:

```text
RF
Wi-Fi
Bluetooth
network
process
device
optical
behavioral telemetry
```

Pipeline:

```text
Feature vectors
      ↓
Normalization
      ↓
Dimensionality reduction
      ↓
Clustering
      ↓
Known state / Unknown state
      ↓
Temporal correlation
      ↓
Candidate explanation
```

An unknown cluster means:

> **Previously unclassified behavior was observed.**

It does NOT mean:

> **An attacker was detected.**

---

# 6. NETWORK VECTOR DATABASE

Expand PostgreSQL + pgvector into a multimodal similarity-retrieval system.

Represent:

```text
RF fingerprints
device behavior
network sessions
process behavior
protocol behavior
Wi-Fi states
Bluetooth states
incident patterns
event sequences
firmware metadata
```

as embeddings or numerical feature vectors.

The system should answer questions such as:

```text
Have we observed this RF fingerprint before?

Has this process/network pattern occurred previously?

Which historical incident most closely resembles this event sequence?

Which devices have produced similar temporal signatures?

Which prior candidate entry paths resemble this incident?
```

Keep canonical forensic evidence separate from vector representations.

---

# 7. STATE-IN-EVENT-SPACE™

Extend the existing State-in-Event-Space architecture.

Conceptually:

```text
S(t) = [
    PhysicalState,
    RFState,
    OpticalState,
    NetworkState,
    ProtocolState,
    DeviceState,
    ProcessState,
    IdentityState,
    BehavioralState,
    EvidenceState
]
```

Each observation must retain:

```text
timestamp
source
sensor
measurement
confidence
provenance
model version
processing history
```

Allow queries such as:

```text
What was the complete observed system state at T?

What changed between T1 and T2?

Which state dimensions changed first?

Which changes repeatedly occur together?
```

---

# 8. AUTOLOG™ OS FORENSIC TRACING

Develop **AutoLog™** as an advanced forensic subsystem.

Its purpose is to automatically preserve traces associated with security-relevant system changes.

Monitor authorized systems for:

```text
process creation
process termination
service changes
drivers/modules
authentication events
privilege changes
network sockets
new listening ports
configuration changes
device connections
Wi-Fi changes
Bluetooth changes
selected firmware/device metadata
security events
```

Architecture:

```text
System Event
     ↓
Normalize
     ↓
Timestamp
     ↓
Correlate
     ↓
Hash
     ↓
TRUE-PASS-AGE™ Ledger
```

AutoLog must never silently rewrite collected evidence.

---

# 9. PII / IDENTITY STATE DATABASE

Future identity research may maintain a logically separated identity system containing explicitly consented data.

Potential categories:

```text
Identity profile
Device possession
Authentication history
Optional fingerprint template
Optional facial template
Optional voice template
Behavioral baseline
Physiological research measurements
User-controlled research profile
```

Maintain strict separation:

```text
Identity
    ≠
Evidence

Identity
    ≠
Wallet private key

Identity
    ≠
Threat classification
```

Raw biometric data should be minimized.

Protected templates should be preferred.

---

# 10. DIGITAL FOOTPRINT BASELINE

Develop an optional user-controlled **Digital Footprint Baseline**.

Possible dimensions:

```text
known devices
normal login periods
usual applications
normal network destinations
normal process behavior
normal peripherals
normal Wi-Fi relationships
normal Bluetooth relationships
```

Use the baseline for authentication/risk context.

Example:

```text
CURRENT STATE
      ↓
Compare
      ↓
USER BASELINE
      ↓
Deviation Score
```

Do not use behavioral deviation alone to accuse a user of wrongdoing.

---

# 11. MACHINE BEHAVIORAL PROFILE

Develop a machine behavioral profile representing system/device behavior rather than subjective personality.

Example:

```text
MachineBehaviorState = [
    process_distribution,
    network_distribution,
    service_state,
    device_state,
    authentication_patterns,
    resource_usage,
    protocol_behavior,
    RF_context
]
```

Use it for:

```text
novelty detection
device identification research
security correlation
historical comparison
```

---

# 12. CRYPTOGRAPHIC IDENTITY GATE

Research ways for multiple identity factors to authorize access to protected cryptographic material.

Conceptual flow:

```text
User
  ↓
Identity factors
  ↓
Authentication score
  ↓
Policy engine
  ↓
Approved?
  ↓
Secure key store / TPM / hardware wallet
  ↓
Cryptographic operation
```

Potential factors:

```text
OS credential
device possession
hardware token
optional fingerprint
optional facial verification
optional voice verification
behavioral context
```

These factors may **unlock or authorize use of an existing securely generated key**.

They must never serve as the sole entropy for generating the private key.

---

# 13. TIME-SPECIFIC CRYPTOGRAPHIC EVENT STATE

Develop cryptographic commitments representing an observed state at a particular moment.

Example:

```text
State Snapshot
      +
Precise Timestamp
      +
Event IDs
      +
Evidence IDs
      ↓
Canonical Serialization
      ↓
SHA-256
      ↓
State Commitment
```

Conceptually:

```text
C(t) = SHA256(
    CanonicalSerialize(State(t))
)
```

This produces a verifiable commitment to the observed state without putting all state data into a public ledger.

---

# 14. RHYTHM-SEQUENCED HASH RESEARCH

Research a deterministic sequencing model where temporal event order contributes to cryptographic evidence construction.

Do not alter established cryptographic algorithms themselves.

Instead:

```text
Event rhythm / sequence
        ↓
Canonical ordering
        ↓
Evidence sequence
        ↓
Standard cryptographic hash
```

Example:

```text
H0 = SHA256(Event0)

H1 = SHA256(
    H0 ||
    timestamp1 ||
    Event1
)

H2 = SHA256(
    H1 ||
    timestamp2 ||
    Event2
)
```

Use standard, reviewed cryptographic primitives.

Never create custom "shuffled" cryptography whose security depends on secret algorithm design.

---

# 15. BITCOIN-COMPATIBLE EVIDENCE ANCHORING

Continue research into Bitcoin-compatible evidence verification.

Correct architecture:

```text
TruePass Evidence
      ↓
Hash
      ↓
Merkle Tree
      ↓
Merkle Root
      ↓
Signed Commitment
      ↓
Optional Bitcoin Transaction
```

The Bitcoin network receives only the commitment.

Never place:

```text
biometrics
psychological profiles
EEG
voice recordings
names
addresses
raw identity information
```

directly on-chain.

---

# 16. BTC WALLET ARCHITECTURE

If wallet functionality becomes part of a future TruePass product, maintain strict separation between:

```text
WALLET KEY DOMAIN

IDENTITY DOMAIN

TRUE-PASS-AGE™ EVIDENCE DOMAIN
```

Wallet key generation:

```text
CSPRNG
  ↓
256-bit private key
  ↓
Elliptic Curve Operation
  ↓
Public Key
  ↓
Bitcoin Address
```

Identity may authorize wallet access.

Identity must not deterministically generate the wallet private key.

Where mnemonic wallets are used, use standard wallet specifications such as BIP-39/BIP-32-compatible mechanisms rather than inventing custom PII-derived seed phrases.

---

# 17. BLOCKCHAIN MESSAGE / PROOF RESEARCH

Research optional transaction commitments capable of proving that an evidence state existed by a given time.

Possible architecture:

```text
Evidence batch
      ↓
Merkle root
      ↓
Commitment
      ↓
Bitcoin transaction
      ↓
Transaction identifier
```

Store locally:

```text
transaction ID
block reference
confirmation status
Merkle root
evidence batch
timestamp
```

The blockchain becomes an external timestamp/proof layer, not the primary evidence database.

---

# 18. QR EVIDENCE PROOFS

Develop QR representation for portable verification.

QR payload may contain:

```text
TruePass evidence ID
ledger sequence
Merkle root
proof reference
signature fingerprint
optional blockchain transaction ID
verification URL/reference
```

Example workflow:

```text
TRUE-PASS-AGE™
      ↓
Generate Verification Package
      ↓
QR Code
      ↓
Independent verifier
      ↓
Verify signature
      ↓
Verify Merkle proof
      ↓
Verify optional external anchor
```

Never embed unnecessary sensitive PII in QR codes.

---

# 19. HUMAN STATE RESEARCH DOMAIN

Human-state research must remain completely separate from core cybersecurity conclusions.

Potential research dimensions:

```text
Core Traits Map
Physical Baseline
Physiological Baseline
Psychological Baseline
Behavioral Responses
```

All measurements must be:

```text
consensual
revocable where possible
scientifically documented
confidence-scored
provenance-tracked
```

Do not treat these models as immutable truths about a person.

---

# 20. SECONDARY DEVIANCE / FORENSIC PSYCHOLOGY RESEARCH

Create a research-only framework for studying significant behavioral or psychological transitions.

The original hypothesis may investigate whether a severe event can produce long-term behavioral or affective changes.

However, TruePass must not encode:

```text
person.evil = true
```

or equivalent permanent moral judgments.

Instead represent:

```text
ObservedEvent
      ↓
DocumentedResponse
      ↓
MeasuredChange
      ↓
Longitudinal Observation
      ↓
Research Assessment
```

Store:

```text
observation
measurement technique
timestamp
research context
confidence
source
review status
```

Replace the concept of an automatically **Immutable Affective Profile** with a research-safe:

```text
Longitudinal Affective Profile
```

whose observations may change over time.

---

# 21. PHYSICAL BASELINE

Research optional measurable physical context.

Examples may include:

```text
movement
posture where appropriately measured
environmental context
device-derived physical activity
```

Do not interpret physical state as criminal intent.

---

# 22. PHYSIOLOGICAL BASELINE

Experimental physiological research may investigate measurements such as:

```text
heart-rate trends
heart-rate variability
respiratory patterns
EEG features
other explicitly consented measurements
```

These measurements are sensitive data and must remain isolated from standard TruePass cybersecurity telemetry.

---

# 23. PSYCHOLOGICAL BASELINE

Psychological data must be research-only.

Use validated instruments where applicable.

Never infer permanent identity from transient emotion.

Represent:

```text
measurement
method
timestamp
context
confidence
research interpretation
```

not absolute truth.

---

# 24. EMOTIONAL-STATE RESEARCH

If emotional-state ML is researched, treat outputs as uncertain classifications.

Example:

```text
Input
 ↓
Feature Extraction
 ↓
Model
 ↓
Probability Distribution

calm       0.47
stressed   0.31
uncertain  0.22
```

Never represent:

```text
Emotion = confirmed intent
```

An emotional classification cannot independently establish intent, guilt, danger, deception, or criminality.

---

# 25. EEG RESEARCH

Develop EEG as a separate experimental Brain-Computer Interface laboratory.

Pipeline:

```text
EEG
 ↓
Filtering
 ↓
Artifact Removal
 ↓
Segmentation
 ↓
Feature Extraction
 ↓
Temporal Model
 ↓
Constrained Classification
 ↓
Candidate Symbol / Command
 ↓
Language Model
```

Research:

```text
frequency bands
temporal patterns
event-related potentials
classification
BCI command selection
limited symbol decoding
```

Clearly document that non-invasive EEG is not unrestricted mind reading.

---

# 26. EEG → NLP EXPERIMENTAL PIPELINE

Investigate whether constrained EEG classifications can feed an NLP layer.

Safe architecture:

```text
EEG
 ↓
Constrained classifier
 ↓
Candidate semantic class
 ↓
Confidence threshold
 ↓
NLP model
 ↓
Candidate text
```

Always show uncertainty.

Example:

```text
Classifier output:

YES            0.71
NO             0.16
UNDETERMINED   0.13
```

Never silently convert uncertain neural measurements into definitive statements attributed to a person.

---

# 27. BRAINWAVE FREQUENCY ANALYSIS

Research measurable EEG frequency ranges and temporal features.

Pipeline:

```text
EEG signal
 ↓
FFT / wavelets
 ↓
Frequency-domain features
 ↓
Temporal features
 ↓
State classifier
```

Keep the scientific interpretation tied to validated experimental paradigms.

---

# 28. NEUROMODULATION RESEARCH BOUNDARY

Neuromodulation involves active interaction with the nervous system and therefore belongs to a fundamentally different safety class from passive sensing.

The default TruePass product must remain:

```text
READ ONLY
```

Do not implement autonomous stimulation.

Future neuromodulation research would require:

```text
specialized medical/research oversight
hardware safety controls
human authorization
independent ethics review
regulatory review where applicable
```

Keep all stimulation functionality outside the normal TruePass application.

---

# 29. PHOTON / ELECTRON SIGNAL RESEARCH

Develop an abstract physical-signal framework capable of describing different sensor domains.

Conceptually:

```text
Physical Signal
     │
     ├── Electromagnetic RF
     ├── Optical / photons
     ├── Electrical sensor signals
     └── Other future sensors
```

Normalize them through domain-specific DSP into a common event architecture.

Example:

```text
Sensor
 ↓
Signal
 ↓
Sampling
 ↓
Feature Extraction
 ↓
Event
 ↓
State-in-Event-Space
```

---

# 30. MODULATION RESEARCH

Develop reusable DSP modules for studying:

```text
amplitude modulation
frequency modulation
phase modulation
pulse modulation
digital modulation signatures
envelope structure
periodic patterns
```

The purpose is signal characterization and classification.

---

# 31. WAVELENGTH / FREQUENCY MODEL

Normalize physical measurements appropriately:

```text
frequency
wavelength
sampling rate
bandwidth
power/intensity
phase where measurable
```

Use physically valid conversions.

Do not assume different signals with equal frequency or wavelength necessarily have equal meaning or origin.

---

# 32. BINARY STATE MATRIX

Research a generalized machine-readable State Matrix.

Example:

```text
StateMatrix(t) =

[
  RF features,
  optical features,
  network features,
  process features,
  device features,
  identity context,
  behavioral context,
  evidence context
]
```

Provide:

```text
dense numerical form
sparse form
categorical representation
vector embedding
graph representation
```

depending on the analytic task.

---

# 33. MULTIMODAL FUSION ENGINE

Build a research framework capable of combining:

```text
SDR
SDL/optical
OS telemetry
network telemetry
Wi-Fi
Bluetooth
EEG research
voice
behavioral signals
```

Each modality must retain independent provenance.

Architecture:

```text
Modality A ─┐
Modality B ─┤
Modality C ─┼──► Multimodal Fusion
Modality D ─┤
Modality E ─┘
                │
                ▼
          State Representation
                │
                ▼
          Correlation Model
```

The model must be capable of indicating:

```text
INSUFFICIENT EVIDENCE
```

rather than forcing a classification.

---

# 34. GENERIC RESPONSE LANGUAGE MODEL

Develop an optional local/remote LLM integration layer capable of explaining TruePass findings in natural language.

The LLM must consume structured evidence rather than invent system state.

Architecture:

```text
TruePass Evidence
      ↓
Structured Retrieval
      ↓
Policy / Privacy Filter
      ↓
LLM
      ↓
Natural-Language Explanation
```

The model may answer:

```text
Why was this incident scored HIGH?

What changed during the last 30 seconds?

Which process opened port 7331?

What evidence links this RF anomaly to the incident?

Has anything similar happened before?
```

The LLM must cite or reference underlying TruePass events.

---

# 35. RELAY / ECHO AGENT™

Develop **Echo Agent™** as an optional conversational interface.

Architecture:

```text
Microphone
 ↓
Voice Activity Detection
 ↓
Speech-to-Text
 ↓
Command / Intent Classification
 ↓
Policy Engine
 ↓
TruePass Agent
 ↓
LLM
 ↓
Text Response
 ↓
Speech Synthesis
```

Potential personas may affect:

```text
voice
presentation
verbosity
interaction style
```

but must never change security evidence.

---

# 36. VOICE MODEL RESEARCH

Research voice characteristics such as:

```text
frequency
pitch
prosody
contour envelope
timing
oscillations
speech rhythm
speaker embeddings
```

Applications:

```text
speaker verification
anti-spoofing
voice-interface customization
synthetic voice detection
replay detection
```

Do not use voice alone as definitive identity verification.

---

# 37. ANTI-SPY / ANTI-SPOOF METRICS

Develop defensive telemetry for identifying suspicious interaction with TruePass voice/agent systems.

Research:

```text
replay attacks
synthetic voices
voice cloning
microphone injection
unexpected audio routing
session hijacking
device mismatch
challenge-response
```

Possible risk model:

```text
VoiceSessionRisk =
    replay_score
  + synthetic_voice_score
  + device_mismatch
  + session_anomaly
  + identity_context
```

All individual components must remain explainable.

---

# 38. INTENT ANALYSIS RESEARCH

Separate three concepts:

```text
Machine Action Intent
User Command Intent
Human Psychological Intent
```

### Machine Action Intent

Technically useful.

Example:

```text
process opens port
process initiates connection
device associates with Wi-Fi
```

### User Command Intent

Appropriate for NLP.

Example:

```text
"show current incidents"
        ↓
VIEW_INCIDENTS
```

### Human Psychological Intent

Highly uncertain and sensitive.

Do not infer criminal or moral intent from RF, EEG, emotion, voice, or behavioral measurements without scientifically defensible validation.

---

# 39. QUANTUM RESEARCH SANDBOX

If quantum technologies are explored, place them in:

```text
research/quantum/
```

Possible legitimate research directions include:

```text
quantum-safe cryptography
quantum random number generation
quantum networking literature
quantum sensing research
```

Do not make quantum entanglement a dependency of the TruePass architecture unless an actual implementable mechanism and hardware capability exist.

Specifically, do not assume:

```text
quantum entanglement
      ↓
human intent detection
```

without evidence.

---

# 40. FUTURE REPOSITORY STRUCTURE

Expand the project with:

```text
research/
│
├── multimodal/
│
├── sdr/
│
├── sdl/
│
├── eeg/
│
├── physiology/
│
├── affective/
│
├── voice/
│
├── anti_spoof/
│
├── behavior/
│
├── quantum/
│
└── experiments/

truepass/
│
├── autolog/
├── state_space/
├── fusion/
├── agents/
├── identity/
├── physical_signals/
└── anchors/
```

Research code must not automatically become trusted production code.

---

# 41. FUTURE TRUEPASS GUI

Add a dedicated:

```text
RESEARCH LAB
```

inside the GUI.

Navigation:

```text
TruePass™

Dashboard
Live Monitor
TruePass-Scan™
Spectrum
Timeline
Incidents
TRUE-PASS-AGE™

─────────────

Research Lab

  RF Laboratory
  Optical / SDL
  Multimodal Fusion
  State Matrix
  Behavioral Research
  EEG Laboratory
  Voice Laboratory
  Anti-Spoof
  Agent Lab
  Cryptography
  Blockchain
  Quantum Sandbox
```

Clearly mark experimental pages:

```text
EXPERIMENTAL
NOT FOR PRODUCTION DECISIONS
```

---

# 42. STATE MATRIX GUI

Create a visual State-in-Event-Space explorer.

Example:

```text
STATE AT 17:41:03.219

┌─────────────────┬───────────────────┐
│ DOMAIN          │ STATE             │
├─────────────────┼───────────────────┤
│ RF              │ anomaly 0.81      │
│ Wi-Fi           │ changed           │
│ Bluetooth       │ normal            │
│ Network         │ new connection    │
│ Process         │ PID 9184 created  │
│ Authentication  │ change detected   │
│ Identity        │ authenticated     │
│ Evidence        │ verified          │
└─────────────────┴───────────────────┘
```

Allow time travel:

```text
◀ Previous State     T = 17:41:03.219     Next State ▶
```

---

# 43. MULTIMODAL CORRELATION GUI

Display relationships as an interactive graph:

```text
                     RF ANOMALY
                          │
                          │ +38 ms
                          ▼
                    WI-FI CHANGE
                          │
                          │ +21 ms
                          ▼
                    PROCESS START
                          │
                          │ +16 ms
                          ▼
                  NETWORK SOCKET
                          │
                          ▼
                    REMOTE HOST
```

Allow operators to enable/disable individual modalities to understand their impact on the score.

---

# 44. RESEARCH EXPERIMENT TRACKING

Every research experiment must have:

```text
experiment_id
hypothesis
dataset
consent requirements
configuration
model version
software version
timestamp
results
metrics
limitations
review status
```

Never preserve only the successful experiments.

Record negative results.

---

# 45. SCIENTIFIC VALIDATION GATE

A research capability cannot migrate into production until it has:

```text
repeatable experiment
documented dataset
baseline comparison
appropriate metrics
false-positive analysis
false-negative analysis
privacy review
security review
independent reproducibility where practical
```

Migration path:

```text
IDEA
 ↓
RESEARCH
 ↓
EXPERIMENT
 ↓
VALIDATION
 ↓
SECURITY REVIEW
 ↓
PRIVACY REVIEW
 ↓
BETA
 ↓
PRODUCTION
```

---

# 46. FUTURE DEVELOPMENT ORDER

After TruePass v1.0.0:

```text
01. Advanced TruePass-Scan™ correlation
02. AutoLog™ forensic expansion
03. Network vector database expansion
04. Advanced RF fingerprints
05. X-means / unknown-state discovery
06. State-in-Event-Space v2
07. State Matrix GUI
08. Multimodal correlation graph

09. Identity baseline research
10. Machine behavioral baseline
11. Advanced authentication policy
12. Secure cryptographic authorization

13. Time-specific state commitments
14. Evidence QR verification
15. Bitcoin evidence anchoring improvements
16. Hardware-wallet/TPM integration

17. Echo Agent™
18. Voice Anti-Spoof Lab
19. Generic Response Language Model integration

20. EEG Research Lab
21. EEG → constrained NLP research
22. Physiological research framework
23. Longitudinal affective research

24. SDL / optical laboratory
25. Photon/electron physical-signal framework
26. Multimodal fusion engine

27. Quantum research sandbox
28. Scientific validation
29. Security/privacy review
30. Selected migration to future production releases
```

---

# 47. FUTURE CRYPTOGRAPHIC PRINCIPLE

TruePass must maintain three separate domains permanently:

```text
┌──────────────────────────┐
│ IDENTITY                 │
│ Who is authorized?       │
└─────────────┬────────────┘
              │ authorization
              ▼
┌──────────────────────────┐
│ CRYPTOGRAPHIC KEY STORE  │
│ Secure random keys       │
└──────────────────────────┘


┌──────────────────────────┐
│ FORENSIC EVIDENCE        │
│ What happened?           │
└─────────────┬────────────┘
              │ hash
              ▼
┌──────────────────────────┐
│ TRUE-PASS-AGE™           │
│ Integrity / provenance   │
└─────────────┬────────────┘
              │ commitment
              ▼
┌──────────────────────────┐
│ OPTIONAL BTC ANCHOR      │
│ External timestamp       │
└──────────────────────────┘
```

Do not collapse these domains.

---

# 48. LONG-TERM TRUEPASS VISION

The long-term TruePass ecosystem should evolve toward:

```text
                           TRUEPASS™
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
 TRUEPASS-SCAN™        TRUE-PASS-AGE™          RESEARCH LAB
         │                     │                     │
         ▼                     ▼                     ▼
 Observation            Evidence Integrity     Experimental
 & Correlation          & Verification         Modalities
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               ▼
                     STATE-IN-EVENT-SPACE
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
       RF/SDR                NETWORK              PHYSICAL
       Wi-Fi                 PROCESS              OPTICAL
       BLE                   DEVICE               EEG*
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               ▼
                       MULTIMODAL FUSION
                               │
                               ▼
                        EVENT CORRELATION
                               │
                               ▼
                       CANDIDATE EXPLANATION
                               │
                               ▼
                       EVIDENCE VERIFICATION
```

`* EEG and human-state data remain experimental, consent-based research domains and are not required for cybersecurity operation.`

---

# 49. FINAL FUTURE-DEVELOPMENT INSTRUCTION

Treat the concepts in this roadmap as **research hypotheses to test**, not conclusions to encode into software.

Preserve the original ambition:

```text
Frequency
Rhythm
Signals
Devices
Networks
Behavior
Identity
Time
Cryptography
Evidence
```

while enforcing a disciplined engineering progression:

```text
IDEA
   ↓
MEASURABLE VARIABLE
   ↓
EXPERIMENT
   ↓
DATA
   ↓
MODEL
   ↓
VALIDATION
   ↓
CORRELATION
   ↓
EVIDENCE
```

The system must always be able to distinguish:

```text
OBSERVED FACT
        ≠
DERIVED FEATURE
        ≠
STATISTICAL ANOMALY
        ≠
MODEL INFERENCE
        ≠
CORRELATION
        ≠
HYPOTHESIS
        ≠
VERIFIED CAUSATION
```

The long-term objective is therefore not:

> Detect intent from a frequency.

It is:

> **Create a multimodal State-in-Event-Space where RF, network, protocol, process, device, identity, behavioral, temporal, and cryptographic evidence can be independently measured, correlated, searched, visualized, and verified while preserving provenance and uncertainty.**

And for forensic integrity:

> **Observed evidence → canonical state → cryptographic hash → hash chain → Merkle proof → signature → optional external timestamp → QR-verifiable proof.**

Continue future development only after the production TruePass foundation remains stable, tested, privacy-preserving, and cryptographically verifiable.




