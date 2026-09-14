from pathlib import Path

from truepass.config import AppSettings


def test_load_toml_and_environment_override(tmp_path: Path, monkeypatch) -> None:
    config = tmp_path / "truepass.toml"
    config.write_text(
        'environment = "test"\n[logging]\nlevel = "WARNING"\njson = true\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("TRUEPASS_LOGGING__LEVEL", "DEBUG")
    settings = AppSettings.load(config)
    assert settings.environment == "test"
    assert settings.logging.level == "DEBUG"
