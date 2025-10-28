# ==========================================
# TRAINERAPP.AI - Content Automation System
# Production Docker Image
# ==========================================

FROM python:3.11-slim

# Metadata
LABEL maintainer="TrainerApp.AI <tech@trainerapp.ai>"
LABEL description="Automated content generation and posting for TrainerApp.AI"
LABEL version="2.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p storage/raw_inputs \
    storage/generated/images \
    storage/generated/videos \
    storage/generated/temp \
    storage/processed \
    storage/metadata \
    logs

# Set permissions
RUN chmod +x scripts/*.py
RUN chmod +x scripts/generators/*.py
RUN chmod +x scripts/uploaders/*.py

# Environment variables (override with docker run -e)
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
ENV ENVIRONMENT=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command (can be overridden)
CMD ["python", "scripts/orchestrator.py", "--help"]
