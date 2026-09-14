#!/usr/bin/env python3
"""Bounded synthetic reliability/soak verification for realtime spectrum and AGE."""
from __future__ import annotations
import argparse, asyncio, json, time, tracemalloc
from truepass.api.state import RuntimeState
from truepass.sdr.sources import SDRConfig, SyntheticIQSource
from truepass.spectrum.pipeline import SpectrumDSPPipeline

async def run(iterations: int) -> dict[str, object]:
    state = RuntimeState()
    cfg = SDRConfig(2_000_000.0, 100_000_000.0, 0.0, 4096, "synthetic")
    pipe = SpectrumDSPPipeline(sample_rate_hz=cfg.sample_rate, center_frequency_hz=cfg.center_frequency)
    source = SyntheticIQSource(cfg, tone_hz=125_000.0, noise_amplitude=0.03, seed=77)
    start = time.perf_counter(); tracemalloc.start()
    for _ in range(iterations):
        frame = pipe.process(source.read_samples(4096)).as_dict()
        await state.publish_spectrum(frame)
    current, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
    elapsed = time.perf_counter() - start
    return {
        "status": "pass", "iterations": iterations, "elapsed_seconds": elapsed,
        "frames_per_second": iterations / max(elapsed, 1e-9),
        "peak_python_bytes": peak, "latest_spectrum_present": state.latest_spectrum is not None,
        "ledger_valid": state.age.status()["valid"],
    }

def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--iterations", type=int, default=100); args=parser.parse_args()
    if args.iterations < 1: raise SystemExit("iterations must be positive")
    print(json.dumps(asyncio.run(run(args.iterations)), indent=2))
    return 0

if __name__ == "__main__": raise SystemExit(main())
