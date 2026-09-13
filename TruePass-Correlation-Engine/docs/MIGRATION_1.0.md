# Migration Notes — 0.7.0 to 1.0.0

No new database migration is required by Phases 30–37; the finalization work adds testing, deployment, documentation, CI/CD, and integration orchestration around the existing schema.

Before upgrading, back up PostgreSQL and the evidence ledger. Install the new package, run Alembic upgrades normally, run `truepass doctor`, verify the evidence ledger, and execute the API health check. Review `.env.example` because Docker Compose now requires an explicit PostgreSQL password rather than silently accepting a committed default.
