#!/bin/bash

# Détecter si nous sommes sur Windows ou Linux
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    export ADB_HOST="host.docker.internal"
else
    # Linux
    export ADB_HOST="127.0.0.1"
fi

# Démarrer les conteneurs
docker compose up -d 