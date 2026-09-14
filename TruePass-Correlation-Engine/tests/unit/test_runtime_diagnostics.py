from __future__ import annotations

from truepass.config import AppSettings
from truepass.runtime.diagnostics import run_diagnostics


def test_diagnostics_are_structured_without_hardware(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    settings = AppSettings.model_validate(
        {
            "environment": "development",
            "database": {"url": "sqlite+pysqlite:///:memory:"},
            "evidence": {"ledger_path": str(tmp_path / "evidence" / "ledger.jsonl")},
        }
    )
    report = run_diagnostics(settings)
    payload = report.as_dict()
    assert payload["healthy"] is True
    names = {check["name"] for check in payload["checks"]}
    assert {"configuration", "database", "evidence_storage", "evidence_ledger", "hackrf"} <= names
