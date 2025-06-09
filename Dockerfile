# syntax=docker/dockerfile:1.4
FROM python:3.12-slim

# Install system dependencies with cache optimization
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    android-tools-adb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies with persistent cache
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools && \
    pip install -r requirements.txt

# Copy application code (last step for cache optimization)
COPY . .

EXPOSE 5000

CMD ["python", "flaskProject.py"]