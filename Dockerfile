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

# Étape 5: Copier uniquement les fichiers de dépendances d'abord (si présents)
COPY requirements.txt .

# Étape 6: Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Étape 7: Copier le reste du projet (code source, etc.)
COPY . .

# Étape 8: Installer doctr si nécessaire (décommenter si utilisé)
# RUN pip install --no-cache-dir "python-doctr[torch]"

# Étape 9: Exposer le port Flask
EXPOSE 5000

# Étape 10: Démarrer l'application Flask
CMD ["python", "flaskProject.py"]
