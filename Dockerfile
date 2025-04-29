# Étape 1: Utiliser une image de base Python
FROM python:3.12-slim

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    android-tools-adb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Mettre à jour pip et setuptools
RUN pip install --upgrade pip setuptools

# Étape 2: Définir le répertoire de travail
WORKDIR /app

# Étape 3: Copier les fichiers du projet
COPY . .

# Étape 4: Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Installer doctr après pour éviter des conflits potentiels
#RUN pip install --no-cache-dir "python-doctr[torch]"

# Étape 5: Exposer le port Flask
EXPOSE 5000

# Étape 6: Démarrer l'application Flask
CMD ["python", "flaskProject.py"]
