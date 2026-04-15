# ─── Этап 1: development ─────────────────────────────────────────
FROM python:3.12-slim AS development

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir ".[dev]"

COPY . .

EXPOSE 3000 8001
CMD ["sh", "-c", "reflex init && reflex run --env dev"]

# ─── Этап 2: production ──────────────────────────────────────────
FROM python:3.12-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser

COPY pyproject.toml .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir .

COPY --chown=appuser:appgroup . .

RUN reflex init && reflex export --no-zip

USER appuser
EXPOSE 3000 8001

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

CMD ["reflex", "run", "--env", "prod"]
