
from appium.options.android import UiAutomator2Options



from appium import webdriver



apps_page="com.android.car.carlauncher/.GASAppGridActivity"
def setup_driver_mobile(device):
    """Initialise et retourne le driver Appium."""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = "15"
    options.device_name = device
    options.adb_exec_timeout = 60000
    options.remote_adb_host="host.docker.internal"
    options.disable_window_animation = True
    options.new_command_timeout = 300
    options.allowInvisibleElements = True
    options.disableIdLocatorAutocompletion = True
    #remote_url = "http://127.0.0.1:4723"
    #remote_url = "http://172.21.0.3:4723"
    remote_url = "http://appium:4723"

    options.set_capability("enforceXPath1", True)
    return webdriver.Remote(remote_url, options=options)


import subprocess
import re


def get_bluetooth_name(driver):
    """
    Récupère le nom de l'appareil Bluetooth via ADB.

    :param driver: Instance du driver Appium.
    :return: Nom du périphérique Bluetooth (str) ou None si non trouvé.
    """
    try:
        # Récupérer le nom du device depuis Appium
        device = driver.capabilities['deviceName']

        # Exécuter la commande ADB pour récupérer les informations Bluetooth
        adb_command = ["adb", "-s", device, "shell", "dumpsys", "bluetooth_manager"]
        result = subprocess.check_output(adb_command, encoding="utf-8")

        # Rechercher la ligne contenant 'name:'
        match = re.search(r'name:\s*([\w\d_\-]+)', result)

        # Retourner le nom trouvé
        return match.group(1) if match else None

    except Exception as e:
        print(f"Erreur lors de la récupération du nom Bluetooth: {e}")
        return None