# Troubleshooting

## `ModuleNotFoundError: truepass`
Install with `python -m pip install -e .` or use `PYTHONPATH=src` from a source checkout.

## PostgreSQL test is skipped
Set `TRUEPASS_TEST_DATABASE_URL` to a PostgreSQL URL. The default suite intentionally skips external-database integration when no test database is available.

## HackRF is not detected
Confirm `hackrf_info`, SoapySDR, and SoapyHackRF are installed and that the device is visible to the current OS user. TruePass degrades to no devices rather than failing the entire application.

## Dashboard loads but has no events
The dashboard reads the runtime/API event state. Start collectors, POST synthetic events to the API, or connect persistence/integration ingestion.

## Ledger verification fails
Do not edit the evidence JSONL manually. Preserve the file, copy it for investigation, and use `truepass verify ledger --path ...` to identify the first broken chain position.
