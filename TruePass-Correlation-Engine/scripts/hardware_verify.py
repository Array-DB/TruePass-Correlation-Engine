#!/usr/bin/env python3
"""On-host receive-only HackerRF verification for the final TruePass release gate."""
from __future__ import annotations
import argparse, json, sys
from truepass.sdr.sources import HackRFOneSource, SDRConfig
from truepass.spectrum.pipeline import SpectrumDSPPipeline


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", default=None)
    parser.add_argument("--center-frequency", type=float, default=100_000_000.0)
    parser.add_argument("--sample-rate", type=float, default=2_000_000.0)
    parser.add_argument("--gain", type=float, default=0.0)
    parser.add_argument("--samples", type=int, default=4096)
    args = parser.parse_args()
    cfg = SDRConfig(args.sample_rate, args.center_frequency, args.gain, args.samples, "hackrf")
    try:
        devices = HackRFOneSource.enumerate_devices()
        if not devices:
            raise RuntimeError("no HackerRF One enumerated through SoapySDR/SoapyHackRF")
        with HackRFOneSource(cfg, serial=args.serial) as source:
            iq = source.read_samples(args.samples)
        frame = SpectrumDSPPipeline(sample_rate_hz=cfg.sample_rate, center_frequency_hz=cfg.center_frequency).process(iq)
        payload = {
            "status": "pass", "receive_only": True, "devices": devices,
            "samples": len(iq), "fft_bins": len(frame.fft_magnitude_db),
            "waterfall_rows": len(frame.waterfall_db_per_hz),
            "center_frequency_hz": frame.center_frequency_hz,
        }
        print(json.dumps(payload, indent=2, default=str))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
