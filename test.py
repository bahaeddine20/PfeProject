from time import sleep

from appium import webdriver
from appium.options.android import UiAutomator2Options


def setup_driver(device):
    """Initialise et retourne le driver Appium."""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = "14"
    options.device_name = device
    options.adb_exec_timeout = 60000
    remote_url = "http://127.0.0.1:4723"
    return webdriver.Remote(remote_url, options=options)



def Print_Activity(driver):
    """Retourne l'activité complète sous la forme 'com.android.car.messenger/.ui.launcher.MessageLauncherActivity'."""
    current_package = driver.current_package
    current_activity = driver.current_activity
    return f"{current_package}/{current_activity}"





import subprocess

def get_connected_devices():
    """Récupère la liste des appareils connectés via ADB"""
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")[1:]  # Ignorer la première ligne

    devices = []
    for line in lines:
        parts = line.split()
        if len(parts) == 2 and parts[1] == "device":
            devices.append(parts[0])  # Ajouter l'ID du device

    return devices

def get_device_type(device_id):
    """Détermine si un appareil est Mobile ou Automotive"""
    result = subprocess.run(["adb", "-s", device_id, "shell", "getprop", "ro.build.characteristics"],
                            capture_output=True, text=True)
    characteristics = result.stdout.strip()

    if "automotive" in characteristics:

        return "Android Automotive 🚗"
    else:
        return "Android Mobile 📱"

def main():
    devices = get_connected_devices()

    if not devices:
        print("Aucun appareil connecté.")
        return

    for device in devices:
        device_type = get_device_type(device)
        print(f"Device ID: {device} → {device_type}")


def afficher_infos_elements(driver):
    elements = driver.find_elements("xpath", "//*")
    for index, element in enumerate(elements):
        try:
            attributs = {
                "text": element.text,
                "class": element.get_attribute("class"),
                "resource-id": element.get_attribute("resource-id"),
                "content-desc": element.get_attribute("content-desc"),
                "bounds": element.get_attribute("bounds"),
            }

            # Vérifier si c'est un TextView
            if attributs["class"] == "android.widget.TextView":
                xpath_suggere = f"//{attributs['class']}[@resource-id='{attributs['resource-id']}' and @text='{attributs['text']}']"
                print(f"Élément {index + 1}: {attributs}")
                print(f"➡️ XPath suggéré : {xpath_suggere}\n")
        except Exception as e:
            print(f"Élément {index + 1}: Erreur - {str(e)}")


def afficher_noms_applications(driver):
    noms_applications = []  # Liste pour stocker les noms des applications

    elements = driver.find_elements("xpath", "//*")
    for element in elements:
        try:
            classe = element.get_attribute("class")
            text = element.text
            resource_id = element.get_attribute("resource-id")

            # Vérifier si l'élément est une application (TextView avec un resource-id spécifique)
            if classe == "android.widget.TextView" and resource_id == "com.android.car.carlauncher:id/app_name":
                noms_applications.append(text)  # Ajouter le nom à la liste
        except Exception as e:
            print(f"Erreur lors de la récupération d'un élément : {str(e)}")

    print("\n📌 Liste des applications détectées :", noms_applications)
    return noms_applications  # Retourner la liste si besoin

# Exemple d'utilisation :
# noms = afficher_noms_applications(driver)
def revenir_a_la_home_page(driver):
    start_Activity_code(driver,"com.android.car.carlauncher/.GASAppGridActivity")
    first = afficher_noms_applications(driver)  # Capturer les apps de la home page
    print("📌 First Home Page détectée :", first)

    while True:
        driver.swipe(600, 500, 900, 500)  # Swipe vers la droite (modifie si nécessaire)
        seconde = afficher_noms_applications(driver)  # Vérifier les apps après swipe

        if first == seconde:
            print("✅ Retour à la first home page !")
            break  # Sortir de la boucle une fois la home page atteinte
        else:
            first = seconde
        print("🔄 Swipe en cours...")

# Exemple d'utilisation :
# revenir_a_la_home_page(driver)
def start_Activity_code(driver, app_activity):
    """Lance une activité spécifique sur un appareil Android via Appium."""
    driver.execute_script('mobile: startActivity', {'intent': app_activity})


def revenir_a_la_setting_haut(driver):
    first = afficher_noms_setting(driver)  # Capturer les apps de la home page
    print("📌 First Home Page détectée :", first)

    while True:
        driver.swipe(300, 400, 300, 700)  # Swipe vers la droite (modifie si nécessaire)
        seconde = afficher_noms_setting(driver)  # Vérifier les apps après swipe

        if first == seconde:
            print("✅ Retour à la first home page !")
            break  # Sortir de la boucle une fois la home page atteinte
        else:
            first = seconde
        print("🔄 Swipe en cours...")




