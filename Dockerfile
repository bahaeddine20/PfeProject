# syntax=docker/dockerfile:1.4
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    android-tools-adb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools

WORKDIR /app

COPY requirements.txt .

ARG PIP_CACHE_DIR=/tmp/pip-cache
RUN mkdir -p ${PIP_CACHE_DIR}
RUN pip install --cache-dir=${PIP_CACHE_DIR} -r requirements.txt

# ❌ Ne pas copier tout le code source
# COPY . . ← supprime cette ligne

EXPOSE 5000

# ⚠️ Corrige le chemin vers ton script principal s’il est dans un dossier
CMD ["python", "ServeurFlaskHost/flaskProject.py"]
