from flask import Flask, jsonify
import subprocess

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