def afficher_noms_setting(driver):
    noms_applications = []  # Liste pour stocker les noms des applications

    elements = driver.find_elements("xpath", "//*")
    for element in elements:
        try:
            classe = element.get_attribute("class")
            text = element.text
            resource_id = element.get_attribute("resource-id")

            # Vérifier si l'élément est une application (TextView avec un resource-id spécifique)
            if classe == "android.widget.TextView" and resource_id == "android:id/title":
                noms_applications.append(text)  # Ajouter le nom à la liste
        except Exception as e:
            print(f"Erreur lors de la récupération d'un élément : {str(e)}")

    print("\n📌 Liste des applications détectées :", noms_applications)
    return noms_applications  # Retourner la liste si besoin


def get_menu_gauche_elements(driver):
    elements = driver.find_elements("xpath", "//android.widget.TextView[@resource-id='android:id/title']")
    menu_list = []

    for element in elements:
        try:
            menu_list.append(element.text)
        except Exception as e:
            print(f"Erreur lors de la récupération d'un élément : {str(e)}")

    return menu_list  # Retourne la liste des éléments


def afficheraLL_infos_elements(driver):
    elements = driver.find_elements("xpath", "//*")
    for index, element in enumerate(elements):
        try:
            attributs = {
                "text": element.text,
                "class": element.get_attribute("class"),
                "resource-id": element.get_attribute("resource-id"),
                "content-desc": element.get_attribute("content-desc"),
                "bounds": element.get_attribute("bounds"),
                "clickable":element.get_attribute("clickable")
            }
            print(f"Élément {index + 1}: {attributs}")
        except Exception as e:
            print(f"Élément {index + 1}: Erreur - {str(e)}")


from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.interaction import POINTER_TOUCH



def click_sur(driver, x, y):
    # Créer un objet ActionBuilder
    actions = ActionBuilder(driver)

    # Créer un pointeur de type "touch"
    pointer = PointerInput(POINTER_TOUCH, "touch")  # Utiliser "touch" comme type de pointeur

    # Ajouter le pointeur à l'ActionBuilder
    actions.add_pointer_input("touch", pointer)  # Ajouter un nom pour le pointeur

    # Définir les actions (déplacement, appui, relâchement)
    actions.pointer_action.move_to_location(x, y)  # Déplacer le pointeur à (x, y)
    actions.pointer_action.pointer_down()  # Appuyer
    actions.pointer_action.pointer_up()  # Relâcher

    # Exécuter les actions
    actions.perform()

import time




import re


def extract_bounds(bounds_str):
    # Utiliser une expression régulière pour extraire les coordonnées
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)

    if match:
        # Retourner les 4 coordonnées sous forme d'entiers
        x1, y1, x2, y2 = map(int, match.groups())
        return x1, y1, x2, y2
    else:
        print("Format de bounds invalide.")
        return None


def open_application(driver,text):
    revenir_a_la_home_page(driver)
    page=True
    while page:
        first = afficher_noms_applications(driver)  # Vérifier les apps après swipe

        if get_element_bounds(driver, text) is not None:
            bounds=get_element_bounds(driver, text)
            x1, y1, x2, y2 = extract_bounds(bounds)
            print(x1, y1, x2, y2)
            x_center = (x1 + x2) // 2
            y_center = (y1 + y2) // 2
            click_sur(driver, x_center, y_center)
            page =False
            return True
        else:
            driver.swipe(700, 500, 400, 500)  # Swipe vers la droite (modifie si nécessaire)

            seconde = afficher_noms_applications(driver)  # Vérifier les apps après swipe

            if first == seconde:
                print("✅ Retour à la first home page !")
                break  # Sortir de la boucle une fois la home page atteinte
            else:
                first = seconde
            print("🔄 Swipe en cours...")

from selenium.webdriver.common.by import By

from selenium.webdriver.common.by import By

def get_elements_by_id(driver, element_id):
    """
    Récupère tous les éléments correspondant à un ID spécifique.

    :param driver: WebDriver Appium
    :param element_id: ID de l'élément (ex: "com.android.car.settings:id/top_level_menu")
    :return: Liste des éléments trouvés (vide si aucun élément)
    """
    try:
        elements = driver.find_elements(By.ID, element_id)  # Récupère les éléments par ID
        return elements
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des éléments avec l'ID {element_id} : {e}")
        return []

