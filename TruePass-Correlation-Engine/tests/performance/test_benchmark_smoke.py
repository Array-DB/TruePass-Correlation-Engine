import subprocess
import sys
from pathlib import Path


def test_benchmark_harness_smoke(tmp_path: Path) -> None:
    output = tmp_path / "bench.json"
    subprocess.run(
        [sys.executable, "scripts/benchmark.py", "--iterations", "10", "--output", str(output)],
        check=True,
        env={"PYTHONPATH": "src"},
    )
    text = output.read_text(encoding="utf-8")
    assert "db_inserts_per_sec_sqlite_local" in text
    assert "spectrogram_frames_per_sec" in text
