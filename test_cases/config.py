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
    """Détecte l'exécution dans Docker via des méthodes robustes"""
    # 1. Fichier Docker classique
    if os.path.exists('/.dockerenv'):
        return True

    # 2. Vérification via les cgroups (méthode Linux)
    try:
        with open('/proc/self/cgroup', 'r') as cgroup_file:
            if 'docker' in cgroup_file.read():
                return True
    except FileNotFoundError:
        pass

    # 3. Résolution DNS spécifique à Docker
    try:
        socket.gethostbyname('host.docker.internal')
        return True
    except socket.gaierror:
        pass

    return False

# Détection environnement
USE_DOCKER = is_running_in_docker()
IS_WINDOWS = is_windows()

# Configuration unique basée sur Docker
if USE_DOCKER:
    HOST_ADDRESS = "host.docker.internal"  # Nom d'hôte Docker standard
else:
    HOST_ADDRESS = "127.0.0.1"  # Localhost

# Configuration unifiée (supprime la dualité LOCAL/DOCKER)
CONFIG = {
    'appium_url': f'http://{HOST_ADDRESS}:4723',
    'host_url': f'http://{HOST_ADDRESS}:5000',
    'remote_adb_host': HOST_ADDRESS
}

# Helper functions
def get_appium_url():
    return CONFIG['appium_url']

def get_host_url():
    return CONFIG['host_url']

def get_remote_adb_host():
    return CONFIG['remote_adb_host']

# Logs de diagnostic
print(f"Environnement détecté : {'Docker' if USE_DOCKER else 'Local'}")
print(f"Système d'exploitation : {'Windows' if IS_WINDOWS else 'Non-Windows'}")
print(f"Adresse hôte utilisée : {HOST_ADDRESS}")
print(f"URL Appium : {get_appium_url()}")