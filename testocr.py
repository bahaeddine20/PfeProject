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



print(get_text_bounds("screenshot1.png","Son"))