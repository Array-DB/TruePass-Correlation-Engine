FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TRUEPASS_HOST=0.0.0.0 \
    TRUEPASS_PORT=8000

RUN groupadd --system truepass && useradd --system --gid truepass --create-home truepass
WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY migrations ./migrations
COPY alembic.ini ./
COPY config ./config

RUN python -m pip install --upgrade pip && \
    python -m pip install . && \
    mkdir -p /app/data && chown -R truepass:truepass /app

USER truepass
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()" || exit 1

CMD ["truepass", "run", "--host", "0.0.0.0", "--port", "8000"]
