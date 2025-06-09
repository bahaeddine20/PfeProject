"""
Configuration file for managing Docker and local environment settings
"""
import os
import socket

# Docker configuration
DOCKER_CONFIG = {
    'appium_url': 'http://appium:4723',
    'host_url': 'http://host.docker.internal:6000',
    'remote_adb_host': 'host.docker.internal'
}

# Local configuration
LOCAL_CONFIG = {
    'appium_url': 'http://127.0.0.1:4723',
    'host_url': 'http://127.0.0.1:6000',
    'remote_adb_host': '127.0.0.1'
}


def is_running_in_docker():
    """
    Détecte automatiquement si le code s'exécute dans un conteneur Docker.
    Retourne True si dans Docker, False sinon.
    """
    try:
        # Vérifier si le fichier .dockerenv existe
        if os.path.exists('/.dockerenv'):
            return True

        # Vérifier si le hostname contient 'docker'
        hostname = socket.gethostname()
        if 'docker' in hostname.lower():
            return True

        # Vérifier si on peut se connecter à appium:4723
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('appium', 4723))
        sock.close()
        if result == 0:
            return True

        return False
    except:
        return False


# Détection automatique de l'environnement
USE_DOCKER = is_running_in_docker()


# Get current configuration
def get_config():
    return DOCKER_CONFIG if USE_DOCKER else LOCAL_CONFIG


# Helper functions
def get_appium_url():
    return get_config()['appium_url']


def get_host_url():
    return get_config()['host_url']


def get_remote_adb_host():
    return get_config()['remote_adb_host']


# Afficher l'environnement détecté au démarrage
print(f"Environnement détecté : {'Docker' if USE_DOCKER else 'Local'}")