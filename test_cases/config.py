"""
Configuration file for managing Docker and local environment settings
"""
import os
import socket
import platform

def is_windows():
    """Détecte si le système est Windows"""
    return platform.system().lower() == 'windows'

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
IS_WINDOWS = is_windows()

# Déterminer l'adresse hôte appropriée
HOST_ADDRESS = "host.docker.internal" if IS_WINDOWS else "127.0.0.1"

# Docker configuration
DOCKER_CONFIG = {
    'appium_url': f'http://{HOST_ADDRESS}:4723',
    'host_url': f'http://{HOST_ADDRESS}:5000',
    'remote_adb_host': HOST_ADDRESS
}

# Local configuration
LOCAL_CONFIG = {
    'appium_url': 'http://127.0.0.1:4723',
    'host_url': 'http://127.0.0.1:5000',
    'remote_adb_host': '127.0.0.1'
}

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
print(f"Système d'exploitation : {'Windows' if IS_WINDOWS else 'Linux'}")
print(f"Adresse hôte utilisée : {HOST_ADDRESS}") 