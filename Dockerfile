# syntax=docker/dockerfile:1

# ── Base image ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Avoid .pyc files and force unbuffered stdout/stderr (better container logs)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ── Dependencies (cached layer) ─────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Application code ────────────────────────────────────────────────────────
COPY Server.py .
COPY Functions/ ./Functions/

# ── Runtime configuration ───────────────────────────────────────────────────
# Bind to all interfaces inside the container so the port is reachable from the host.
ENV MCP_HOST=0.0.0.0 \
    MCP_PORT=8000

EXPOSE 8000

# Run as a non-root user
RUN useradd --create-home --uid 10001 appuser
USER appuser

CMD ["python", "Server.py"]
