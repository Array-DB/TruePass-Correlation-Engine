#!/usr/bin/env python3
"""Offline release verification for TruePass Overall Definition of Done."""
from __future__ import annotations
import json
from pathlib import Path
from truepass import __version__
from truepass.integration import FullPlatformIntegrationPipeline
from truepass.verification import run_overall_dod_audit


def main() -> None:
    required = [
        "README.md", "CHANGELOG.md", "Dockerfile", "docker-compose.yml",
        "docs/RELEASE_CHECKLIST.md", "docs/release/1.0.0.md",
        "docs/benchmarks/latest.json", "docs/OVERALL_DEFINITION_OF_DONE.md",
        "scripts/hardware_verify.py", "scripts/reliability_soak.py",
        "frontend/tsconfig.json", "frontend/src/dod.ts",
    ]
    missing = [item for item in required if not Path(item).is_file()]
    if missing:
        raise SystemExit(f"missing release artifacts: {missing}")
    if __version__ != "1.0.0":
        raise SystemExit(f"unexpected version: {__version__}")
    result = FullPlatformIntegrationPipeline().run()
    audit = run_overall_dod_audit(include_external=False)
    if not result.overall_verified or not audit.overall_pass:
        raise SystemExit("offline Overall Definition-of-Done verification failed")
    print(json.dumps({
        "version": __version__,
        "release_artifacts": "verified",
        "full_platform_e2e": "verified",
        "source_level_dod": "verified",
        "incident_id": result.incident_id,
        "external_environment_gate": "run truepass verify dod on deployment host",
    }, indent=2))

if __name__ == "__main__":
    main()
