# syntax=docker/dockerfile:1.4
FROM python:3.12-slim

ENV PIP_CACHE_DIR=/tmp/pip-cache

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    android-tools-adb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools

WORKDIR /app

COPY requirements.txt .
RUN mkdir -p ${PIP_CACHE_DIR}
RUN pip install --cache-dir=${PIP_CACHE_DIR} -r requirements.txt

# ⛔️ Ne pas copier tout le code sauf si nécessaire
 COPY . .

EXPOSE 5000

CMD ["python", "flaskProject.py"]
