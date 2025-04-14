
from appium.options.android import UiAutomator2Options

from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.interaction import POINTER_TOUCH

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from appium import webdriver

from datetime import datetime
import time

import random

import re

apps_page="com.android.car.carlauncher/.GASAppGridActivity"
def setup_driver(device):
    """Initialise et retourne le driver Appium."""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = "14"
    options.device_name = device
    options.adb_exec_timeout = 60000
    options.remote_adb_host="host.docker.internal"
    options.disable_window_animation=True
    options.new_command_timeout=300
    options.allowInvisibleElements=True
    options.disableIdLocatorAutocompletion=True
    #remote_url = "http://127.0.0.1:4723"
    #remote_url = "http://172.21.0.3:4723"
    remote_url = "http://appium:4723"

    options.set_capability("enforceXPath1", True)
    return webdriver.Remote(remote_url, options=options)

def start_activity_code(driver, app_activity):
    """Lance une activité spécifique sur un appareil Android via Appium."""
    driver.execute_script('mobile: startActivity', {'intent': app_activity})

def is_activity_active(driver, expected_activity):
    """Vérifie si l'activité actuelle correspond à l'activité spécifiée."""
    current_activity = driver.current_activity
    print(current_activity)
    return current_activity in  expected_activity

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
        driver.swipe(250, 400, 250, 600)  # Le swipe vers le haut
        time.sleep(1)  # Attendre 1 seconde entre les swipes pour permettre à l'élément d'apparaître

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


cor_all_apps_x=640
cor_all_apps_y=745
def revenir_a_la_home_page(driver):
    click_sur(driver,cor_all_apps_x,cor_all_apps_y)
    driver.press_keycode(3)  # KEYCODE_HOME

    click_sur(driver,cor_all_apps_x,cor_all_apps_y)

    first = afficher_noms_applications(driver)  # Capturer les apps de la home page
    print("📌 First Home Page détectée :", first)

    while True:
        driver.swipe(200, 500, 900, 500)  # Swipe vers la droite (modifie si nécessaire)
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




