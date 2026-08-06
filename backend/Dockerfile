FROM python:3.13-slim AS builder

# Cài uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy everything needed for build
COPY pyproject.toml uv.lock README.md ./
COPY src/ src/

# Install dependencies + package (editable mode needs src/)
RUN uv sync --frozen --no-dev

# Stage 2: runtime
FROM python:3.13-slim

WORKDIR /app

# Copy .venv từ builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY migrations/ migrations/
COPY alembic.ini .

ENV PATH="/app/.venv/bin:$PATH"
ENV APP_ENV=production

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uvicorn", "customer_analytics.main:app", "--host", "0.0.0.0", "--port", "8000"]
