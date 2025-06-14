from appium.options.android import UiAutomator2Options

from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.interaction import POINTER_TOUCH

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException

from appium import webdriver

from datetime import datetime
import time

import random

from config import get_host_url, get_appium_url, get_remote_adb_host

url_host = get_host_url()
# url_host="http://127.0.0.1:6000"


apps_page = "com.android.car.carlauncher/.GASAppGridActivity"


def setup_driver(device):
    """Initialise et retourne le driver Appium."""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = "14"
    options.device_name = device
    # options.adb_exec_timeout = 60000
    options.remote_adb_host = get_remote_adb_host()
    # remote_url = "http://127.0.0.1:4723"
    # remote_url = "http://172.21.0.3:4723"
    remote_url = get_appium_url()

    options.uiautomator2ServerPort = 8201

    return webdriver.Remote(remote_url, options=options)


import subprocess


def switch_android_user(device, user_id):
    """Switch Android user via ADB."""
    command = ["adb", "-s", device, "shell", "am", "switch-user", str(user_id)]
    subprocess.run(command, check=True)


def close_driver(driver):
    """Ferme proprement le driver Appium."""
    if driver:
        driver.quit()


def start_activity_code(driver, app_activity):
    """Lance une activité spécifique sur un appareil Android via Appium."""
    driver.execute_script('mobile: startActivity', {'intent': app_activity})


def close_activity(driver, app_package):
    """
    Ferme une application spécifique sur un appareil Android via Appium.
    
    Args:
        driver: L'instance du driver Appium
        app_package: Le package de l'application à fermer (ex: 'com.example.audioapplicationtest')
    """
    try:
        # Force l'arrêt de l'application
        driver.execute_script('mobile: terminateApp', {'bundleId': app_package})
        print(f"Application {app_package} fermée avec succès")
        return True
    except Exception as e:
        print(f"Erreur lors de la fermeture de l'application {app_package}: {str(e)}")
        return False


def close_activity_robot(driver, app_package):
    """
    Version de close_activity adaptée pour Robot Framework.
    Utilise plusieurs méthodes pour s'assurer que l'application est bien fermée.
    
    Args:
        driver: L'instance du driver Appium
        app_package: Le package de l'application à fermer
    """
    try:
        # Méthode 1: Utiliser terminateApp
        try:
            driver.execute_script('mobile: terminateApp', {'bundleId': app_package})
            print(f"Application {app_package} fermée avec terminateApp")
        except Exception as e:
            print(f"Échec de terminateApp: {str(e)}")

        # Méthode 2: Utiliser la touche HOME
        try:
            driver.press_keycode(3)  # KEYCODE_HOME
            print("Touche HOME pressée")
        except Exception as e:
            print(f"Échec de la touche HOME: {str(e)}")

        # Méthode 3: Utiliser ADB pour forcer l'arrêt
        try:
            device = driver.capabilities.get('deviceName')
            if device:
                subprocess.run(
                    ["adb", "-s", device, "shell", "am", "force-stop", app_package],
                    check=True,
                    capture_output=True
                )
                print(f"Application {app_package} fermée avec force-stop")
        except Exception as e:
            print(f"Échec de force-stop: {str(e)}")

        # Vérifier si l'application est toujours en cours d'exécution
        time.sleep(1)  # Attendre un peu
        current_package = driver.current_package
        if current_package == app_package:
            raise Exception(f"L'application {app_package} est toujours en cours d'exécution")
        
        print(f"Application {app_package} fermée avec succès")
    except Exception as e:
        print(f"Erreur lors de la fermeture de l'application {app_package}: {str(e)}")
        raise Exception(f"Échec de la fermeture de l'application {app_package}")


def is_activity_active(driver, expected_activity):
    """Vérifie si l'activité actuelle correspond à l'activité spécifiée."""
    current_activity = driver.current_activity
    print(current_activity)
    return current_activity in expected_activity


def Print_Activity(driver):
    """Retourne l'activité complète sous la forme 'com.android.car.messenger/.ui.launcher.MessageLauncherActivity'."""
    current_package = driver.current_package
    current_activity = driver.current_activity
    return f"{current_package}/{current_activity}"


def print_activity2(driver):
    """Retourne l'activité complète sous la forme 'com.android.car.messenger/.ui.launcher.MessageLauncherActivity'."""
    current_package = driver.current_package
    current_activity = driver.current_activity
    return f"{current_package}/{current_activity}"


def check_element_exists(driver, xpath):
    """
    Vérifie si un élément existe en utilisant le XPath donné.

    :param driver: L'instance du WebDriver.
    :param xpath: Le XPath de l'élément à vérifier.
    :return: True si l'élément existe, False sinon.
    """
    try:
        # Rechercher l'élément par XPath
        driver.find_element(By.XPATH, xpath)
        return True  # L'élément existe
    except NoSuchElementException:
        return False  # L'élément n'existe pas


def get_element_text(driver, xpath):
    """Récupère le texte d'un élément spécifié par son XPath."""
    try:
        element = driver.find_element(By.XPATH, xpath)
        return element.text
    except NoSuchElementException:
        return "Élément non trouvé"


def swap_Until(driver, target_xpath):
    """
    Effectue un swipe vers le haut jusqu'à ce que l'élément cible spécifié par 'target_xpath' apparaisse.

    :param driver: Instance du WebDriver Appium.
    :param target_xpath: XPath de l'élément cible.
    """
    # Vérifiez si l'élément cible est déjà visible
    try:
        element = driver.find_element(By.XPATH, target_xpath)
        if element.is_displayed():
            print("L'élément est déjà visible.")
            return
    except NoSuchElementException:
        pass  # Si l'élément n'est pas trouvé, continuez le swipe

    # Effectuer un swipe vers le haut jusqu'à ce que l'élément soit trouvé
    while True:
        # Effectuer le swipe
        driver.swipe(250, 400, 250, 600, 100)  # Le swipe vers le haut

        # Vérifier si l'élément cible est présent
        try:
            element = driver.find_element(By.XPATH, target_xpath)
            if element.is_displayed():
                print("L'élément a été trouvé.")
                break
        except NoSuchElementException:
            pass  # Si l'élément n'est toujours pas trouvé, continuer à swipernt n'a pas été trouvé après plusieurs tentatives.")


def afficher_noms_applications(driver):
    noms_applications = []

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


cor_all_apps_x = 640
cor_all_apps_y = 745


def revenir_a_la_home_page(driver):
    click_sur(driver, cor_all_apps_x, cor_all_apps_y)
    driver.press_keycode(3)  # KEYCODE_HOME

    click_sur(driver, cor_all_apps_x, cor_all_apps_y)

    first = afficher_noms_applications(driver)  # Capturer les apps de la home page
    print("📌 First Home Page détectée :", first)

    while True:
        driver.swipe(200, 500, 900, 500, 100)  # Swipe vers la droite (modifie si nécessaire)
        seconde = afficher_noms_applications(driver)  # Vérifier les apps après swipe

        if first == seconde:
            print("✅ Retour à la first home page !")
            break  # Sortir de la boucle une fois la home page atteinte
        else:
            first = seconde
        print("🔄 Swipe en cours...")


