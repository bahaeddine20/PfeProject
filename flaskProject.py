import os
import shutil

from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import threading
import time
import subprocess
import datetime
import re

app = Flask(__name__)

# Variables globales pour stocker les sélections
selected_automotive = None
selected_mobile = None
selected_tests = []

# Dossier contenant les fichiers `.robot`
TESTS_FOLDER = "test_cases"
RESULTS_FOLDER = "resultats"

# Progression des tests
progress_data = {
    "current_file": "En attente...",
    "percentage": 0,
    "total": 0,
    "completed": 0
}
stop_execution = False

def get_connected_devices():
    """Récupère la liste des appareils connectés via ADB"""
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")[1:]
    return [line.split()[0] for line in lines if len(line.split()) == 2 and line.split()[1] == "device"]

def get_device_type(device_id):
    """Détermine si un appareil est Mobile ou Automotive"""
    result = subprocess.run(["adb", "-s", device_id, "shell", "getprop", "ro.build.characteristics"],
                            capture_output=True, text=True)
    return "Automotive" if "automotive" in result.stdout.strip() else "Mobile"

@app.route('/')
def home():
    global selected_automotive, selected_mobile
    devices = get_connected_devices()
    automotive_devices = [d for d in devices if get_device_type(d) == "Automotive"]
    mobile_devices = [d for d in devices if get_device_type(d) == "Mobile"]
    return render_template('index.html',
                           automotive=automotive_devices,
                           mobile=mobile_devices,
                           selected_automotive=selected_automotive,
                           selected_mobile=selected_mobile)


import os


def remplacer_device(dossier, nouveau_device):
    for root, _, files in os.walk(dossier):
        for file in files:
            if file.endswith(".robot"):
                chemin_fichier = os.path.join(root, file)
                with open(chemin_fichier, "r", encoding="utf-8") as f:
                    contenu = f.readlines()

                nouveau_contenu = []
                modifié = False
                for ligne in contenu:
                    if "${Device}     " in ligne :
                        ligne = f"${{Device}}              {nouveau_device}\n"
                        modifié = True
                    nouveau_contenu.append(ligne)

                if modifié:
                    with open(chemin_fichier, "w", encoding="utf-8") as f:
                        f.writelines(nouveau_contenu)
                    print(f"[MODIFIÉ] {chemin_fichier}")


# Exemple d'utilisation :
# remplacer_device("chemin/vers/ton/dossier", "device123")


# Exemple d'utilisation :
# remplacer_device_dans_dossier("my_pixel_7")



from robot.parsing import get_model
@app.route('/save_selection', methods=['POST'])
def save_selection():
    global selected_automotive, selected_mobile
    selected_automotive = request.form.get('automotive_device')
    selected_mobile = request.form.get('mobile_device')

    # Appel de la fonction de remplacement dans les .robot
    remplacer_devices_robot_files(selected_automotive, selected_mobile)

    return redirect(url_for('select_tests'))

def remplacer_devices_robot_files(device_auto, device_mobile):
    dossier = os.path.join(os.getcwd(), "test_cases")  # Dossier contenant les fichiers .robot
    for fichier in os.listdir(dossier):
        if fichier.endswith(".robot"):
            chemin = os.path.join(dossier, fichier)
            with open(chemin, "r", encoding="utf-8") as f:
                lignes = f.readlines()

            nouveau_contenu = []
            modifié = False
            for ligne in lignes:
                if re.match(r"^\s*\${Device}\s+", ligne):
                    espace = re.search(r"(\s+)", ligne.strip()).group(1) if re.search(r"(\s+)", ligne.strip()) else "    "
                    ligne = f"${{Device}}{espace}{device_auto}\n"
                    modifié = True
                elif re.match(r"^\s*\${Device_mobile}\s+", ligne):
                    espace = re.search(r"(\s+)", ligne.strip()).group(1) if re.search(r"(\s+)", ligne.strip()) else "    "
                    ligne = f"${{Device_mobile}}{espace}{device_mobile}\n"
                    modifié = True
                nouveau_contenu.append(ligne)

            if modifié:
                with open(chemin, "w", encoding="utf-8") as f:
                    f.writelines(nouveau_contenu)
                print(f"[MODIFIÉ] {fichier}")