from selenium.webdriver.common.by import By
import re

def get_element_bounds(driver, element_id):
    """
    Récupère les bounds (coordonnées) d'un élément donné par son ID.

    :param driver: WebDriver Appium
    :param element_id: ID de l'élément (ex: "com.android.car.settings:id/top_level_menu")
    :return: Bounds sous forme de tuple (x1, y1, x2, y2) ou (0,0,0,0) si l'élément n'existe pas
    """
    try:
        element = driver.find_element(By.ID, element_id)  # Trouver l'élément par ID
        bounds_str = element.get_attribute("bounds")  # Récupérer l'attribut bounds

        # Extraction des coordonnées avec une regex
        match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
        if match:
            return tuple(map(int, match.groups()))  # Retourner (x1, y1, x2, y2)
        else:
            print("⚠️ Format de bounds invalide :", bounds_str)
            return (0, 0, 0, 0)
    except Exception as e:
        print(f"❌ Erreur : Impossible de récupérer les bounds pour '{element_id}' -> {e}")
        return (0, 0, 0, 0)

def element_existe_par_accessibility_id(driver, accessibility_id):
    try:
        driver.find_element("accessibility id", accessibility_id)
        return True  # L'élément existe
    except:
        return False  # L'élément n'existe pas





def get_checked_attribute(driver, element_id):
    try:
        element = driver.find_element("id", element_id)  # Trouver l'élément par ID
        checked_value = element.get_attribute("checked")  # Récupérer l'attribut "checked"
        return checked_value  # Retourner la valeur (True, False ou None)
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de l'attribut checked : {str(e)}")
        return None  # Retourne None si l'élément n'existe pas

import subprocess