def click_element_by_text(driver, text):
    try:
        # Chercher tous les éléments contenant le texte spécifié
        elements = driver.find_elements(By.XPATH, f'//android.widget.Button[@text="{text}"]')

        # Vérifier si des éléments ont été trouvés
        if elements:
            # Cliquer sur le premier élément trouvé
            elements[0].click()
            print(f"Clic effectué sur l'élément avec le texte: {text}")
        else:
            print(f"Aucun élément trouvé avec le texte: {text}")

    except Exception as e:
        print(f"Erreur lors du clic sur l'élément avec le texte '{text}': {e}")


def get_element_bounds(driver, text):
    try:
        # Recherche exactement "Settings" sans aucune variation
        element = driver.find_element(By.XPATH, f"//android.widget.TextView[normalize-space(@text)='{text}']")

        # Récupérer l'attribut 'bounds'
        bounds_str = element.get_attribute("bounds")

        return bounds_str if bounds_str else None
    except Exception as e:
        print(f"Erreur : {e}")
        return None


def afficher_noms_setting(driver):
    noms_applications = []  # Liste pour stocker les noms des settings

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


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def click_element_by_text_att(driver, text, timeout=20):
    locator = (By.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')
    element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(locator)
    )
    element.click()


def is_within_bounds(child_bounds, parent_bounds):
    if not child_bounds or not parent_bounds:
        return False  # Évite les erreurs si l'un des bounds est None

    x1_c, y1_c, x2_c, y2_c = child_bounds
    x1_p, y1_p, x2_p, y2_p = parent_bounds

    return (x1_p <= x1_c <= x2_p and y1_p <= y1_c <= y2_p) or (x1_p <= x2_c <= x2_p and y1_p <= y2_c <= y2_p)


def afficher_noms_setting_bound(driver, xpathid):
    try:
        elements = driver.find_elements("xpath", f"//*[@resource-id='{xpathid}']//android.widget.TextView")
        noms = {el.text.strip() for el in elements if el.text.strip()}
        return list(noms)
    except Exception as e:
        print("⚠️ Erreur récupération noms:", e)
        return []


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


def click_sur_bound(driver, bound):
    # bound est sous la forme (x_min, y_min, x_max, y_max)
    x_min, y_min, x_max, y_max = bound

    # Calcul du centre
    x_center = (x_min + x_max) // 2
    y_center = (y_min + y_max) // 2

    actions = ActionBuilder(driver)

    # Créer un pointeur de type "touch"
    pointer = PointerInput(POINTER_TOUCH, "touch")  # Utiliser "touch" comme type de pointeur

    # Ajouter le pointeur à l'ActionBuilder
    actions.add_pointer_input("touch", pointer)  # Ajouter un nom pour le pointeur

    # Définir les actions (déplacement, appui, relâchement)
    actions.pointer_action.move_to_location(x_center, y_center)  # Déplacer le pointeur à (x, y)
    actions.pointer_action.pointer_down()  # Appuyer
    actions.pointer_action.pointer_up()  # Relâcher

    # Exécuter les actions
    actions.perform()


def check_element_exists_by_id(driver, element_id):
    """
    Vérifie si un élément existe en utilisant son ID.

    :param driver: L'instance du WebDriver.
    :param element_id: L'ID de l'élément à vérifier (ex: "com.android.systemui:id/notifications").
    :return: True si l'élément existe, False sinon.
    """
    try:
        # Rechercher l'élément par son ID
        driver.find_element(By.ID, element_id)
        return True  # L'élément existe
    except NoSuchElementException:
        return False  # L'élément n'existe pas


def check_element_exists_by_text(driver, text):
    """
    Vérifie si un élément contenant le texte spécifié existe sur la page.

    :param driver: L'instance du WebDriver.
    :param text: Le texte à rechercher.
    :return: True si l'élément existe, False sinon.
    """
    try:
        # Récupérer tous les éléments de la page
        elements = driver.find_elements(By.XPATH, "//*")

        # Parcourir chaque élément
        for element in elements:
            try:
                # Vérifier si le texte de l'élément correspond
                if text in element.text:
                    return True  # L'élément existe
            except StaleElementReferenceException:
                # Ignorer les éléments qui ne sont plus dans le DOM
                continue

        # Si aucun élément ne correspond
        return False
    except Exception as e:
        print(f"Erreur lors de la recherche de l'élément : {e}")
        return False


from selenium.common.exceptions import NoSuchElementException
import time


