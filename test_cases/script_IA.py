
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
    threshold = 0.97

    # Trouver la meilleure correspondance
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val >= threshold:
        x, y = max_loc
        return (x, y, w, h)
    else:
        return None


def click_icon_ia(driver, icon_name):
    icon_pos = find_icon_position(driver, icon_name)  # Sans l'extension .png
    print(icon_pos)
    if icon_pos:
        x, y, w, h = icon_pos
        # Cliquer au centre de l'icône
        driver.tap([(x + w // 2, y + h // 2)])
        return  True
    else:
        return False