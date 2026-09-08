# Production Dockerfile for AQPG FastAPI Backend
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies needed for compiling package assets
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose backend API port
EXPOSE 8011

# Run API server with production parameters
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8011"]
