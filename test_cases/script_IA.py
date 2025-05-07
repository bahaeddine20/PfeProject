import cv2
import numpy as np
import os

from io import BytesIO


def find_icon_position(driver, icon_name):
    """
    Trouve la position d'une icône sur l'écran du device Android.

    Args:
        driver: Instance du driver Appium
        icon_name: Nom du fichier de l'icône à trouver (doit être dans le dossier 'icons')

    Returns:
        Tuple (x, y, width, height) de la position de l'icône ou None si non trouvée
    """
    # Obtenir le chemin absolu du dossier iconshd
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(os.path.dirname(current_dir), 'iconshd')

    # Chemin vers l'icône template (uniquement PNG)
    template_path = os.path.join(icons_dir, f'{icon_name}.png')

    # Créer le dossier s'il n'existe pas
    os.makedirs(icons_dir, exist_ok=True)

    if not os.path.exists(template_path):
        raise FileNotFoundError(
            f"Le fichier d'icône {template_path} n'existe pas. Veuillez ajouter l'icône PNG dans le dossier 'iconshd/'")

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
    threshold = 0.94  # Seuil de tolérance

    # Trouver la meilleure correspondance
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val >= threshold:
        x, y = max_loc
        return (x, y, w, h)
    else:
        return None


from appium.options.android import UiAutomator2Options

from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.interaction import POINTER_TOUCH


def click_icon_ia(driver, icon_name):
    """
    Clique sur une icône trouvée sur l'écran.

    Args:
        driver: Instance du driver Appium
        icon_name: Nom de l'icône à cliquer (sans l'extension .png)

    Returns:
        bool: True si le clic a réussi, False sinon
    """
    try:
        icon_pos = find_icon_position(driver, icon_name)
        if icon_pos:
            x, y, w, h = icon_pos
            # Cliquer au centre de l'icône
            driver.tap([(x + w // 2, y + h // 2)])
            return True
        else:
            print(f"Icône '{icon_name}.png' non trouvée sur l'écran")
            return False
    except FileNotFoundError as e:
        print(f"Erreur: {str(e)}")
        return False
    except Exception as e:
        print(f"Erreur lors du clic sur l'icône '{icon_name}.png': {str(e)}")
        return False


import io
from PIL import Image
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

# Charger le modèle OCR une seule fois
ocr_model = ocr_predictor(pretrained=True)


def get_text_bounds(image_input, text_to_find):
    """
    Extrait les coordonnées (xmin, ymin, xmax, ymax) du texte trouvé dans une image.

    :param image_input: Chemin vers l'image (str) ou image en bytes
    :param text_to_find: Mot ou texte à chercher
    :return: Tuple (xmin, ymin, xmax, ymax) ou None si non trouvé
    """
    import unicodedata

    def normalize_text(text):
        # Normaliser le texte en supprimant les accents
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
        return text.lower()

    # Charger l'image et créer l'objet Doctr
    if isinstance(image_input, str):  # chemin de fichier
        image = Image.open(image_input)
        # Convert to bytes to handle both cases the same way
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
    elif isinstance(image_input, (bytes, bytearray)):  # image PNG depuis Selenium
        img_byte_arr = image_input
        image = Image.open(io.BytesIO(img_byte_arr))
    else:
        raise TypeError("image_input must be a file path or PNG bytes")

    width, height = image.size

    # Create DocumentFile from bytes (note: from_images expects a list)
    doc = DocumentFile.from_images([img_byte_arr])

    # OCR avec Doctr
    result = ocr_model(doc)

    # Normaliser le texte recherché
    normalized_search = normalize_text(text_to_find)

    # Analyse du résultat
    blocks = result.pages[0].blocks  # On suppose une seule page

    for block in blocks:
        for line in block.lines:
            for word in line.words:
                # Normaliser le texte détecté
                normalized_word = normalize_text(word.value)
                if normalized_search in normalized_word:
                    (xmin_norm, ymin_norm), (xmax_norm, ymax_norm) = word.geometry

                    xmin = int(xmin_norm * width)
                    ymin = int(ymin_norm * height)
                    xmax = int(xmax_norm * width)
                    ymax = int(ymax_norm * height)

                    return (xmin, ymin, xmax, ymax)

    return None


def get_text_bounds_driver(driver, text_to_find):
    """
    Capture une capture d'écran du navigateur et extrait les coordonnées du texte.

    :param driver: Instance de Selenium WebDriver
    :param text_to_find: Texte à rechercher dans l'image
    :return: Tuple (xmin, ymin, xmax, ymax) ou None si non trouvé
    """
    screenshot_bytes = driver.get_screenshot_as_png()
    return get_text_bounds(screenshot_bytes, text_to_find)