def get_tests_and_descriptions(file_path):
    """Extrait les tests et leurs descriptions d'un fichier .robot en utilisant robot.parsing."""
    try:
        model = get_model(file_path)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {file_path}: {e}")
        return "Aucune description trouvée.", []

    # Extraire la description du fichier
    file_description = "Aucune description trouvée."
    for section in model.sections:
        if section.__class__.__name__ == "SettingSection":
            for statement in section.body:
                if statement.__class__.__name__ == "Documentation":
                    file_description = statement.value.strip()
                    break

    # Extraire les cas de test et leurs descriptions
    tests_with_descriptions = []
    for section in model.sections:
        if section.__class__.__name__ == "TestCaseSection":
            for test_case in section.body:
                if test_case.__class__.__name__ == "TestCase":
                    test_name = test_case.name
                    test_description = "Aucune description."
                    for statement in test_case.body:
                        if statement.__class__.__name__ == "Documentation":
                            test_description = statement.value.strip()
                            break
                    tests_with_descriptions.append({"name": test_name, "description": test_description})

    if not tests_with_descriptions:
        print(f"Aucun test trouvé dans le fichier {file_path}.")

    print(file_description, tests_with_descriptions)
    return (file_description, tests_with_descriptions)

run = 0
lock = threading.Lock()

@app.route('/run_tests')
def run_tests():
    global run
    with lock:
        if run == 0:
            run = 1
            global stop_execution
            stop_execution = False
            threading.Thread(target=execute_tests).start()
            return render_template('progress.html', progress_data=progress_data)
        else:
            return "Les tests sont déjà en cours d'exécution", 409
@app.route('/select_tests', methods=['GET', 'POST'])
def select_tests():
    global selected_tests
    files = [f for f in os.listdir(TESTS_FOLDER) if f.endswith('.robot')]
    test_details = {file: get_tests_and_descriptions(os.path.join(TESTS_FOLDER, file)) for file in files}
    if request.method == 'POST':
        selected_tests = request.form.getlist('test_files')
        return redirect(url_for('run_tests'))
    return render_template('select_tests.html', files=files, selected_tests=selected_tests, test_details=test_details)
@app.route('/progress', methods=['GET'])
def get_progress():
    return jsonify(progress_data)

@app.route('/stop_tests', methods=['POST'])
def stop_tests():
    global stop_execution
    stop_execution = True
    return jsonify({"message": "Tests stoppés !"})


def execute_tests():
    global progress_data, stop_execution, run

    # Create application context
    with app.app_context():
        if not selected_tests:
            run = 0
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d (%H-%M)")
        results_dir = os.path.join(RESULTS_FOLDER, f"resultats_{timestamp}")
        os.makedirs(results_dir, exist_ok=True)
        total_tests = len(selected_tests)

        progress_data.update({"total": total_tests, "completed": 0})

        for i, test_file in enumerate(selected_tests):
            if stop_execution:
                progress_data.update({"current_file": "🛑 Exécution stoppée !", "percentage": 100})
                run = 0
                return

            test_result_dir = os.path.join(results_dir, os.path.splitext(test_file)[0])
            os.makedirs(test_result_dir, exist_ok=True)
            progress_data.update({"current_file": test_file, "percentage": int(i / total_tests * 100)})

            time.sleep(1)
            subprocess.run(["robot", "--outputdir", test_result_dir, os.path.join(TESTS_FOLDER, test_file)],
                           capture_output=True, text=True)

            progress_data.update({"completed": i + 1, "percentage": int((i + 1) / total_tests * 100)})
            time.sleep(1)
        run = 0
        progress_data.update({
            "current_file": "✅ Tous les tests sont terminés !",
            "percentage": 100,
            "download_link": url_for('download_results')
        })

        shutil.make_archive(results_dir, 'zip', results_dir)
        run = 0
@app.route('/download_results')
def download_results():
    latest_results = sorted(os.listdir(RESULTS_FOLDER), reverse=True)
    if not latest_results:
        return "Aucun résultat disponible", 404
    latest_folder = os.path.join(RESULTS_FOLDER, latest_results[0])

    zip_filename = f"{latest_results[0]}.zip"
    zip_filepath = os.path.join(RESULTS_FOLDER, zip_filename)

    # Créer un fichier ZIP du dossier de résultats
    shutil.make_archive(zip_filepath.replace('.zip', ''), 'zip', latest_folder)

    return send_file(zip_filepath, as_attachment=True)



app.run(host='0.0.0.0', port=5000)
if __name__ == '__main__':
    app.run(debug=True)
