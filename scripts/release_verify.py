#!/usr/bin/env python3
"""Offline release-artifact verification that does not require external services."""
from __future__ import annotations

import json
from pathlib import Path

from truepass import __version__
from truepass.integration import SyntheticIntegrationPipeline


def main() -> None:
    required = [
        "README.md",
        "CHANGELOG.md",
        "Dockerfile",
        "docker-compose.yml",
        "docs/RELEASE_CHECKLIST.md",
        "docs/release/1.0.0.md",
        "docs/benchmarks/latest.json",
    ]
    missing = [item for item in required if not Path(item).is_file()]
    if missing:
        raise SystemExit(f"missing release artifacts: {missing}")
    if __version__ != "1.0.0":
        raise SystemExit(f"unexpected version: {__version__}")
    result = SyntheticIntegrationPipeline().run()
    if not (result.ledger_verified and result.merkle_verified and result.api_incident_visible):
        raise SystemExit("synthetic integration verification failed")
    print(json.dumps({
        "version": __version__,
        "release_artifacts": "verified",
        "synthetic_e2e": "verified",
        "incident_id": result.incident_id,
    }, indent=2))


if __name__ == "__main__":
    main()
