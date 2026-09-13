from truepass.cli.main import main


def test_cli_help(capsys) -> None:
    assert main([]) == 0
    assert "Defensive telemetry" in capsys.readouterr().out
