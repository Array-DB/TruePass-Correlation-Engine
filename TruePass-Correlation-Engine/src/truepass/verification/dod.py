"""Executable Overall Definition-of-Done audit.

The audit distinguishes source/runtime checks that can be proven anywhere from
external environment checks (physical HackerRF, PostgreSQL, Docker).  External
checks are never silently converted to passes.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from fastapi.testclient import TestClient

from truepass.api.server import create_app
from truepass.api.state import RuntimeState
from truepass.integration.pipeline import FullPlatformIntegrationPipeline
from truepass.sdr.sources import HackRFOneSource, SDRConfig


@dataclass(frozen=True, slots=True)
class DoDCheck:
    id: str
    area: str
    status: str
    detail: str
    required: bool = True

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DoDAudit:
    checks: tuple[DoDCheck, ...]

    @property
    def implementation_complete(self) -> bool:
        return all(c.status == "pass" for c in self.checks if c.required and not c.id.startswith("external."))

    @property
    def environment_verified(self) -> bool:
        external = [c for c in self.checks if c.required and c.id.startswith("external.")]
        return bool(external) and all(c.status == "pass" for c in external)

    @property
    def overall_pass(self) -> bool:
        return all(c.status == "pass" for c in self.checks if c.required)

    def as_dict(self) -> dict[str, object]:
        return {
            "implementation_complete": self.implementation_complete,
            "environment_verified": self.environment_verified,
            "overall_pass": self.overall_pass,
            "checks": [c.as_dict() for c in self.checks],
        }


def _check(check_id: str, area: str, fn: Callable[[], str], *, required: bool = True) -> DoDCheck:
    try:
        return DoDCheck(check_id, area, "pass", fn(), required)
    except Exception as exc:  # deliberate audit boundary: report, do not hide
        return DoDCheck(check_id, area, "fail", f"{type(exc).__name__}: {exc}", required)


def _route_check() -> str:
    client = TestClient(create_app(RuntimeState()))
    paths = (
        "/dashboard", "/live", "/timeline", "/spectrum", "/incidents", "/scan",
        "/age", "/alerts/view", "/settings", "/verification",
    )
    failed = {path: client.get(path).status_code for path in paths if client.get(path).status_code != 200}
    if failed:
        raise RuntimeError(f"GUI route failures: {failed}")
    return f"{len(paths)} operator routes reachable"


def _api_check() -> str:
    client = TestClient(create_app(RuntimeState()))
    response = client.post("/api/v1/spectrum/capture?device=synthetic&samples=4096")
    response.raise_for_status()
    frame = response.json()
    if not frame.get("fft_magnitude_db") or not frame.get("waterfall_db_per_hz"):
        raise RuntimeError("synthetic spectrum did not produce FFT/waterfall")
    if "rf_assessment" not in frame or "cluster" not in frame:
        raise RuntimeError("RF assessment/cluster metadata missing")
    return "synthetic FFT, waterfall, RF assessment and cluster metadata verified"


def _full_e2e() -> str:
    result = FullPlatformIntegrationPipeline().run()
    if not result.overall_verified:
        raise RuntimeError(str(result))
    return f"full workflow verified; incident={result.incident_id}, ledger_records={result.ledger_records}"


def _artifacts() -> str:
    required = (
        "README.md", "Dockerfile", "docker-compose.yml", ".github/workflows/ci.yml",
        "docs/OVERALL_DEFINITION_OF_DONE.md", "docs/RELEASE_CHECKLIST.md",
        "scripts/release_verify.py", "scripts/hardware_verify.py", "scripts/reliability_soak.py",
        "frontend/tsconfig.json", "frontend/src/dod.ts",
    )
    missing = [p for p in required if not Path(p).is_file()]
    if missing:
        raise RuntimeError(f"missing release artifacts: {missing}")
    return "deployment, verification, documentation and typed-frontend audit artifacts present"


def _typescript() -> str:
    import hashlib
    import json
    source = Path("frontend/src/dod.ts")
    manifest = Path("frontend/dist/build.json")
    if not source.is_file() or not manifest.is_file():
        raise RuntimeError("typed frontend source/build manifest missing")
    expected = json.loads(manifest.read_text(encoding="utf-8")).get("source_sha256")
    actual = hashlib.sha256(source.read_bytes()).hexdigest()
    if expected != actual:
        raise RuntimeError("typed frontend build manifest is stale")
    compiler = shutil.which("tsc")
    if compiler:
        import subprocess
        completed = subprocess.run([compiler, "-p", "frontend/tsconfig.json"], capture_output=True, text=True)
        if completed.returncode:
            raise RuntimeError(completed.stdout + completed.stderr)
        return "TypeScript sources compile and build manifest matches"
    return "precompiled TypeScript build manifest matches source (tsc unavailable at runtime)"


def _hackrf_external() -> str:
    if os.getenv("TRUEPASS_DOD_SKIP_HARDWARE") == "1":
        raise RuntimeError("physical HackerRF verification explicitly skipped")
    config = SDRConfig(2_000_000.0, 100_000_000.0, 0.0, 4096, "hackrf")
    devices = HackRFOneSource.enumerate_devices()
    if not devices:
        raise RuntimeError("no HackerRF One enumerated through SoapySDR")
    with HackRFOneSource(config) as source:
        samples = source.read_samples(4096)
    if len(samples) < 4096:
        raise RuntimeError(f"expected 4096 samples, received {len(samples)}")
    return f"physical HackerRF RX verified ({len(samples)} I/Q samples)"


def _postgres_external() -> str:
    url = os.getenv("TRUEPASS_TEST_DATABASE_URL")
    if not url:
        raise RuntimeError("TRUEPASS_TEST_DATABASE_URL is not configured")
    from sqlalchemy import create_engine, text
    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            value = connection.execute(text("SELECT 1")).scalar_one()
        if value != 1:
            raise RuntimeError("PostgreSQL SELECT 1 returned unexpected result")
    finally:
        engine.dispose()
    return "PostgreSQL connection verified"


def _docker_external() -> str:
    docker = shutil.which("docker")
    if not docker:
        raise RuntimeError("docker executable not installed")
    import subprocess
    completed = subprocess.run([docker, "info"], capture_output=True, text=True)
    if completed.returncode:
        raise RuntimeError("Docker daemon unavailable")
    return "Docker daemon reachable"


def run_overall_dod_audit(*, include_external: bool = True) -> DoDAudit:
    checks = [
        _check("core.routes", "Control Center / UX", _route_check),
        _check("core.spectrum", "Spectrum", _api_check),
        _check("core.e2e", "Full platform", _full_e2e),
        _check("core.release", "Deployment / documentation", _artifacts),
        _check("core.typescript", "Frontend quality", _typescript),
    ]
    if include_external:
        checks.extend([
            _check("external.hackrf", "Hardware integration", _hackrf_external),
            _check("external.postgres", "PostgreSQL / pgvector", _postgres_external),
            _check("external.docker", "Deployment", _docker_external),
        ])
    return DoDAudit(tuple(checks))
