import json
import logging

from truepass.monitoring.logging import JsonFormatter


def test_json_formatter_includes_context() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "hello", (), None)
    record.component = "unit"  # type: ignore[attr-defined]
    record.sensor_id = "sensor-1"  # type: ignore[attr-defined]
    payload = json.loads(formatter.format(record))
    assert payload["message"] == "hello"
    assert payload["component"] == "unit"
    assert payload["sensor_id"] == "sensor-1"
