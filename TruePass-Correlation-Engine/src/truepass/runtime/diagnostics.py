"""Operational diagnostics used by the CLI and API health surfaces."""

from __future__ import annotations

import os
import platform
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from truepass.config import AppSettings
from truepass.database.session import create_database_engine
from truepass.evidence.ledger import FileEvidenceLedger
from truepass.sdr.sources import HackRFOneSource

DiagnosticLevel = Literal["ok", "warning", "error"]


@dataclass(frozen=True, slots=True)
class DiagnosticCheck:
    name: str
    level: DiagnosticLevel
    message: str
    details: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DiagnosticReport:
    checks: tuple[DiagnosticCheck, ...]

    @property
    def healthy(self) -> bool:
        return not any(check.level == "error" for check in self.checks)

    def as_dict(self) -> dict[str, object]:
        return {
            "healthy": self.healthy,
            "python": platform.python_version(),
            "platform": platform.platform(),
            "checks": [check.as_dict() for check in self.checks],
        }


def _path_check(name: str, path: Path, *, require_file: bool = False) -> DiagnosticCheck:
    if require_file and not path.is_file():
        return DiagnosticCheck(name, "warning", f"file not found: {path}", {"path": str(path)})
    parent = path.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return DiagnosticCheck(name, "error", f"cannot create/access {parent}: {exc}", {"path": str(parent)})
    if not os.access(parent, os.W_OK | os.X_OK):
        return DiagnosticCheck(name, "error", f"path is not writable: {parent}", {"path": str(parent)})
    return DiagnosticCheck(name, "ok", "path is writable", {"path": str(parent)})


def run_diagnostics(settings: AppSettings, *, config_path: str | Path | None = None) -> DiagnosticReport:
    """Run safe, read-mostly deployment checks.

    Missing external infrastructure is reported without mutating it. A database
    failure is an error in production and a warning in development/test so that
    hardware-independent development remains possible.
    """

    checks: list[DiagnosticCheck] = []
    resolved_config = Path(config_path or os.getenv("TRUEPASS_CONFIG", "config/truepass.toml"))
    if resolved_config.is_file():
        checks.append(DiagnosticCheck("configuration", "ok", "configuration file loaded", {"path": str(resolved_config)}))
    else:
        checks.append(DiagnosticCheck("configuration", "warning", "configuration file not found; safe defaults/environment may be in use", {"path": str(resolved_config)}))

    ledger_path = Path(settings.evidence.ledger_path)
    checks.append(_path_check("evidence_storage", ledger_path, require_file=False))
    if ledger_path.exists():
        verification = FileEvidenceLedger(ledger_path).verify()
        level: DiagnosticLevel = "ok" if verification.valid else "error"
        checks.append(DiagnosticCheck("evidence_ledger", level, "ledger verified" if verification.valid else f"ledger verification failed: {verification.error}", {"records": verification.records, "path": str(ledger_path)}))
    else:
        checks.append(DiagnosticCheck("evidence_ledger", "warning", "ledger has not been created yet", {"path": str(ledger_path)}))

    engine = create_database_engine(settings)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        checks.append(DiagnosticCheck("database", "ok", "database connection succeeded", {}))
    except SQLAlchemyError as exc:
        level = "error" if settings.environment.lower() == "production" else "warning"
        checks.append(DiagnosticCheck("database", level, "database unavailable", {"error": str(exc).splitlines()[0][:300]}))
    finally:
        engine.dispose()

    devices = HackRFOneSource.enumerate_devices()
    if devices:
        checks.append(DiagnosticCheck("hackrf", "ok", f"detected {len(devices)} HackRF device(s)", {"devices": [device.raw for device in devices]}))
    else:
        checks.append(DiagnosticCheck("hackrf", "warning", "no HackRF device detected (or SoapySDR/SoapyHackRF unavailable)", {"devices": []}))

    return DiagnosticReport(tuple(checks))
