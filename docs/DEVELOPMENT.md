# Development

Install development dependencies with `python -m pip install -e '.[dev]'`.

Run the standard validation suite:

```bash
ruff format --check .
ruff check .
mypy src/truepass
pytest -q
python -m compileall -q src tests
PYTHONPATH=src python -m truepass --help
```

Run the automated synthetic E2E scenario with `pytest -q tests/e2e`. Run local benchmarks with `PYTHONPATH=src python scripts/benchmark.py`.

PostgreSQL integration tests are enabled by setting `TRUEPASS_TEST_DATABASE_URL`. Hardware-specific HackRF execution requires local hardware and Soapy drivers; CI verifies the adapter's guards and graceful no-device behavior instead.
