```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install FFmpeg and system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        gcc \
        build-essential \
        libmagic1 \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency file first for better Docker layer caching
COPY requirements.txt .

RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . .

# Create required directories
RUN mkdir -p \
    logs \
    temp \
    cache

# Expose Render/Railway/Koyeb port
EXPOSE 10000

# Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
CMD curl -f http://127.0.0.1:${PORT:-10000}/health || exit 1

# Start Bot
CMD ["python", "-m", "main"]
```
