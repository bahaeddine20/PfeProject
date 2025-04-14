import requests
import time
from datetime import datetime
import xml.etree.ElementTree as ET

# Clé API de ThingSpeak
api_key = "117NMJWEH4716Q7X"


# Fonction pour lire les points GPS d'un fichier GPX
def read_gpx(file):
    tree = ET.parse(file)
    root = tree.getroot()

    # Extraire les points (latitude, longitude) du fichier GPX
    ns = {'default': 'http://www.topografix.com/GPX/1/1'}
    points = []
    for trkpt in root.findall('.//default:trkpt', ns):
        lat = float(trkpt.attrib['lat'])
        lon = float(trkpt.attrib['lon'])
        points.append((lat, lon))
    return points


# Fonction pour envoyer les données à ThingSpeak
def send_to_thingspeak(route):
    for i in range(len(route)):
        lat, lon = route[i]

        # Obtenir la date actuelle au format voulu
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Construire l'URL pour envoyer les données à ThingSpeak
        url = f"https://api.thingspeak.com/update?api_key={api_key}&field1=1&field2={lat}&field3={lon}&field4={current_time}"

        # Envoyer la requête GET
        response = requests.get(url)

        # Afficher la réponse pour vérifier
        print(f"Envoyé à ThingSpeak: {current_time} - Lat: {lat}, Lon: {lon}")

        # Attendre une seconde avant d'envoyer de nouvelles données
        time.sleep(5)


# Lire le fichier GPX
route = read_gpx("C:/Users/bahae/Desktop/PfeProject/run.gpx")

# Démarrer l'envoi de données à ThingSpeak
send_to_thingspeak(route)
