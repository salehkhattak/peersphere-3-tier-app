# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS base

# System dependencies (Pillow needs libjpeg, zlib)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libjpeg-dev \
        zlib1g-dev \
        libpng-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Set working directory inside container
WORKDIR /app

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# ── Stage 2: App ───────────────────────────────────────────────────────────────
# Copy backend source
COPY backend/ ./backend/

# Copy frontend assets
COPY frontend/ ./frontend/

# Copy entrypoint
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Create upload and DB directories with correct permissions
RUN mkdir -p /app/frontend/static/uploads \
             /app/backend/instance \
    && chown -R appuser:appuser /app /docker-entrypoint.sh

USER appuser

# Flask app lives in /app/backend
WORKDIR /app/backend

# Expose port
EXPOSE 5000

ENTRYPOINT ["/docker-entrypoint.sh"]