def check_language_change(device, reference_language='fr-FR'):
    # Exécution de la commande ADB pour obtenir la langue du système
    result = subprocess.run(["adb", "-s", device, "shell", "settings", "get", "system", "system_locales"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(result)
    if result.returncode != 0:
        print(f"Erreur ADB: {result.stderr}")
        return False

    current_language = result.stdout.strip()

    # Vérifier si plusieurs langues sont retournées et ne garder que la première
    first_language = current_language.split(",")[0] if current_language else ""

    # Vérification si la langue actuelle est différente de la langue de référence
    if first_language == reference_language:
        print(f"🔄 La langue a été modifiée : {first_language}")

        return True
    else:
        print("✅ La langue n'a pas été modifiée.")

        return False


import subprocess
import time


def enable_bluetooth(driver):
    """
    Active le Bluetooth sur un appareil Android via ADB.

    :param driver: Instance du driver Appium
    :return: True si le Bluetooth est activé, False sinon.
    """
    device = driver.capabilities['deviceName']  # Récupérer l'ID du device depuis Appium

    # Vérifier l'état actuel du Bluetooth
    check_cmd = ["adb", "-s", device, "shell", "settings", "get", "global", "bluetooth_on"]
    result = subprocess.run(check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(f"❌ Erreur ADB : {result.stderr}")
        return False

    bluetooth_status = result.stdout.strip()

    if bluetooth_status == "1":
        print("✅ Le Bluetooth est déjà activé.")
        return True  # Bluetooth déjà activé

    # Activer le Bluetooth via ADB
    enable_cmd = ["adb", "-s", device, "shell", "settings", "put", "global", "bluetooth_on", "1"]
    subprocess.run(enable_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Simuler un appui sur le bouton Bluetooth pour certains appareils (optionnel)
    subprocess.run(
        ["adb", "-s", device, "shell", "am", "broadcast", "-a", "android.bluetooth.adapter.action.REQUEST_ENABLE"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Attendre quelques secondes pour que le Bluetooth s'active
    time.sleep(2)

    # Vérifier si le Bluetooth est activé après la commande
    result = subprocess.run(check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.stdout.strip() == "1":
        print("✅ Bluetooth activé avec succès !")
        return True
    else:
        print("❌ Échec de l'activation du Bluetooth.")
        return False
import subprocess

def get_device_datetime_adb(device_id="emulator-5554"):
    """
    Retourne la date et l'heure actuelles du périphérique Android via ADB.
    """
    result = subprocess.run(
        ["adb", "-s", device_id, "shell", "date '+%Y-%m-%d %H:%M:%S'"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()


from datetime import datetime


def get_device_datetime(driver):
    """
    Retourne la date et l'heure du périphérique Android au format 'YYYY-MM-DD HH:MM:SS'.
    """
    device_time_str = driver.device_time  # Ex: "2025-03-12T19:44:49+00:00"
    device_time_obj = datetime.fromisoformat(device_time_str.replace("Z", "+00:00"))  # Convertir ISO 8601
    return device_time_obj.strftime("%Y-%m-%d %H:%M")

from selenium.webdriver.common.by import By

def get_button_elements(driver):
    """
    Retourne les éléments de classe android.widget.Button avec leurs attributs 'bounds' et 'text'.
    :param driver: Instance de WebDriver Appium.
    :return: Liste de dictionnaires contenant 'bounds' et 'text' pour chaque bouton.
    """
    buttons = driver.find_elements(By.CLASS_NAME, "android.widget.EditText")
    button_info = []

    for button in buttons:
        bounds = button.get_attribute("bounds")  # Récupère les attributs 'bounds'
        text = button.text  # Récupère le texte du bouton
        button_info.append({"bounds": bounds, "text": text})

    return button_info

# Exemple d'utilisation :
def compose_time(driver):
    """
    Compose l'heure en utilisant deux boutons : un pour l'heure et un pour les minutes.
    :param driver: Instance de WebDriver Appium.
    :return: L'heure composée sous forme de chaîne (HH:MM).
    """
    buttons = get_button_elements(driver)

    # Vérifier qu'on a bien 2 boutons
    if len(buttons) < 2:
        raise ValueError("Pas assez de boutons pour composer l'heure et les minutes.")

    # Trier les boutons par position X (de gauche à droite)
    buttons.sort(key=lambda btn: int(btn['bounds'].split('[')[1].split(',')[0]))

    # Le premier bouton est pour les heures, le deuxième pour les minutes
    hour = buttons[0]['text']
    minute = buttons[1]['text']

    print(f"Hour: {hour}")
    print(f"Minute: {minute}")

    # Retourner l'heure sous format HH:MM
    return f"{hour}:{minute}"


import re


def swipe_up(driver, bounds):
    """
    Effectue un swipe vers le haut sur un élément en utilisant ses bounds.

    :param driver: Instance de WebDriver Appium.
    :param bounds: Chaîne de bounds sous forme "[x1,y1][x2,y2]".
    """
    # Extraire les coordonnées (x1, y1, x2, y2) depuis la chaîne de bounds
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
    if not match:
        raise ValueError(f"Format de bounds invalide : {bounds}")

    x1, y1, x2, y2 = map(int, match.groups())

    # Calculer le point central de l'élément
    start_x = (x1 + x2) // 2
    start_y = (y1 + y2) // 2

    # Définir les coordonnées de fin pour un swipe vers le haut
    end_x = start_x
    end_y = start_y - 100  # Ajuste cette valeur selon le besoin (plus c'est grand, plus le swipe est long)

    # Effectuer le swipe
    driver.swipe(start_x, start_y, end_x, end_y, 500)  # 500ms pour la durée du swipe

    print(f"Swipe up effectué de ({start_x}, {start_y}) à ({end_x}, {end_y})")
def swipe_down(driver, bounds):
    """
    Effectue un swipe vers le haut sur un élément en utilisant ses bounds.

    :param driver: Instance de WebDriver Appium.
    :param bounds: Chaîne de bounds sous forme "[x1,y1][x2,y2]".
    """
    # Extraire les coordonnées (x1, y1, x2, y2) depuis la chaîne de bounds
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
    if not match:
        raise ValueError(f"Format de bounds invalide : {bounds}")

    x1, y1, x2, y2 = map(int, match.groups())

    # Calculer le point central de l'élément
    start_x = (x1 + x2) // 2
    start_y = (y1 + y2) // 2

    # Définir les coordonnées de fin pour un swipe vers le haut
    end_x = start_x
    end_y = start_y + 100  # Ajuste cette valeur selon le besoin (plus c'est grand, plus le swipe est long)

    # Effectuer le swipe
    driver.swipe(start_x, start_y, end_x, end_y, 500)  # 500ms pour la durée du swipe

    print(f"Swipe up effectué de ({start_x}, {start_y}) à ({end_x}, {end_y})")
import random

def heure_aleatoire():
    heures = random.randint(0, 23)
    minutes = random.randint(0, 59)
    return f"{heures:02d}:{minutes:02d}"


import subprocess


def get_location(driver):
    # Récupérer l'ID du device depuis Appium
    device = driver.capabilities['deviceName']

    # Exécuter la commande adb pour obtenir les données de localisation
    adb_command = ["adb", "-s", device, "shell", "dumpsys", "location"]
    result = subprocess.run(adb_command, capture_output=True, text=True)

    # Modèle Regex pour extraire la latitude et la longitude de la sortie
    location_pattern = r"Location\[gps (-?\d+\.\d+),(-?\d+\.\d+)"

    # Chercher la latitude et la longitude dans la sortie de la commande
    match = re.search(location_pattern, result.stdout)

    if match:
        latitude = match.group(1)
        longitude = match.group(2)
        return float(latitude), float(longitude)
    else:
        return None, None


import subprocess


def get_android_users(driver):
    """
    Récupère la liste des utilisateurs Android via ADB.

    :param driver: L'objet Appium WebDriver.
    :return: Une liste de dictionnaires contenant les IDs, noms et statuts des utilisateurs.
    """
    try:
        # Récupérer l'ID du device depuis Appium
        device = driver.capabilities['deviceName']

        # Exécuter la commande pour obtenir la liste des utilisateurs
        adb_command = ["adb", "-s", device, "shell", "pm list users"]
        result = subprocess.run(adb_command, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Erreur ADB : {result.stderr}")

        # Exécuter la commande pour obtenir l'utilisateur actuel
        current_user_command = ["adb", "-s", device, "shell", "am get-current-user"]
        current_user_result = subprocess.run(current_user_command, capture_output=True, text=True)

        if current_user_result.returncode != 0:
            raise Exception(f"Erreur ADB : {current_user_result.stderr}")

        current_user_id = current_user_result.stdout.strip()  # Récupérer l'ID de l'utilisateur actif

        # Parser la sortie pour extraire les utilisateurs
        users = []
        for line in result.stdout.splitlines():
            if "UserInfo" in line:
                parts = line.split("{")[1].split("}")[0].split(":")
                user_id = parts[0].strip()
                user_name = parts[1].strip()
                user_status = "running" if "running" in line else "inactive"

                users.append({
                    "id": user_id,
                    "name": user_name,
                    "status": "active" if user_id == current_user_id else user_status
                })

        return users

    except Exception as e:
        print(f"Erreur lors de la récupération des utilisateurs : {e}")
        return []

def set_location(driver, x, y):
    """
    Définit une nouvelle position GPS sur l'émulateur ou l'appareil.

    :param driver: Le driver Appium de l'appareil ou de l'émulateur.
    :param x: La longitude à définir (en degrés).
    :param y: La latitude à définir (en degrés).
    :return: True si la commande a réussi, False sinon.
    """
    # Récupérer l'ID du device depuis Appium
    device = driver.capabilities['deviceName']

    # Construire la commande ADB pour définir la localisation
    adb_command = ["adb", "-s", device, "emu", "geo", "fix", str(x), str(y)]

    # Exécuter la commande
    result = subprocess.run(adb_command, capture_output=True, text=True)

    # Vérifier si la commande a réussi
    if result.returncode == 0:
        print(f"Position définie à Longitude: {x}, Latitude: {y}")
        return True
    else:
        print(f"Erreur lors de la définition de la position : {result.stderr}")
        return False


# Exemple d'utilisation
# set_location(driver, -74.0060, 40.7128)  # Exemples de coordonnées pour New York

from appium import webdriver

def click_element_by_text_att(driver, text):
    element = driver.find_element(By.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')
    element.click()
# Exemple d'utilisation

# Exemple d'utilisation :
# swipe_up(driver, "[862,356][926,404]")
def get_added_user(old_users, new_users):
    """
    Compare deux listes d'utilisateurs et retourne l'utilisateur ajouté.

    :param old_users: Liste initiale des utilisateurs (avant modification).
    :param new_users: Liste mise à jour des utilisateurs (après modification).
    :return: Le dictionnaire de l'utilisateur ajouté ou None si aucun ajout.
    """
    old_user_ids = {user["id"] for user in old_users}

    for user in new_users:
        if user["id"] not in old_user_ids:
            return user  # Retourne le premier utilisateur ajouté trouvé

    return None  # Aucun utilisateur ajouté

import re
import subprocess
import io
import subprocess
import re
from PIL import Image
import os

def capture_element_screenshot(driver, bounds, output_path="element_screenshot.png"):
    """
    Capture un screenshot d'un élément spécifique à partir de ses bounds via ADB,
    le transfère sur le PC, puis supprime le fichier du périphérique.

    :param driver: Instance Appium WebDriver.
    :param bounds: Coordonnées de l'élément sous la forme "[x1,y1][x2,y2]".
    :param output_path: Nom du fichier de sortie pour l'image rognée.
    """
    # Récupérer l'ID du périphérique via Appium
    device = driver.capabilities.get('deviceName')

    if not device:
        raise ValueError("Impossible de récupérer l'ID du périphérique.")

    # Extraire les coordonnées des bounds
    match = re.match(r"\[(\d+),(\d+)]\[(\d+),(\d+)]", bounds)
    if not match:
        raise ValueError("Format des bounds invalide.")

    x1, y1, x2, y2 = map(int, match.groups())

    # Chemins des fichiers
    remote_screenshot_path = "/sdcard/full_screenshot.png"
    local_screenshot_path = "full_screenshot.png"

    try:
        # Capture d'écran complète via ADB
        subprocess.run(["adb", "-s", device, "shell", "screencap", "-p", remote_screenshot_path], check=True)

        # Copier le fichier sur le PC
        subprocess.run(["adb", "-s", device, "pull", remote_screenshot_path, local_screenshot_path], check=True)

        # Charger l'image avec PIL
        img = Image.open(local_screenshot_path)

        # Rogner l'image pour ne garder que la zone de l'élément
        cropped_img = img.crop((x1, y1, x2, y2))
        cropped_img.save(output_path)

        print(f"Capture d'élément enregistrée sous : {output_path}")

    finally:
        # Supprimer le fichier distant du périphérique
        subprocess.run(["adb", "-s", device, "shell", "rm", remote_screenshot_path], check=True)
        # Optionnel : Supprimer le fichier local après traitement
        if os.path.exists(local_screenshot_path):
            os.remove(local_screenshot_path)


def is_aligned(text_el, switch_el, tolerance=50):
    # Récupérer la position et taille des éléments
    text_y = text_el.location['y']
    text_height = text_el.size['height']
    switch_y = switch_el.location['y']
    switch_height = switch_el.size['height']

    # Comparaison des lignes verticales (alignement)
    return abs(text_y - switch_y) < tolerance and abs((text_y + text_height) - (switch_y + switch_height)) < tolerance

def find_switch_by_label(driver, label_text):
    # 1. Chercher tous les TextView
    text_views = driver.find_elements("class name", "android.widget.TextView")

    # 2. Identifier l'élément dont le texte correspond
    target_label = None
    for tv in text_views:
        if label_text.lower() in tv.text.lower():
            target_label = tv
            break

    if not target_label:
        print(f"[ERROR] Label '{label_text}' non trouvé")
        return None

    # 3. Chercher tous les Switchs (toggles)
    switches = driver.find_elements("class name", "android.widget.Switch")

    # 4. Trouver celui qui est aligné avec le label
    for sw in switches:
        if is_aligned(target_label, sw):
            return sw

    print(f"[ERROR] Aucun switch aligné avec '{label_text}' trouvé.")
    return None

def is_wifi_enabled(driver):
    device = driver.capabilities['deviceName']  # Récupérer l'ID du device depuis Appium

    try:
        # Utiliser ADB pour vérifier l'état du Wi-Fi
        result = subprocess.check_output(["adb", "-s", device, "shell", "dumpsys", "wifi"], text=True)

        # Chercher la ligne indiquant l'état du Wi-Fi
        if "Wi-Fi is enabled" in result or "Wi-Fi enabled" in result:
            return True
        elif "Wi-Fi is disabled" in result or "Wi-Fi disabled" in result:
            return False
        else:
            print("État du Wi-Fi non déterminé.")
            return None

    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution ADB : {e}")
        return None


import cv2
import numpy as np
import os
import tempfile
from appium.webdriver.common.appiumby import AppiumBy
from io import BytesIO
from PIL import Image


def find_icon_position(driver, icon_name):
    """
    Trouve la position d'une icône sur l'écran du device Android.

    Args:
        driver: Instance du driver Appium
        icon_name: Nom du fichier de l'icône à trouver (doit être dans le dossier 'icons')

    Returns:
        Tuple (x, y, width, height) de la position de l'icône ou None si non trouvée
    """
    # Chemin vers l'icône template
    template_path = os.path.join('iconshd/', f'{icon_name}.png')
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Le fichier d'icône {template_path} n'existe pas")

    # Prendre un screenshot avec Appium
    screenshot = driver.get_screenshot_as_png()
    img = np.array(Image.open(BytesIO(screenshot)))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Charger le template
    template = cv2.imread(template_path)
    if template is None:
        raise ValueError(f"Impossible de charger l'icône {template_path}")

    h, w = template.shape[:2]

    # Convertir en niveaux de gris
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Faire la correspondance de template
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8

    # Trouver la meilleure correspondance
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val >= threshold:
        x, y = max_loc
        return (x, y, w, h)
    else:
        return None


import os
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from PIL import Image


def get_text_bounds(image_path, text_to_find):
    """
    Extrait les coordonnées (xmin, ymin, xmax, ymax) du texte trouvé dans l'image.

    :param image_path: Chemin vers l'image
    :param text_to_find: Mot ou texte à chercher
    :return: Tuple (xmin, ymin, xmax, ymax) ou None si non trouvé
    """
    # Charger l'image pour obtenir ses dimensions
    image = Image.open(image_path)
    width, height = image.size

    # OCR avec Doctr
    doc = DocumentFile.from_images(image_path)
    model = ocr_predictor(pretrained=True)
    result = model(doc)

    # Récupérer les blocs de texte
    blocks = result.pages[0].blocks  # On suppose qu'une seule page

    for block in blocks:
        for line in block.lines:
            for word in line.words:
                if text_to_find.lower() in word.value.lower():
                    xmin_norm, ymin_norm = word.geometry[0]
                    xmax_norm, ymax_norm = word.geometry[1]

                    xmin = int(xmin_norm * width)
                    ymin = int(ymin_norm * height)
                    xmax = int(xmax_norm * width)
                    ymax = int(ymax_norm * height)

                    return (xmin, ymin, xmax, ymax)

    return None
def get_text_bounds_driver(driver,text_to_find):
    screenshot = driver.get_screenshot_as_png()
    (x, y, w, h)=get_text_bounds(screenshot, text_to_find)
    return (x, y, w, h)


import subprocess

def is_in_call(driver):
    device = driver.capabilities.get('deviceName')
    if not device:
        print("❌ Aucune information sur l'ID du device.")
        return None

    try:
        result = subprocess.check_output(
            ["adb", "-s", device, "shell", "dumpsys", "telephony.registry"], text=True
        )

        for line in result.splitlines():
            if "mCallState=" in line:
                call_state = line.strip().split("=")[-1]
                if call_state == "2":
                    print("📞 L'appareil est en appel.")
                    return True
                elif call_state == "1":
                    print("🔔 L'appareil a un appel entrant.")
                    return True
                else:
                    print("✅ Aucun appel en cours.")
                    return False

        print("⚠️ État d'appel non déterminé.")
        return None

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution ADB : {e}")
        return None



# Exemple d'utilisation
# icon_position = find_icon_position(driver, "notif_menu")
# if icon_position:
#     x, y, w, h = icon_position
#     print(f"Icône trouvée à : x={x}, y={


import subprocess
import os
import re
from datetime import datetime


def download_latest_recording(device, destination_dir='.'):
    """
    Télécharge le dernier fichier audio depuis l'émulateur Android.
    Version améliorée avec recherche approfondie et création de dossier si nécessaire.

    Args:
        device (str): ID de l'appareil (ex: 'emulator-5554')
        destination_dir (str): Dossier de destination local

    Returns:
        str: Chemin du fichier téléchargé ou None
    """
    # Chemins possibles (ajustés pour Android Automotive)
    possible_paths = [
        '/sdcard/Music/Recordings',
        '/sdcard/Music/Recording',
        '/sdcard/Recordings',
        '/sdcard/Recording',
        '/storage/emulated/0/Music/Recordings',
        '/storage/emulated/0/Recordings',
        '/data/media/0/Music/Recordings',  # Ajout pour Android Automotive
        '/sdcard/Android/media/com.android.soundrecorder'  # Dossier par défaut de l'appli Enregistreur
    ]

    try:
        # 1. Trouver le dossier existant
        valid_path = None
        for path in possible_paths:
            result = subprocess.run(
                ['adb', '-s', device, 'shell', 'test', '-d', path, '&&', 'echo', 'exists'],
                capture_output=True,
                text=True
            )
            if 'exists' in result.stdout.strip():
                valid_path = path
                break

        if not valid_path:
            print("🔍 Recherche approfondie des fichiers audio...")
            # Si aucun dossier connu, chercher tous les fichiers audio récents
            find_cmd = [
                'adb', '-s', device, 'shell',
                'find', '/sdcard', '/storage', '/data/media',
                '-type', 'f', '(', '-name', '*.wav', '-o', '-name', '*.mp3', '-o', '-name', '*.aac', ')',
                '-exec', 'ls', '-lt', '{}', '+'
            ]
            result = subprocess.run(find_cmd, capture_output=True, text=True)

            if not result.stdout.strip():
                print("❌ Aucun fichier audio trouvé sur l'appareil")
                return None

            # Prendre le fichier le plus récent
            latest = result.stdout.split('\n')[0]
            parts = re.split(r'\s+', latest.strip(), maxsplit=7)
            remote_path = parts[-1]

            # Téléchargement direct
            filename = os.path.basename(remote_path)
            local_path = os.path.join(destination_dir, filename)
            os.makedirs(destination_dir, exist_ok=True)

            subprocess.run(
                ['adb', '-s', device, 'pull', remote_path, local_path],
                check=True
            )
            print(f"✅ Fichier trouvé et téléchargé: {local_path}")
            return local_path

        # 2. Lister les fichiers par date (nouveaux en premier)
        list_cmd = [
            'adb', '-s', device, 'shell',
            'find', valid_path, '-type', 'f',
            '-exec', 'ls', '-lt', '{}', '+'
        ]
        result = subprocess.run(list_cmd, capture_output=True, text=True)

        if not result.stdout.strip():
            print(f"ℹ️ Dossier trouvé mais vide: {valid_path}")
            return None

        # Prendre le premier fichier (le plus récent)
        first_line = result.stdout.split('\n')[0]
        parts = re.split(r'\s+', first_line.strip(), maxsplit=7)
        remote_path = parts[-1]
        filename = os.path.basename(remote_path)
        local_path = os.path.join(destination_dir, filename)

        # 3. Télécharger
        os.makedirs(destination_dir, exist_ok=True)
        subprocess.run(
            ['adb', '-s', device, 'pull', remote_path, local_path],
            check=True
        )
        print(f"✅ Fichier téléchargé: {local_path}")
        return local_path

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur ADB: {e.stderr}")
        return None
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")
        return None


if __name__ == "__main__":

    main()

    driver = setup_driver("emulator-5554")
    device_id = "emulator-5554"  # Remplacer par votre ID d'émulateur
    destination = "./enregistrements"  # Dossier de destination

    # Créer le dossier s'il n'existe pas
    os.makedirs(destination, exist_ok=True)

    downloaded_file = download_latest_recording(
        device="emulator-5554",
        destination_dir="./enregistrements"
    )
    if downloaded_file:
        print(f"Fichier téléchargé: {downloaded_file}")
    else:
        print("Échec du téléchargement")
    #set_location(driver, -74.0060, 40.7128)  # Exemples de coordonnées pour New York
    # Exemple d'utilisation dans un test Appium :
    # driver = webdriver.Remote("http://localhost:4723/wd/hub", desired_caps)
    #bounds_exemple = "[404,76][1408,696]"
    #capture_element_screenshot(driver, bounds_exemple)
    # Exemple d'éléments obtenus avec UIAutomator (comme tu l'as montré)
    # Utilisation dans ton script de test
    #print(is_in_call(driver))
    #print(get_text_bounds("screenshot1.png", "Son"))
    #print(get_location(driver))
    #swipe_down(driver, "[862,356][926,404]")
    #print(get_android_users(driver))
    #enable_bluetooth(driver)
    #print(get_element_bounds(driver,"com.android.car.settings:id/top_level_menu"))
    #print(get_checked_attribute(driver,"android:id/switch_widget"))
    #print(check_language_change("emulator-5554","fr-FR"))
    #revenir_a_la_home_page(driver)
    #
    print(Print_Activity(driver))
    # #afficher_noms_setting(driver)
    afficheraLL_infos_elements(driver)
    # Test de la fonction

    # y_center = (619 + 657) // 2  # 638
    #
    # click_sur(driver, x_center, y_center)
    # sleep(5)
    # revenir_a_la_home_page(driver)
    # bounds = get_element_bounds(driver, "YouTube")
    # print(bounds)  # Output: '[1170,414][1249,452]'
    # # Exemple d'utilisation
    # x1, y1, x2, y2 = extract_bounds(bounds)
    # print(x1, y1, x2, y2)  # Sortie : 1170 414 1249 452
    # x_center = (x1 + x2) // 2  # 956
    # y_center = (y1 + y2) // 2  # 638
    # click_sur(driver, x_center, y_center)
    #open_application(driver, "teyuz")
    #revenir_a_la_setting_haut(driver)
    # first=afficher_noms_applications(driver)
    # driver.swipe(600, 500, 900, 500)  # Le swipe vers le haut
    # seconde=afficher_noms_applications(driver)
    # if first == seconde:
    #     print("first home page")
    # else:
    #     print("second home page")
    #