def click_element_by_text_att(driver, text):
    element = driver.find_element(By.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')
    element.click()
# Exemple d'utilisation


def is_within_bounds(child_bounds, parent_bounds):
    if not child_bounds or not parent_bounds:
        return False  # Évite les erreurs si l'un des bounds est None

    x1_c, y1_c, x2_c, y2_c = child_bounds
    x1_p, y1_p, x2_p, y2_p = parent_bounds

    return (x1_p <= x1_c <= x2_p and y1_p <= y1_c <= y2_p) or (x1_p <= x2_c <= x2_p and y1_p <= y2_c <= y2_p)

def afficher_noms_setting_bound(driver, xpath_id):
    noms_settings = []  # Liste pour stocker les noms des settings
    parent_bounds = get_element_bounds_byId(driver, xpath_id)

    print(parent_bounds)
    print("###################################")
    print(parent_bounds)

    if parent_bounds == (0, 0, 0, 0):
        print(f"Aucun élément trouvé avec le texte: {xpath_id}")
        return noms_settings  # Retourne une liste vide

    elements = driver.find_elements("xpath", "//*")  # Récupérer tous les éléments
    for element in elements:
        try:
            classe = element.get_attribute("class")
            text = element.text
            resource_id = element.get_attribute("resource-id")
            bounds = element.get_attribute("bounds")

            if bounds:
                child_bounds = extract_bounds(bounds)
                if child_bounds and is_within_bounds(child_bounds, parent_bounds):
                    if classe == "android.widget.TextView" and resource_id == "android:id/title":
                        noms_settings.append(text)  # Ajouter le nom si dans la zone
        except Exception as e:
            print(f"Erreur lors de la récupération d'un élément : {str(e)}")

    print("\n📌 Liste des settings détectés dans la zone :", noms_settings)
    return noms_settings  # Retourne la liste des settings trouvés
def revenir_a_la_setting_haut(driver):
    first = afficher_noms_setting(driver)
    print("📌 First Home Page détectée :", first)

    while True:
        driver.swipe(300, 400, 300, 750)
        seconde = afficher_noms_setting(driver)

        if first == seconde:
            print("✅ Retour à la first home page !")
            break
        else:
            first = seconde
        print("🔄 Swipe en cours...")





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

def afficher_notification(driver):
    # Créer un objet ActionBuilder
    actions = ActionBuilder(driver)

    # Créer un pointeur de type "touch"
    pointer = PointerInput(POINTER_TOUCH, "touch")  # Utiliser "touch" comme type de pointeur

    # Ajouter le pointeur à l'ActionBuilder
    actions.add_pointer_input("touch", pointer)  # Ajouter un nom pour le pointeur

    # Définir les actions (déplacement, appui, relâchement)
    actions.pointer_action.move_to_location(500, 25)  # Déplacer le pointeur à (x, y)
    actions.pointer_action.pointer_down()  # Appuyer
    actions.pointer_action.move_to_location(500, 200)  # Déplacer le pointeur à (x, y)

    actions.pointer_action.pointer_up()  # Relâcher

    # Exécuter les actions
    actions.perform()
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
        time.sleep(2)  # Attendre que l'élément soit visible

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




def open_application_with_click(driver,text):
    revenir_a_la_home_page(driver)
    print("111111111111111111111")
    page=True
    while page:
        print("2222222222222222")
        first = afficher_noms_applications(driver)  # Vérifier les apps après swipe
        if text in first:
            if get_element_bounds(driver, text) is not None:
                print("3333333333333333333")
                bounds=get_element_bounds(driver, text)
                x1, y1, x2, y2 = extract_bounds(bounds)
                print(x1, y1, x2, y2)
                x_center = (x1 + x2) // 2
                y_center = (y1 + y2) // 2
                click_sur(driver, x_center, y_center)
                page =False
                return True
        else:
            driver.swipe(1200, 500, 500, 500)  # Swipe vers la droite (modifie si nécessaire)
            print("444444444444444444444'")
            seconde = afficher_noms_applications(driver)  # Vérifier les apps après swipe

            if first == seconde:
                print("55555555555555555")
                print("✅ Retour à la first home page !")
                return  False # Sortir de la boucle une fois la home page atteinte
            else:
                print("6666666666666666666")
                first = seconde
            print("🔄 Swipe en cours...")



def search_application(driver,text):
    revenir_a_la_home_page(driver)
    click_sur(driver,cor_all_apps_x,cor_all_apps_y)
    click_sur(driver,cor_all_apps_x,cor_all_apps_y)

    print("111111111111111111111")
    page=True
    while page:
        print("2222222222222222")
        first = afficher_noms_applications(driver)  # Vérifier les apps après swipe
        if text in first:
            if get_element_bounds(driver, text) is not None:
                print("3333333333333333333")
                bounds=get_element_bounds(driver, text)
                x1, y1, x2, y2 = extract_bounds(bounds)
                print(x1, y1, x2, y2)
                x_center = (x1 + x2) // 2
                y_center = (y1 + y2) // 2
                page =False
                return True
        else:
            driver.swipe(1200, 500, 500, 500)  # Swipe vers la droite (modifie si nécessaire)
            print("444444444444444444444'")
            seconde = afficher_noms_applications(driver)  # Vérifier les apps après swipe

            if first == seconde:
                print("55555555555555555")
                print("✅ Retour à la first home page !")
                return  False # Sortir de la boucle une fois la home page atteinte
            else:
                print("6666666666666666666")
                first = seconde
            print("🔄 Swipe en cours...")




def all_setting_list(driver,xpathid):
    setting = []
    revenir_a_la_setting_haut(driver)
    first = afficher_noms_setting_bound(driver,xpathid)
    setting=setting+first
    print("📌 First Home Page détectée :", first)

    while True:
        driver.swipe(300, 500, 300, 220)
        seconde = afficher_noms_setting_bound(driver,xpathid)
        setting=setting+seconde

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
    result = []   # Liste pour stocker les éléments uniques

    for item in input_list:
        if item not in seen:
            result.append(item)  # Ajouter l'élément si non vu
            seen.add(item)        # Ajouter à l'ensemble des éléments vus

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

        driver.swipe(x_middle, y_start, x_middle, y_end)
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


def clique_sur_setting(driver, nom, xpathid):
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
        # Vérifier si le nom recherché est dans les éléments actuels
        if nom in seconde:
            print(f" {nom} trouvé ! Appui sur le nom.")
            # Si le nom est trouvé, clique sur l'élément correspondant
            element = driver.find_element("xpath", f"//*[contains(@text, '{nom}')]")
            return element.click()  # Clique sur l'élément trouvé

        driver.swipe(x_middle, y_start, x_middle, y_end)
        print(" Swipe effectué...")
        seconde = afficher_noms_setting_bound(driver, xpathid)
        setting = setting + seconde

        # Si la page a recommencé à afficher les mêmes éléments (retour à la première page)
        if first == seconde:
            print(" Retour à la first home page !")
            return remove_duplicates(setting) # Si on est revenu à la première page, on arrête le swipe

        first = seconde  # Mettre à jour 'first' pour la prochaine itération

    # Retourner la liste sans doublons après avoir arrêté de swiper
    return remove_duplicates(setting)

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
            return  True
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



def check_language_change(device, reference_language):
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


def is_app_installed(driver, package_name):
    """
    Vérifie si une application est installée sur l'appareil via ADB.
    """
    device_id = driver.capabilities.get("deviceName")
    if not device_id:
        raise ValueError("Impossible de récupérer l'ID du device depuis le driver.")

    result = subprocess.run(["adb", "-s", device_id, "shell", "pm", "list", "packages", package_name],
                            capture_output=True, text=True)

    return package_name in result.stdout


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


def change_date(driver,date):
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
    match = re.search(r"\b(\d{2}):(\d{2})\b", date)
    if match:
        h = match.group(1)  # Heures
        m = match.group(2)  # Minutes
        print("eeeeeeeeee:", h)
        print("cccccccccccc:", m)

    while (h!=hour) :

        if h > hour :
            swipe_up(driver, buttons[0]['bounds'])

        elif h < hour :
            swipe_down(driver,buttons[0]['bounds'])



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
        match = re.search(r"\b(\d{2}):(\d{2})\b", date)
        if match:
            h = match.group(1)  # Heures
            m = match.group(2)  # Minutes
            print("eeeeeeeeee:", h)
            print("cccccccccccc:", m)
    while (m!=minute) :

        if m > minute :
            swipe_up(driver, buttons[1]['bounds'])

        elif m < minute :
            swipe_down(driver,buttons[1]['bounds'])



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
        match = re.search(r"\b(\d{2}):(\d{2})\b", date)
        if match:
            h = match.group(1)  # Heures
            m = match.group(2)  # Minutes
            print("eeeeeeeeee:", h)
            print("cccccccccccc:", m)

    return f"{hour}:{minute}"




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
    Définit une nouvelle position GPS sur l'émulateur ou l'appareil.

    :param device_id: L'ID du device Appium ou l'ID du périphérique.
    :param x: La longitude à définir (en degrés).
    :param y: La latitude à définir (en degrés).
    :return: True si la commande a réussi, False sinon.
    """
    # Construire la commande ADB pour définir la localisation
    adb_command = ["adb", "-s", device_id, "emu", "geo", "fix", str(x), str(y)]

    # Exécuter la commande
    result = subprocess.run(adb_command, capture_output=True, text=True)

    # Vérifier si la commande a réussi
    if result.returncode == 0:
        print(f"Position définie à Longitude: {x}, Latitude: {y}")
        return True
    else:
        print(f"Erreur lors de la définition de la position : {result.stderr}")
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