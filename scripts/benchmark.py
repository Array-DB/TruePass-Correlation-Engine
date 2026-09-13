#!/usr/bin/env python3
"""Reproducible local TruePass benchmark harness; writes JSON results."""
from __future__ import annotations

import argparse
import json
import resource
import time
from pathlib import Path

import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from truepass.correlation.engine import TemporalCorrelationEngine
from truepass.database.models import Base
from truepass.database.repositories import EventRepository
from truepass.eventspace.timeline import Timeline
from truepass.models.events import Event, EventSource, EventType, Provenance
from truepass.spectrum.fft import compute_fft
from truepass.spectrum.psd import compute_spectrogram
from truepass.vectors.search import InMemoryVectorIndex


def event(i: int) -> Event:
    return Event(
        timestamp_ns=1_800_000_000_000_000_000 + i * 1_000_000,
        received_timestamp_ns=1_800_000_000_000_000_100 + i * 1_000_000,
        source=EventSource.NETWORK,
        sensor_id="bench",
        host="bench-host",
        event_type=EventType.NETWORK_CONNECTION,
        provenance=Provenance(collector="benchmark", method="synthetic"),
    )


def per_second(fn, iterations: int) -> float:
    start = time.perf_counter()
    for _ in range(iterations):
        fn()
    elapsed = max(time.perf_counter() - start, 1e-9)
    return iterations / elapsed


def db_insert_throughput(events: list[Event]) -> float:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    start = time.perf_counter()
    with Session(engine) as session:
        repo = EventRepository(session)
        for item in events:
            repo.add(item)
        session.commit()
    elapsed = max(time.perf_counter() - start, 1e-9)
    return len(events) / elapsed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="docs/benchmarks/latest.json")
    parser.add_argument("--iterations", type=int, default=200)
    args = parser.parse_args()
    if args.iterations < 10:
        raise SystemExit("--iterations must be at least 10")

    events = [event(i) for i in range(500)]
    timeline = Timeline(events)
    correlation = TemporalCorrelationEngine(window_ms=500)
    samples = np.exp(2j * np.pi * 0.125 * np.arange(4096, dtype=np.float64))
    index = InMemoryVectorIndex(8)
    for i in range(1000):
        index.upsert(str(i), [float((i + j) % 17) for j in range(8)])

    target = events[len(events) // 2]
    results = {
        "generated_at_unix_ns": time.time_ns(),
        "iterations": args.iterations,
        "events_per_sec_model_serialization": per_second(
            lambda: target.canonical_bytes(), args.iterations * 10
        ),
        "db_inserts_per_sec_sqlite_local": db_insert_throughput(events),
        "timeline_queries_per_sec": per_second(
            lambda: timeline.around(target.event_id, before_ms=50, after_ms=50), args.iterations
        ),
        "correlations_per_sec": per_second(
            lambda: correlation.correlate(target, events), args.iterations
        ),
        "fft_frames_per_sec": per_second(
            lambda: compute_fft(
                samples,
                sample_rate_hz=2_000_000,
                center_frequency_hz=100_000_000,
            ),
            max(10, args.iterations // 2),
        ),
        "spectrogram_frames_per_sec": per_second(
            lambda: compute_spectrogram(
                samples,
                sample_rate_hz=2_000_000,
                center_frequency_hz=100_000_000,
                nperseg=256,
            ),
            max(10, args.iterations // 4),
        ),
        "vector_queries_per_sec": per_second(
            lambda: index.search([1.0] * 8, limit=5), args.iterations
        ),
        "memory_max_rss_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "notes": (
            "Synthetic local benchmark. SQLite is used only for portable insert timing; "
            "production PostgreSQL/pgvector must be benchmarked in its deployment environment."
        ),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
