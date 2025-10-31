FROM python:3.13-slim AS builder

ENV PYTHONUNBUFFERED=1

# The installer requires curl (and certificates) to download the release archive
COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /uvx /bin/

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app

# Copy dependency file(s) first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies in a separate layer
RUN uv sync --frozen

# Copy application source code
COPY . .

# ---------- Stage 2: Runtime ----------
FROM python:3.13-slim AS runtime

# Security: create a non-root user
RUN useradd --create-home appuser
USER appuser

WORKDIR /app

# Copy dependencies and source code from builder
COPY --from=builder /app /app

CMD [".venv/bin/python", "main.py"]
