# Configuration

TruePass loads typed settings from TOML plus `TRUEPASS_*` environment overrides. Nested settings use double underscores, for example `TRUEPASS_DATABASE__URL`.

The committed `config/truepass.toml` is a safe development baseline. Secrets must come from environment variables, deployment secret stores, or mounted protected files rather than source control.

Important deployment values include the database URL, API authentication secret, evidence-ledger path, collector enablement, and SDR settings. Process command-line capture remains disabled by default because arguments may contain secrets or personal data.

Use `truepass doctor` before deployment and `truepass status` to print a redacted configuration summary.
