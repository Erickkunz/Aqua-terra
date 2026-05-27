FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# OS deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# App code
COPY backend/ /app/

# Non-root user
RUN groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app \
 && mkdir -p /app/static/uploads \
 && chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/healthz || exit 1

# Gunicorn with uvicorn workers for production-grade serving.
# Workers are configurable via WEB_WORKERS env (defaults to 2).
CMD ["sh", "-c", "gunicorn main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --workers ${WEB_WORKERS:-2} --timeout 60 --forwarded-allow-ips='*' --access-logfile - --error-logfile -"]
