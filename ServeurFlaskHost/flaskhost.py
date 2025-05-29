from flask import Flask, jsonify, request
import subprocess
import sounddevice as sd
import soundfile as sf
from scipy.io.wavfile import write
import os
import threading

app = Flask(__name__)

# Route pour exécuter la commande ADB
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/call', methods=['POST'])
def simulate_incoming_call():
    """
    Simule un appel entrant sur un émulateur Android via ADB et vérifie si la commande a réussi.

    Reçoit un JSON contenant :
      - device_name : nom de l'appareil (string)
      - phone_number : numéro de téléphone à simuler (string)

    :return: JSON { "success": true/false, "message": "..." }
    """
    data = request.get_json()

    device_name = data.get('device_name')
    phone_number = data.get('phone_number')

    if not device_name or not phone_number:
        return jsonify({"success": False, "message": "Paramètres 'device_name' et 'phone_number' requis."}), 400

    command = ["adb", "-s", device_name, "emu", "gsm", "call", phone_number]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        if "OK" in output:
            print(f"[OK] Appel simulé depuis {phone_number} vers {device_name}.")
            return jsonify({"success": True, "message": f"Appel simulé vers {phone_number}."}), 200
        else:
            print(f"[ERREUR] Réponse inattendue : {output}")
            return jsonify({"success": False, "message": f"Réponse inattendue : {output}"}), 500
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Échec de la simulation d'appel : {e.stderr.strip()}")
        return jsonify({"success": False, "message": f"Erreur ADB : {e.stderr.strip()}"}), 500

@app.route('/setlocation', methods=['POST'])
def set_location():
    data = request.get_json()

    device_id = data.get('device_id')
    longitude = data.get('longitude')
    latitude = data.get('latitude')
    
    if not device_id or longitude is None or latitude is None:
        return jsonify({"success": False, "message": "Champs manquants."}), 400

    adb_command = ["adb", "-s", device_id, "emu", "geo", "fix", str(longitude), str(latitude)]

    try:
        result = subprocess.run(adb_command, capture_output=True, text=True, check=True)
        return jsonify({"success": True, "message": f"Position définie : {longitude}, {latitude}"}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "message": f"Erreur ADB : {e.stderr.strip()}"}), 500

def record_audio_thread(duration_sec, file_path, sample_rate):
    try:
        # Enregistrement de l'audio
        recording = sd.rec(
            int(duration_sec * sample_rate),
            samplerate=sample_rate,
            channels=2,
            device=None  # Utilise le périphérique par défaut
        )
        sd.wait()
        
        # Sauvegarde le fichier
        write(file_path, sample_rate, recording)
        print(f"Recording saved to {file_path}")
    except Exception as e:
        print(f"Error in recording thread: {str(e)}")

@app.route('/record_audio', methods=['POST'])
def record_audio():
    """
    Enregistre l'audio du système pour une durée spécifiée.
    """
    print("Received request for /record_audio")
    print("Request headers:", request.headers)
    print("Request data:", request.get_data())
    
    try:
        data = request.get_json()
        print("Parsed JSON data:", data)
    except Exception as e:
        print("Error parsing JSON:", str(e))
        return jsonify({
            "success": False,
            "message": f"Erreur de parsing JSON: {str(e)}"
        }), 400
    
    if data is None:
        data = {}
    
    # Paramètres avec valeurs par défaut
    try:
        duration_sec = int(data.get('duration_sec', 10))
        output_file = str(data.get('output_file', 'emulator_audio.wav'))
        sample_rate = int(data.get('sample_rate', 44100))
    except (ValueError, TypeError) as e:
        print("Error converting parameters:", str(e))
        return jsonify({
            "success": False,
            "message": f"Erreur de conversion des paramètres: {str(e)}"
        }), 400
    
    try:
        # Crée le dossier recordings s'il n'existe pas
        os.makedirs('recordings', exist_ok=True)
        file_path = os.path.join('recordings', output_file)
        
        # Vérifie les périphériques disponibles
        devices = sd.query_devices()
        print("\nAvailable devices:")
        print(devices)
        
        # Démarre l'enregistrement dans un thread séparé
        recording_thread = threading.Thread(
            target=record_audio_thread,
            args=(duration_sec, file_path, sample_rate)
        )
        recording_thread.start()
        
        # Répond immédiatement
        return jsonify({
            "success": True,
            "message": "Enregistrement audio démarré",
            "file_path": file_path,
            "duration": duration_sec,
            "sample_rate": sample_rate,
            "available_devices": str(devices)
        }), 200
        
    except Exception as e:
        print("Error during recording setup:", str(e))
        return jsonify({
            "success": False,
            "message": f"Erreur lors de la configuration de l'enregistrement audio: {str(e)}"
        }), 500


@app.route('/play_audio', methods=['POST'])
def play_audio():
    """
    Joue un fichier audio depuis le dossier recordings ou le chemin spécifié.
    """
    try:
        data = request.get_json()
        if not data or 'audio_file' not in data:
            return jsonify({
                "success": False,
                "message": "Le paramètre 'audio_file' est obligatoire"
            }), 400

        # Try both the filename and full path if provided
        audio_file = data['audio_file']
        full_path = data.get('full_path', '')

        possible_paths = [
            os.path.join('recordings', audio_file),
            os.path.join(os.getcwd(), 'test_cases', audio_file),
            full_path,
            audio_file
        ]

        file_path = None
        for path in possible_paths:
            if path and os.path.exists(path):
                file_path = path
                break

        if not file_path:
            return jsonify({
                "success": False,
                "message": f"Fichier audio non trouvé. Recherché dans: {possible_paths}",
                "searched_paths": possible_paths
            }), 404

        # Read and play audio
        data, samplerate = sf.read(file_path)
        sd.play(data, samplerate)
        sd.wait()

        return jsonify({
            "success": True,
            "message": f"Lecture du fichier {os.path.basename(file_path)} terminée",
            "file_path": file_path,
            "duration": len(data) / samplerate
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de la lecture audio: {str(e)}"
        }), 500


# Créer un dossier pour stocker les fichiers audio
UPLOAD_FOLDER = 'received_audio'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

from datetime import datetime

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return {'error': 'Aucun fichier audio trouvé'}, 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return {'error': 'Aucun fichier sélectionné'}, 400

    # Générer un nom de fichier unique avec timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'audio_{timestamp}.wav'
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Sauvegarder le fichier
    audio_file.save(filepath)

    return {'message': 'Audio  reçu avec succès', 'filename': filename}, 200

from glob import glob

from flask import  send_file, abort

@app.route('/latest-audio', methods=['GET'])
def get_latest_audio():
    folder_path = 'received_audio'  # Pour le test d'enregistrement qui reçoit l'audio ici
    # Cherche tous les fichiers .wav dans le dossier
    wav_files = glob(os.path.join(folder_path, '*.wav'))

    if not wav_files:
        return abort(404, description="Aucun fichier .wav trouvé.")

    # Trouve le fichier le plus récent
    latest_file = max(wav_files, key=os.path.getctime)
    return send_file(latest_file, mimetype='audio/wav')

@app.route('/latest-audio-record-play', methods=['GET'])
def get_latest_audio_record_play():
    folder_path = 'recordings'  # Pour le test de lecture qui enregistre l'audio ici
    # Cherche tous les fichiers .wav dans le dossier
    wav_files = glob(os.path.join(folder_path, '*.wav'))

    if not wav_files:
        return abort(404, description="Aucun fichier .wav trouvé.")

    # Trouve le fichier le plus récent
    latest_file = max(wav_files, key=os.path.getctime)
    return send_file(latest_file, mimetype='audio/wav')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
