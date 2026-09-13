# Installation

## Requirements

- Python 3.13+
- PostgreSQL 17+ for production persistence
- pgvector for vector similarity in PostgreSQL
- Optional receive-only HackRF One: SoapySDR + SoapyHackRF installed through the operating system or Conda
- Docker/Compose for container deployment

## Local

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
truepass doctor
truepass run --host 127.0.0.1 --port 8000
```

Open `/docs` for OpenAPI and `/dashboard` for the local operator interface.

## Docker

Copy `.env.example` to `.env`, replace `POSTGRES_PASSWORD`, optionally set `TRUEPASS_API_KEY`, then run:

```bash
docker compose up --build -d
```

Enable Prometheus with:

```bash
docker compose --profile monitoring up --build -d
```

TruePass runs as an unprivileged container user and the API container drops Linux capabilities.
