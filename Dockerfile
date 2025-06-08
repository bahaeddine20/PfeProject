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

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

RUN mkdir -p static templates test_cases

COPY . .

EXPOSE 5000

CMD ["python", "flaskProject.py"]