def afficher_notification(driver, max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Tentative {attempt} : swipe vers le bas avec ActionBuilder")

            # Créer un objet ActionBuilder
            actions = ActionBuilder(driver)

            # Créer un pointeur de type "touch"
            pointer = PointerInput(POINTER_TOUCH, "touch")

            # Ajouter le pointeur à l'ActionBuilder
            actions.add_pointer_input("touch", pointer)

            # Définir les actions (swipe du haut vers le bas)
            actions.pointer_action.move_to_location(500, 25)
            actions.pointer_action.pointer_down()
            actions.pointer_action.move_to_location(500, 400)
            actions.pointer_action.pointer_up()

            # Exécuter les actions
            actions.perform()

            time.sleep(2)

            if check_notification_visible(driver):
                print("✅ Notification affichée avec succès.")
                return True
            else:
                print("❌ Notification non détectée, nouvelle tentative...")

        except Exception as e:
            print(f"Erreur à la tentative {attempt}: {e}")
            time.sleep(1)

    print("❌ Échec après plusieurs tentatives.")
    return False


def check_notification_visible(driver):
    try:
        notif = driver.find_element("id", "com.android.systemui:id/notifications")
        return notif.is_displayed()
    except NoSuchElementException:
        return False


def get_element_bounds_byId(driver, element_id):
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


def get_element_bounds(driver, text):
    try:

        # Chercher avec XPath exact
        xpath_exact = f"//android.widget.TextView[@text='{text}']"
        element = driver.find_elements("xpath", xpath_exact)

        if not element:
            # Chercher avec XPath 'contains' si le texte peut être partiellement présent
            xpath_contains = f"//android.widget.TextView[contains(@text, '{text}')]"
            element = driver.find_elements("xpath", xpath_contains)

        if element:
            return element[0].get_attribute("bounds")

        print(f"Aucun élément trouvé avec le texte: {text}")
        return None

    except Exception as e:
        print(f"Erreur: {e}")
        return None


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


def open_application_with_click(driver, text):

    """
    Ouvre une application soit par son activité si connue, soit par recherche visuelle
    """
    # Dictionnaire des activités connues
    known_activities = {
        "Paramètres": "com.android.car.settings/.Settings_Launcher_Homepage",
        "Settings": "com.android.car.settings/.Settings_Launcher_Homepage",
    }

    # Vérifier si l'application a une activité connue
    if text in known_activities:
        try:
            # Essayer d'ouvrir directement par l'activité
            activity = known_activities[text]
            print(f"🔄 Tentative d'ouverture de {text} via l'activité: {activity}")
            start_activity_code(driver, activity)
            print(Print_Activity(driver))
            
            # Vérifier si l'activité a bien démarré
            current_activity = Print_Activity(driver)
            if activity.split('/')[0] in current_activity:
                print(f"✅ {text} ouvert avec succès via l'activité")
                return True
            else:
                print(f"⚠️ L'activité n'a pas démarré correctement, tentative par recherche visuelle")
        except Exception as e:
            print(f"⚠️ Erreur lors de l'ouverture par activité: {str(e)}")
            print("🔄 Tentative par recherche visuelle...")

    # Si l'activité n'est pas connue ou si l'ouverture a échoué, utiliser la méthode visuelle
    revenir_a_la_home_page(driver)
    page = True
    while page:
        first = afficher_noms_applications(driver)
        if text in first:
            if get_element_bounds(driver, text) is not None:
                bounds = get_element_bounds(driver, text)
                x1, y1, x2, y2 = extract_bounds(bounds)
                x_center = (x1 + x2) // 2
                y_center = (y1 + y2) // 2
                click_sur(driver, x_center, y_center)
                page = False
                return True
        else:
            driver.swipe(1200, 600, 500, 600, 200)
            seconde = afficher_noms_applications(driver)

            if first == seconde:
                print("✅ Retour à la première page !")
                return False
            else:
                first = seconde
            print("🔄 Swipe en cours...")


def search_application(driver, text):
    revenir_a_la_home_page(driver)
    click_sur(driver, cor_all_apps_x, cor_all_apps_y)
    click_sur(driver, cor_all_apps_x, cor_all_apps_y)

    print("111111111111111111111")
    page = True
    while page:
        print("2222222222222222")
        first = afficher_noms_applications(driver)  # Vérifier les apps après swipe
        if text in first:
            if get_element_bounds(driver, text) is not None:
                print("3333333333333333333")
                bounds = get_element_bounds(driver, text)
                x1, y1, x2, y2 = extract_bounds(bounds)
                print(x1, y1, x2, y2)
                x_center = (x1 + x2) // 2
                y_center = (y1 + y2) // 2
                page = False
                return True
        else:
            driver.swipe(1200, 500, 500, 500, 100)  # Swipe vers la droite (modifie si nécessaire)
            print("444444444444444444444'")
            seconde = afficher_noms_applications(driver)  # Vérifier les apps après swipe

            if first == seconde:
                print("55555555555555555")
                print("✅ Retour à la first home page !")
                return False  # Sortir de la boucle une fois la home page atteinte
            else:
                print("6666666666666666666")
                first = seconde
            print("🔄 Swipe en cours...")


def all_setting_list(driver, xpathid):
    setting = []
    revenir_a_la_setting_haut(driver)
    first = afficher_noms_setting_bound(driver, xpathid)
    setting = setting + first
    print("📌 First Home Page détectée :", first)

    while True:
        driver.swipe(300, 500, 300, 220, 100)
        time.sleep(0.2)
        seconde = afficher_noms_setting_bound(driver, xpathid)
        setting = setting + seconde

        if first == seconde:
            print("✅ Retour à la first home page !")
            return remove_duplicates(setting)
        else:
            first = seconde
        print("🔄 Swipe en cours...")

    return remove_duplicates(setting)


def remove_duplicates(input_list):
    """
    Supprime les doublons d'une liste tout en conservant l'ordre d'apparition des éléments.

    :param input_list: Liste d'éléments avec des doublons
    :return: Liste sans doublons
    """
    seen = set()  # Ensemble pour vérifier les doublons
    result = []  # Liste pour stocker les éléments uniques

    for item in input_list:
        if item not in seen:
            result.append(item)  # Ajouter l'élément si non vu
            seen.add(item)  # Ajouter à l'ensemble des éléments vus

    return result


def element_exists(input_list, element):
    """
    Vérifie si un élément existe dans une liste.

    :param input_list: Liste dans laquelle rechercher l'élément
    :param element: Élément à rechercher
    :return: True si l'élément existe, sinon False
    """
    return element in input_list


def clique_sur_setting_include(driver, nom, xpathid):
    setting = []
    revenir_a_la_setting_haut(driver)  # Revenir au haut des settings
    first = afficher_noms_setting_bound(driver, xpathid)  # Obtenir les premiers éléments
    parent_bounds = get_element_bounds_byId(driver, xpathid)

    setting = setting + first
    print("First Home Page détectée :", first)
    seconde = first

    # Calcul des coordonnées centrales pour le swipe
    x_middle = (parent_bounds[0] + parent_bounds[2]) // 2  # Milieu en X
    y_start = (parent_bounds[1] + parent_bounds[3]) // 2 + 100  # Légèrement en dessous du centre
    y_end = (parent_bounds[1] + parent_bounds[3]) // 2 - 150  # Légèrement au-dessus du centre

    while True:
        # Vérifier si une partie du nom recherché est dans les éléments actuels
        for element_text in seconde:
            if nom in element_text:  # Si une partie du texte correspond
                print(f" {nom} trouvé ! Appui sur le texte contenant '{element_text}'.")
                # Si trouvé, clique sur l'élément correspondant
                element = driver.find_element("xpath", f"//*[contains(@text, '{element_text}')]")
                return element.click()  # Clique sur l'élément trouvé

        driver.swipe(x_middle, y_start, x_middle, y_end, 100)
        print(" Swipe effectué...")
        seconde = afficher_noms_setting_bound(driver, xpathid)
        setting = setting + seconde

        # Si la page a recommencé à afficher les mêmes éléments (retour à la première page)
        if first == seconde:
            print(" Retour à la first home page !")
            return remove_duplicates(setting)  # Si on est revenu à la première page, on arrête le swipe

        first = seconde  # Mettre à jour 'first' pour la prochaine itération

    # Retourner la liste sans doublons après avoir arrêté de swiper
    return remove_duplicates(setting)


def revenir_a_la_setting_haut(driver):
    max_swipes = 20
    first = afficher_noms_setting(driver)
    print("📌 First Home Page détectée :", first)

    for i in range(max_swipes):
        driver.swipe(300, 400, 300, 750, 50)  # Durée réduite à 50 ms
        print(f"🔄 Swipe #{i + 1} en cours...")

        seconde = afficher_noms_setting(driver)
        if first == seconde:
            print("✅ Retour à la first home page !")
            return
        else:
            first = seconde

    print("⚠️ Max swipes atteints. Impossible de revenir à la home page.")


def clique_sur_setting(driver, nom, xpathid):
    def get_middle_coords(bounds):
        x_middle = (bounds[0] + bounds[2]) // 2
        y_middle = (bounds[1] + bounds[3]) // 2
        return x_middle, y_middle

    def try_click_on_text(text):
        try:
            locator = (By.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(locator)
            )
            element.click()
            return True
        except Exception:
            return False

    def swipe_vertical(direction='down'):
        delta = 150
        if direction == 'up':
            driver.swipe(x, y + delta, x, y - delta, 300)
        else:
            driver.swipe(x, y - delta, x, y + delta, 300)

    def afficher_page_actuelle():
        return set(afficher_noms_setting_bound(driver, xpathid))

    # --- Initialisation
    parent_bounds = get_element_bounds_byId(driver, xpathid)
    print(parent_bounds)
    x, y = get_middle_coords(parent_bounds)

    visited = set()
    max_swipes = 20

    # Vérification directe sans swiper
    current_items = afficher_page_actuelle()
    visited.update(current_items)
    if nom in current_items:
        print(f"✅ '{nom}' trouvé sans swipe. Appui en cours...")
        try_click_on_text(nom)
        return

    # 🔽 Balayage vers le bas
    for i in range(max_swipes):
        swipe_vertical('down')
        print(f"🔽 Swipe vers le bas #{i + 1}")
        current_items = afficher_page_actuelle()
        if nom in current_items:
            print(f"✅ '{nom}' trouvé en bas ! Appui en cours...")
            try_click_on_text(nom)
            return
        if current_items.issubset(visited):
            print("🛑 Plus de nouveaux éléments en bas. Fin de balayage.")
            break
        visited.update(current_items)
    visited.clear()
    # 🔼 Optionnel : remonter si besoin
    for i in range(max_swipes):
        swipe_vertical('up')
        print(f"🔼 Swipe vers le haut #{i + 1}")
        current_items = afficher_page_actuelle()
        if nom in current_items:
            print(f"✅ '{nom}' trouvé en remontant ! Appui en cours...")
            try_click_on_text(nom)
            return
        if current_items.issubset(visited):
            print("🛑 Aucun nouvel élément en haut. Fin de balayage.")
            break
        visited.update(current_items)

    print(f"❌ '{nom}' introuvable après balayage complet.")
    return list(visited)


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


def activer_bluetooth_si_desactive(driver, element_id):
    try:
        # Trouver le toggle Bluetooth
        toggle = driver.find_element("id", element_id)

        # Vérifier l'état du toggle Bluetooth
        checked_value = toggle.get_attribute("checked")

        if checked_value == "true":
            print("✅ Le Bluetooth est déjà activé.")
        else:
            print("❌ Le Bluetooth est désactivé. Activation en cours...")
            toggle.click()
            print("✅ Bluetooth activé avec succès !")

    except Exception as e:
        print(f"❌ Erreur lors de l'activation du Bluetooth : {str(e)}")


def desactive_bluetooth_si_activer(driver, element_id):
    try:
        # Trouver le toggle Bluetooth
        toggle = driver.find_element("id", element_id)

        # Vérifier l'état du toggle Bluetooth
        checked_value = toggle.get_attribute("checked")

        if checked_value == "true":
            toggle.click()
            print("✅ Le Bluetooth est désactivé.")


        else:
            print("❌ Le Bluetooth est deja  désactivé. ")
            print("✅ Bluetooth désactivé avec succès !")

    except Exception as e:
        print(f"❌ Erreur lors de l'desactivation du Bluetooth : {str(e)}")


def verfier_bluetooth_activer(driver, element_id):
    try:
        # Trouver le toggle Bluetooth
        toggle = driver.find_element("id", element_id)

        # Vérifier l'état du toggle Bluetooth
        checked_value = toggle.get_attribute("checked")

        if checked_value == "true":
            return True
        else:
            return False

    except Exception as e:
        print(f"❌ Erreur lors de l'activation du Bluetooth : {str(e)}")


def est_bluetooth_active(device):
    try:
        # Exécuter la commande ADB pour récupérer l'état du Bluetooth
        result = subprocess.run(
            ["adb", "-s", device, "shell", "settings get global bluetooth_on"],
            capture_output=True, text=True, check=True
        )

        # Récupérer la valeur retournée (0 = désactivé, 1 = activé)
        bluetooth_state = result.stdout.strip()

        if bluetooth_state == "1":
            print("✅ Bluetooth est activé.")
            return True
        elif bluetooth_state == "0":
            print("❌ Bluetooth est désactivé.")
            return False
        else:
            print(f"⚠️ Valeur inattendue retournée : {bluetooth_state}")
            return None

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur ADB : {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur inattendue : {str(e)}")
        return None


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


import subprocess


def is_wifi_enabled_adb(driver):
    # Récupérer l'ID du device depuis Appium
    device = driver.capabilities.get('deviceName')
    if not device:
        print("❌ Aucune information sur l'ID du device.")
        return None

    # Utiliser ADB pour vérifier l'état du Wi-Fi
    result = subprocess.check_output(["adb", "-s", device, "shell", "dumpsys", "wifi"], text=True)

    # Chercher la ligne indiquant l'état du Wi-Fi
    if "Wi-Fi is enabled" in result or "Wi-Fi enabled" in result:
        print("✅ Le Wi-Fi est activé.")
        return True
    elif "Wi-Fi is disabled" in result or "Wi-Fi disabled" in result:
        print("❌ Le Wi-Fi est désactivé.")
        return False
    else:
        print("⚠️ État du Wi-Fi non déterminé.")
        return None


import subprocess


def is_gps_enabled_adb(driver):
    """
    Vérifie si le GPS (services de localisation) est activé via ADB pour un device donné.
    """
    # Récupérer l'ID du device depuis Appium
    device = driver.capabilities.get('deviceName')
    if not device:
        print("❌ Aucune information sur l'ID du device.")
        return None

    try:
        # Vérifie le mode de localisation (0: off, 1: device only, 2: battery saving, 3: high accuracy)
        result = subprocess.check_output(["adb", "-s", device, "shell", "settings", "get", "secure", "location_mode"],
                                         text=True)
        location_mode = result.strip()

        if location_mode == "0":
            print("❌ Le GPS est désactivé (location_mode = 0).")
            return False
        elif location_mode in ["1", "2", "3"]:
            print(f"✅ Le GPS est activé (location_mode = {location_mode}).")
            return True
        else:
            print(f"⚠️ Mode de localisation inconnu : {location_mode}")
            return None

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la commande ADB : {e}")
        return None


def activer_wifi_si_desactive(driver):
    try:
        # Trouver le toggle Bluetooth
        switch_element = find_switch_by_label(driver, "Wi-Fi")
        current_state = switch_element.get_attribute("checked")
        print(current_state)

        if switch_element and current_state == "false":
            switch_element.click()

    except Exception as e:
        print(f"❌ Erreur lors de l'activation du wifi : {str(e)}")


def activer_toggle_si_desactive(driver, text):
    try:
        # Trouver le toggle Bluetooth
        switch_element = find_switch_by_label(driver, text)
        current_state = switch_element.get_attribute("checked")
        print(current_state)

        if switch_element and current_state == "false":
            switch_element.click()

    except Exception as e:
        print(f"❌ Erreur lors de l'activation du wifi : {str(e)}")


def desactiver_wifi_si_active(driver):
    try:
        # Trouver le toggle Bluetooth
        switch_element = find_switch_by_label(driver, "Wi-Fi")
        current_state = switch_element.get_attribute("checked")
        print(current_state)

        if switch_element and current_state == "true":
            switch_element.click()

    except Exception as e:
        print(f"❌ Erreur lors de l'activation du wifi : {str(e)}")


def is_active_wifi_ui(driver):
    try:
        # Trouver le toggle Wi-Fi
        switch_element = find_switch_by_label(driver, "Wi-Fi")

        if not switch_element:
            print("❌ Switch Wi-Fi introuvable")
            return False

        current_state = switch_element.get_attribute("checked")
        print(f"État actuel du Wi-Fi : {current_state}")

        if current_state == "true":
            return True
        else:
            return False

    except Exception as e:
        print(f"❌ Erreur lors de l'activation du Wi-Fi : {str(e)}")
        return False


def get_system_language(device):
    try:
        # Exécuter la commande adb pour obtenir la locale du système
        result = subprocess.run(
            ["adb", "-s", device, "shell", "settings", "get", "system", "system_locales"],
            capture_output=True, text=True, check=True
        )
        lang_code = result.stdout.strip().split("-")[0]  # Extraire "fr" de "fr-FR"

        # Retourner "fr" si la langue est le français, sinon "eng"
        return "fr" if lang_code == "fr" else "eng"
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution d'ADB : {e}")
        return "eng"  # Valeur par défaut si une erreur se produit
    except Exception as e:
        print(f"Erreur générale : {e}")
        return "eng"  # Valeur par défaut en cas d'erreur


import subprocess
import time


def check_language_change(device, reference_language, max_attempts=3, wait_between_attempts=2):
    for attempt in range(1, max_attempts + 1):
        print(f"Tentative {attempt} : Vérification de la langue...")

        # Exécution de la commande ADB
        result = subprocess.run(["adb", "-s", device, "shell", "settings", "get", "system", "system_locales"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print(f"❌ Erreur ADB : {result.stderr.strip()}")
        else:
            current_language = result.stdout.strip()
            first_language = current_language.split(",")[0] if current_language else ""

            if first_language == reference_language:
                print(f"✅ La langue a bien été modifiée : {first_language}")
                return True
            else:
                print(f"🔁 Langue actuelle : {first_language} ≠ attendue : {reference_language}")

        if attempt < max_attempts:
            print(f"⏳ Nouvelle tentative dans {wait_between_attempts} secondes...")
            time.sleep(wait_between_attempts)

    print("❌ Échec : la langue n'a pas été modifiée après plusieurs tentatives.")
    return False


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


def activer_notification_si_desactive(driver, element_id):
    try:
        # Trouver le toggle Bluetooth
        toggle = driver.find_element("id", element_id)

        # Vérifier l'état du toggle notification
        checked_value = toggle.get_attribute("checked")

        if checked_value == "true":
            print("✅ Le notification est déjà activé.")
        else:
            print("❌ Le notification est désactivé. Activation en cours...")
            toggle.click()
            print("✅ notification activé avec succès !")

    except Exception as e:
        print(f"❌ Erreur lors de l'activation du notification : {str(e)}")


def desactive_notification_si_activer(driver, element_id):
    try:
        # Trouver le toggle Bluetooth
        toggle = driver.find_element("id", element_id)

        # Vérifier l'état du toggle notification
        checked_value = toggle.get_attribute("checked")

        if checked_value == "false":
            print("✅ Le notification est déjà desactive.")
        else:
            print("❌ Le notification est activer. Activation en cours...")
            toggle.click()
            print("✅ notification desactive avec succès !")

    except Exception as e:
        print(f"❌ Erreur lors de l'activation du notification : {str(e)}")


def install_apk(driver, apk_path):
    """
    Installe un fichier APK sur un appareil Android via ADB.

    :param driver: Instance du driver Appium (ou autre contenant l'identifiant du device)
    :param apk_path: Chemin absolu du fichier APK à installer
    :return: True si l'installation réussit, False sinon
    """
    try:
        # Obtenir l'identifiant du device depuis le driver
        device_id = driver.capabilities.get("deviceName", "")

        if not device_id:
            print("Erreur : Aucun identifiant de device trouvé.")
            return False

        # Exécuter la commande ADB pour installer l'APK
        result = subprocess.run(["adb", "-s", device_id, "install", apk_path],
                                capture_output=True, text=True)

        if result.returncode == 0:
            print("Installation réussie :", result.stdout)
            return True
        else:
            print("Échec de l'installation :", result.stderr)
            return False
    except Exception as e:
        print(f"Erreur lors de l'installation de l'APK : {e}")
        return False


import subprocess


def is_app_installed(driver, package_name):
    """
    Vérifie de manière fiable si une application est installée sur l'appareil via ADB.
    Utilise 'pm path' pour s'assurer que le package est vraiment présent.

    Args:
        driver: Instance du driver Appium.
        package_name (str): Nom du package à vérifier.

    Returns:
        bool: True si le package est installé (présence de l'APK), False sinon.
    """
    device_id = driver.capabilities.get("deviceName")
    if not device_id:
        raise ValueError("Impossible de récupérer l'ID du device depuis le driver.")

    try:
        result = subprocess.run(
            ["adb", "-s", device_id, "shell", "pm", "path", package_name],
            capture_output=True,
            text=True,
            check=True
        )
        return bool(result.stdout.strip())

    except subprocess.CalledProcessError:
        # La commande échoue si le package n'existe pas
        return False


def get_device_datetime(driver):
    """
    Retourne la date et l'heure du périphérique Android au format 'YYYY-MM-DD HH:MM:SS'.
    """
    device_time_str = driver.device_time  # Ex: "2025-03-12T19:44:49+00:00"
    device_time_obj = datetime.fromisoformat(device_time_str.replace("Z", "+00:00"))  # Convertir ISO 8601
    return device_time_obj.strftime("%Y-%m-%d %H:%M")


def get_device_datetime_heure(driver):
    """
    Retourne la date et l'heure du périphérique Android au format 'YYYY-MM-DD HH:MM:SS'.
    """
    device_time_str = driver.device_time  # Ex: "2025-03-12T19:44:49+00:00"
    device_time_obj = datetime.fromisoformat(device_time_str.replace("Z", "+00:00"))  # Convertir ISO 8601
    return device_time_obj.strftime("%H:%M")


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
import time


def change_date(driver, date):
    """
    Sets the time by using two buttons: one for hours and one for minutes.
    Uses adaptive swipe distances based on the difference between current and target values.

    :param driver: Appium WebDriver instance
    :param date: Target time string in format "HH:MM"
    :return: The set time as string (HH:MM)
    """
    # Validate input format
    time_match = re.fullmatch(r"(\d{2}):(\d{2})", date)
    if not time_match:
        raise ValueError("Invalid time format. Expected HH:MM")

    target_hour, target_minute = map(int, time_match.groups())

    while True:
        buttons = get_button_elements(driver)

        # Validate we have enough buttons
        if len(buttons) < 2:
            raise ValueError("Not enough buttons to set time (need 2)")

        # Sort buttons left to right
        buttons.sort(key=lambda btn: get_bounds_x(btn['bounds']))

        current_hour = int(buttons[0]['text'])
        current_minute = int(buttons[1]['text'])

        print(f"Current time: {current_hour:02d}:{current_minute:02d}")
        print(f"Target time: {target_hour:02d}:{target_minute:02d}")

        # Adjust hours if needed
        if current_hour != target_hour:
            diff = abs(target_hour - current_hour)
            direction = "up" if target_hour > current_hour else "down"
            swipe_time_picker(driver, buttons[0]['bounds'], direction, diff)
            continue

        # Adjust minutes if needed
        if current_minute != target_minute:
            diff = abs(target_minute - current_minute)
            direction = "up" if target_minute > current_minute else "down"
            swipe_time_picker(driver, buttons[1]['bounds'], direction, diff)
            continue

        # Both match - we're done
        return f"{current_hour:02d}:{current_minute:02d}"


def get_bounds_x(bounds_str):
    """Helper to extract x coordinate from bounds string"""
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if not match:
        raise ValueError(f"Invalid bounds format: {bounds_str}")
    return int(match.group(1))


from typing import Optional, Tuple
import time
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement


def wait_until_element_is_visible(
        driver: WebDriver,
        by: str,
        value: str,
        timeout: int = 10,
        poll_frequency: float = 0.5
) -> Optional[WebElement]:
    """
    Attend qu'un élément soit visible sur un appareil Android en utilisant Appium pur.

    Args:
        driver: Instance Appium WebDriver
        by: Stratégie de localisation (MobileBy constants)
        value: Valeur du localisateur
        timeout: Temps d'attente maximum en secondes (défaut: 10)
        poll_frequency: Intervalle de vérification en secondes (défaut: 0.5)

    Returns:
        WebElement: L'élément trouvé et visible

    Raises:
        TimeoutException: Si l'élément n'est pas trouvé dans le délai imparti
    """
    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            element = driver.find_element(by, value)
            if element.is_displayed():
                return element
        except Exception:
            pass
        time.sleep(poll_frequency)

    raise TimeoutException(
        f"Élément avec le localisateur '{by}={value}' non visible après {timeout} secondes"
    )


def swipe_time_picker(driver, bounds, direction, difference):
    """
    Performs an adaptive swipe on a time picker element based on the difference

    :param driver: Appium WebDriver instance
    :param bounds: Bounds string in format "[x1,y1][x2,y2]"
    :param direction: "up" or "down"
    :param difference: Numerical difference between current and target value
    """
    # Parse bounds
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
    if not match:
        raise ValueError(f"Invalid bounds format: {bounds}")

    x1, y1, x2, y2 = map(int, match.groups())

    # Calculate element center and size
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    element_height = y2 - y1

    # Calculate adaptive swipe distance
    base_distance = element_height * 2  # Base swipe distance
    max_distance = element_height * 8  # Maximum swipe distance

    # Scale swipe distance based on difference
    if difference > 10:
        swipe_distance = max_distance  # Big swipe for large differences
    elif difference > 5:
        swipe_distance = min(max_distance, base_distance * 2)
    else:
        swipe_distance = base_distance

    # Set swipe coordinates
    if direction == "up":
        end_y = center_y - swipe_distance
    elif direction == "down":
        end_y = center_y + swipe_distance
    else:
        raise ValueError("Direction must be 'up' or 'down'")

    # Perform swipe (faster swipe for larger distances)
    swipe_duration = max(100, min(500, 200 + difference * 20))
    driver.swipe(center_x, center_y, center_x, end_y, swipe_duration)

    print(f"Swiping {direction} (difference: {difference}) from ({center_x}, {center_y}) to ({center_x}, {end_y})")
    time.sleep(0.3 + difference * 0.05)  # Adaptive pause


def heure_aleatoire():
    heures = random.randint(0, 23)
    minutes = random.randint(0, 59)
    return f"{heures:02d}:{minutes:02d}"


def pressKey(driver, keycode):
    """
    Effectue un appui sur une touche spécifique via son keycode.

    :param driver: Instance de WebDriver Appium.
    :param keycode: Code de la touche à presser (int).
    """
    driver.press_keycode(keycode)
    print(f"Keycode {keycode} pressé.")


# Exemple d'utilisation :
# press_key(driver, 66)  # Appuie sur "ENTER"


def get_location_viaAdb(device_id):
    # Exécuter la commande adb pour obtenir les données de localisation
    adb_command = ["adb", "-s", device_id, "shell", "dumpsys", "location"]
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


def set_location_viaAdb(device_id, x, y):
    """
    Définit une nouvelle position GPS via une API Flask sur le host.
    """
    payload = {
        "device_id": device_id,
        "longitude": x,
        "latitude": y
    }

    try:
        response = requests.post(url_host + "/setlocation", json=payload)
        if response.status_code == 200:
            print(f"[OK] Position définie : {x}, {y}")
            return True
        else:
            print(f"[ERREUR] Réponse API : {response.text}")
            return False
    except requests.RequestException as e:
        print(f"[ERREUR] Exception lors de la requête : {e}")
        return False


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


def is_bluetooth_connected(driver, name_bluetooth):
    """
    Vérifie si un appareil Bluetooth spécifique est connecté.

    :param driver: Instance du driver Appium.
    :param name_bluetooth: Nom de l'appareil Bluetooth à vérifier.
    :return: True si l'appareil est connecté, False sinon.
    """
    try:
        # Récupérer l'ID du device depuis Appium
        device = driver.capabilities['deviceName']

        # Exécuter la commande ADB pour obtenir l'état Bluetooth
        adb_command = ["adb", "-s", device, "shell", "dumpsys", "bluetooth_manager"]
        result = subprocess.check_output(adb_command, encoding="utf-8")

        # Vérifier si l'appareil Bluetooth est connecté
        pattern = rf'{re.escape(name_bluetooth)}.*state=Connected'
        return bool(re.search(pattern, result))

    except Exception as e:
        print(f"Erreur lors de la vérification du Bluetooth: {e}")
        return False


import requests


def simulate_incoming_call(driver, phone_number):
    """
    Simule un appel entrant sur un émulateur Android en envoyant une requête à l'endpoint /call.

    :param driver: Instance Appium WebDriver
    :param phone_number: Numéro de téléphone à simuler (string)
    :return: True si la simulation a réussi, False sinon
    """
    device_name = driver.capabilities.get('deviceName')
    if not device_name:
        print("[ERREUR] deviceName non trouvé dans les capabilities du driver.")
        return False

    payload = {
        "device_name": device_name,
        "phone_number": phone_number
    }

    try:
        response = requests.post(url_host + "/call", json=payload)
        if response.status_code == 200:
            print(f"[OK] Appel simulé : {phone_number} vers {device_name}.")
            return True
        else:
            print(f"[ERREUR] Échec de la simulation d'appel. Réponse : {response.text}")
            return False
    except requests.RequestException as e:
        print(f"[ERREUR] Exception lors de la requête : {e}")
        return False


# def simulate_incoming_call(driver, phone_number):
#     """
#     Simule un appel entrant sur un émulateur Android via ADB et vérifie si la commande a réussi.
#
#     :param driver: Instance Appium WebDriver
#     :param phone_number: Numéro de téléphone à simuler (string)
#     :return: True si la commande a réussi, False sinon
#     """
#     device_name = driver.capabilities.get('deviceName')
#     if not device_name:
#         print("[ERREUR] deviceName non trouvé dans les capabilities du driver.")
#         return False
#
#     # Construire la commande
#     command = ["adb", "-s", device_name, "emu", "gsm", "call", phone_number]
#
#     try:
#         result = subprocess.run(command, capture_output=True, text=True, check=True)
#         output = result.stdout.strip()
#         if "OK" in output:
#             print(f"[OK] Appel simulé depuis {phone_number} vers {device_name}.")
#             return True
#         else:
#             print(f"[ERREUR] Réponse inattendue : {output}")
#             return False
#     except subprocess.CalledProcessError as e:
#         print(f"[ERREUR] Échec de la simulation d'appel : {e.stderr.strip()}")
#         return False

import logging
import requests
import functools
from typing import List, Optional, Dict, Any, Tuple
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Constantes pour les retries et timeouts
MAX_RETRIES = 3
RETRY_DELAY = 2
DEFAULT_TIMEOUT = 10
SCROLL_ATTEMPTS = 5
SCROLL_DELAY = 0.5


def retry_on_failure(max_attempts: int = MAX_RETRIES, delay: int = RETRY_DELAY):
    """Décorateur pour réessayer une fonction en cas d'échec."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Tentative {attempt + 1}/{max_attempts} échouée: {str(e)}")
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            logger.error(f"Toutes les tentatives ont échoué: {str(last_exception)}")
            raise last_exception

        return wrapper

    return decorator


@retry_on_failure()
def find_element_with_scroll(driver: webdriver.Remote, text: str, max_attempts: int = SCROLL_ATTEMPTS) -> Optional[
    Tuple[int, int, int, int]]:
    """Recherche un élément en scrollant si nécessaire."""
    try:
        # Essayer de trouver l'élément directement
        element = driver.find_element(By.XPATH, f"//*[@text='{text}']")
        bounds = element.get_attribute("bounds")
        if bounds:
            return extract_bounds(bounds)

        # Si non trouvé, essayer avec scroll
        screen_size = driver.get_window_size()
        start_y = screen_size['height'] * 0.8
        end_y = screen_size['height'] * 0.2

        for attempt in range(max_attempts):
            # Scroll
            driver.swipe(
                screen_size['width'] // 2,
                start_y,
                screen_size['width'] // 2,
                end_y,
                1000
            )
            time.sleep(SCROLL_DELAY)

            # Chercher l'élément
            try:
                element = driver.find_element(By.XPATH, f"//*[@text='{text}']")
                bounds = element.get_attribute("bounds")
                if bounds:
                    return extract_bounds(bounds)
            except NoSuchElementException:
                continue

        logger.warning(f"Élément '{text}' non trouvé après {max_attempts} tentatives de scroll")
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de l'élément '{text}': {str(e)}")
        return None


@retry_on_failure()
def click_sur_bound(driver: webdriver.Remote, bounds: Tuple[int, int, int, int]) -> bool:
    """Clique sur un élément en utilisant ses coordonnées."""
    try:
        x_center = (bounds[0] + bounds[2]) // 2
        y_center = (bounds[1] + bounds[3]) // 2

        actions = ActionBuilder(driver)
        pointer = PointerInput(POINTER_TOUCH, "touch")
        actions.add_pointer_input("touch", pointer)
        actions.pointer_action.move_to_location(x_center, y_center)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pointer_up()
        actions.perform()

        logger.info(f"Clic effectué aux coordonnées ({x_center}, {y_center})")
        return True
    except Exception as e:
        logger.error(f"Erreur lors du clic sur les coordonnées {bounds}: {str(e)}")
        return False


@retry_on_failure()
def wait_for_element(driver: webdriver.Remote, by: str, value: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[
    WebElement]:
    """Attend qu'un élément soit présent et visible."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        if element.is_displayed():
            return element
        return None
    except TimeoutException:
        logger.warning(f"Timeout en attendant l'élément {by}={value}")
        return None
    except Exception as e:
        logger.error(f"Erreur en attendant l'élément {by}={value}: {str(e)}")
        return None


@retry_on_failure()
def get_element_text_safely(driver: webdriver.Remote, by: str, value: str) -> Optional[str]:
    """Récupère le texte d'un élément de manière sécurisée."""
    try:
        element = wait_for_element(driver, by, value)
        if element:
            return element.text.strip()
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du texte de {by}={value}: {str(e)}")
        return None


@retry_on_failure()
def is_element_visible(driver: webdriver.Remote, by: str, value: str) -> bool:
    """Vérifie si un élément est visible."""
    try:
        element = driver.find_element(by, value)
        return element.is_displayed()
    except NoSuchElementException:
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la visibilité de {by}={value}: {str(e)}")
        return False


@retry_on_failure()
def scroll_to_element(driver: webdriver.Remote, by: str, value: str, max_attempts: int = SCROLL_ATTEMPTS) -> bool:
    """Scroll jusqu'à ce qu'un élément soit visible."""
    try:
        screen_size = driver.get_window_size()
        start_y = screen_size['height'] * 0.8
        end_y = screen_size['height'] * 0.2

        for attempt in range(max_attempts):
            if is_element_visible(driver, by, value):
                return True

            driver.swipe(
                screen_size['width'] // 2,
                start_y,
                screen_size['width'] // 2,
                end_y,
                1000
            )
            time.sleep(SCROLL_DELAY)

        logger.warning(f"Élément {by}={value} non trouvé après {max_attempts} tentatives de scroll")
        return False
    except Exception as e:
        logger.error(f"Erreur lors du scroll vers l'élément {by}={value}: {str(e)}")
        return False


@retry_on_failure()
def verify_bluetooth_state(driver: webdriver.Remote, expected_state: bool) -> bool:
    """Vérifie l'état du Bluetooth et le compare avec l'état attendu."""
    try:
        # Vérifier via l'interface utilisateur
        ui_state = verfier_bluetooth_activer(driver, "com.android.car.settings:id/switch_widget")

        # Vérifier via ADB
        device = driver.capabilities['deviceName']
        adb_state = est_bluetooth_active(device)

        # Les deux états doivent correspondre et être égaux à l'état attendu
        if ui_state is not None and adb_state is not None:
            return ui_state == expected_state and adb_state == expected_state

        logger.warning("Impossible de vérifier l'état du Bluetooth de manière fiable")
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'état du Bluetooth: {str(e)}")
        return False


@retry_on_failure()
def verify_wifi_state(driver: webdriver.Remote, expected_state: bool) -> bool:
    """Vérifie l'état du Wi-Fi et le compare avec l'état attendu."""
    try:
        # Vérifier via l'interface utilisateur
        ui_state = is_active_wifi_ui(driver)

        # Vérifier via ADB
        adb_state = is_wifi_enabled_adb(driver)

        # Les deux états doivent correspondre et être égaux à l'état attendu
        if ui_state is not None and adb_state is not None:
            return ui_state == expected_state and adb_state == expected_state

        logger.warning("Impossible de vérifier l'état du Wi-Fi de manière fiable")
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'état du Wi-Fi: {str(e)}")
        return False


@retry_on_failure()
def verify_gps_state(driver: webdriver.Remote, expected_state: bool) -> bool:
    """Vérifie l'état du GPS et le compare avec l'état attendu."""
    try:
        # Vérifier via ADB
        adb_state = is_gps_enabled_adb(driver)

        if adb_state is not None:
            return adb_state == expected_state

        logger.warning("Impossible de vérifier l'état du GPS de manière fiable")
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'état du GPS: {str(e)}")
        return False


@retry_on_failure()
def verify_notification_state(driver: webdriver.Remote, expected_state: bool) -> bool:
    """Vérifie l'état des notifications et le compare avec l'état attendu."""
    try:
        # Vérifier via l'interface utilisateur
        notifications = afficher_notification(driver)

        # Si on attend des notifications actives, il doit y en avoir
        if expected_state:
            return len(notifications) > 0
        else:
            return len(notifications) == 0
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'état des notifications: {str(e)}")
        return False


@retry_on_failure()
def verify_application_state(driver: webdriver.Remote, package_name: str, expected_state: bool) -> bool:
    """Vérifie l'état d'une application et le compare avec l'état attendu."""
    try:
        # Vérifier si l'application est installée
        is_installed = is_app_installed(driver, package_name)

        if not is_installed:
            return not expected_state  # Si on attend que l'app ne soit pas installée

        # Vérifier si l'application est en cours d'exécution
        current_package = driver.current_package
        is_running = current_package == package_name

        return is_running == expected_state
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'état de l'application {package_name}: {str(e)}")
        return False


@retry_on_failure()
def verify_system_language(driver: webdriver.Remote, expected_language: str) -> bool:
    """Vérifie la langue du système et la compare avec la langue attendue."""
    try:
        # Récupérer la langue actuelle
        device = driver.capabilities['deviceName']
        current_language = get_system_language(device)

        return current_language == expected_language
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la langue du système: {str(e)}")
        return False


@retry_on_failure()
def verify_location_state(driver: webdriver.Remote, expected_state: bool) -> bool:
    """Vérifie l'état de la localisation et le compare avec l'état attendu."""
    try:
        # Vérifier via ADB
        device = driver.capabilities['deviceName']
        location_enabled = is_gps_enabled_adb(driver)

        if location_enabled is not None:
            return location_enabled == expected_state

        logger.warning("Impossible de vérifier l'état de la localisation de manière fiable")
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'état de la localisation: {str(e)}")
        return False


@retry_on_failure()
def record_audio(driver: webdriver.Remote, duration_sec, output_file: str = 'test.wav',
                 sample_rate: int = 44100) -> bool:
    """
    Enregistre l'audio du système via l'API Flask.

    Args:
        driver: Instance Appium WebDriver
        duration_sec: Durée de l'enregistrement en secondes (défaut: 10)
        output_file: Nom du fichier de sortie (défaut: 'emulator_audio.wav')
        sample_rate: Taux d'échantillonnage (défaut: 44100 Hz)

    Returns:
        bool: True si l'enregistrement a réussi, False sinon
    """
    try:
        payload = {
            "duration_sec": duration_sec,
            "output_file": output_file,
            "sample_rate": sample_rate
        }

        response = requests.post(url_host + "/record_audio", json=payload)

        if response.status_code == 200:
            logger.info(f"✅ Enregistrement audio réussi : {response.json()['message']}")
            return True
        else:
            logger.error(f"❌ Échec de l'enregistrement audio : {response.text}")
            return False

    except requests.RequestException as e:
        logger.error(f"❌ Erreur lors de la requête d'enregistrement audio : {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur inattendue lors de l'enregistrement audio : {str(e)}")
        return False


@retry_on_failure()
def play_audio(driver: webdriver.Remote, audio_file: str) -> bool:
    """
    Joue un fichier audio via l'API Flask.
    """
    try:
        # Get all possible paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(base_dir, audio_file),
            os.path.join(base_dir, "recordings", audio_file),
            os.path.join(os.getcwd(), "test_cases", audio_file),
            audio_file
        ]

        # Find the first valid path
        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break

        if not file_path:
            logger.error(f"❌ Fichier audio non trouvé. Recherché dans: {possible_paths}")
            return False

        payload = {
            "audio_file": os.path.basename(file_path),
            "full_path": file_path
        }

        response = requests.post(url_host + "/play_audio", json=payload, timeout=30)

        if response.status_code == 200:
            logger.info(f"✅ Lecture audio réussie : {response.json()['message']}")
            return True

        logger.error(f"❌ Échec de la lecture audio : {response.status_code} - {response.text}")
        return False

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erreur réseau lors de la lecture audio : {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur inattendue lors de la lecture audio : {str(e)}")
        return False


def click_element_by_xpath_bounds(driver, xpath):
    """
    Trouve un élément par XPath et clique dessus en utilisant ses bounds.

    :param driver: L'instance du WebDriver.
    :param xpath: Le XPath de l'élément à cliquer.
    :return: True si le clic a réussi, False sinon.
    """
    try:
        # Rechercher l'élément par XPath
        element = driver.find_element(By.XPATH, xpath)

        # Obtenir les bounds de l'élément
        bounds_str = element.get_attribute('bounds')
        if not bounds_str:
            print(f"Impossible de récupérer les bounds de l'élément: {xpath}")
            return False

        # Parser les bounds (format: "[x1,y1][x2,y2]")
        bounds = bounds_str.replace('][', ',').replace('[', '').replace(']', '').split(',')
        x1, y1, x2, y2 = map(int, bounds)

        # Calculer le centre de l'élément
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        # Cliquer au centre de l'élément
        driver.tap([(center_x, center_y)])
        return True

    except NoSuchElementException:
        print(f"Élément non trouvé: {xpath}")
        return False
    except Exception as e:
        print(f"Erreur lors du clic sur l'élément: {str(e)}")
        return False

import os


def get_audio_duration(driver: webdriver.Remote, audio_file: str) -> float:
    """
    Obtient la durée d'un fichier audio en secondes.
    """
    try:
        import soundfile as sf

        # Search in multiple possible locations
        base_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(base_dir, audio_file),
            os.path.join(base_dir, "recordings", audio_file),
            os.path.join(os.getcwd(), "test_cases", audio_file),
            audio_file
        ]

        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break

        if not file_path:
            logger.error(f"❌ Fichier audio non trouvé. Recherché dans: {possible_paths}")
            return 0.0

        info = sf.info(file_path)
        duration = info.duration
        logger.info(f"✅ Durée du fichier audio {file_path}: {duration:.2f} secondes")
        return duration

    except Exception as e:
        logger.error(f"❌ Erreur lors de la lecture de la durée du fichier audio : {str(e)}")
        return 0.0