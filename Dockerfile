# Étape 1: Utiliser une image de base Python
FROM python:3.12-slim

# Étape 2: Définir le répertoire de travail
WORKDIR /app

# Étape 3: Copier les fichiers de votre projet dans l'image Docker
COPY . .

# Étape 4: Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y android-tools-adb

# Étape 5: Exposer le port que Flask utilise
EXPOSE 5000

# Étape 6: Lancer l'application Flask
CMD ["python", "flaskProject.py"]
