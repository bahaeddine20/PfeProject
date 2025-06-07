# Étape 1: Utiliser une image de base Python
FROM python:3.12-slim

# Étape 2: Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    android-tools-adb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Étape 3: Mettre à jour pip et setuptools
RUN pip install --upgrade pip setuptools

# Étape 4: Définir le répertoire de travail
WORKDIR /app

# Étape 5: Copier uniquement les fichiers de dépendances d'abord
COPY requirements.txt .

# Étape 6: Installer les dépendances Python avec mise en cache
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Étape 7: Copier uniquement les fichiers nécessaires
COPY flaskProject.py .
COPY config.py .
COPY static/ static/
COPY templates/ templates/
COPY test_cases/ test_cases/

# Étape 8: Exposer le port Flask
EXPOSE 5000

# Étape 9: Démarrer l'application Flask
CMD ["python", "flaskProject.py"]
