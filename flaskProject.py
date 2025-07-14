import os
import shutil

from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import threading
import time
import subprocess
import datetime
import matplotlib.pyplot as plt
import re
from collections import defaultdict

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
current_process = None

execution_logs = []

rf_live_log = []

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
    
    # Récupérer l'historique des tests
    test_history = []
    if os.path.exists(RESULTS_FOLDER):
        print(f"Scanning results folder: {RESULTS_FOLDER}")
        for folder in sorted(os.listdir(RESULTS_FOLDER), reverse=True):
            if folder.endswith('.zip'):
                continue
            folder_path = os.path.join(RESULTS_FOLDER, folder)
            if os.path.isdir(folder_path):
                print(f"Found test folder: {folder}")
                # Vérifier si le dossier contient un rapport final
                final_report = os.path.join(folder_path, "final_report")
                if os.path.exists(final_report):
                    report_path = os.path.join(final_report, "report.html")
                    if os.path.exists(report_path):
                        print(f"Found report.html in: {folder}")
                        # Extraire la date du nom du dossier
                        date_str = folder.replace('Tests_', '')
                        try:
                            timestamp = datetime.datetime.strptime(date_str.split('_')[0] + '_' + date_str.split('_')[1], '%Y-%m-%d_%H-%M')
                        except:
                            timestamp = datetime.datetime.now()
                        
                        test_history.append({
                            'name': folder,
                            'date': folder.replace('Tests_', ''),
                            'timestamp': timestamp.isoformat(),
                            'path': folder_path,
                            'has_report': True
                        })
    
    print(f"Total test history entries found: {len(test_history)}")
    
    return render_template('index.html',
                           automotive=automotive_devices,
                           mobile=mobile_devices,
                           selected_automotive=selected_automotive,
                           selected_mobile=selected_mobile,
                           test_history=test_history)

@app.route('/view_report/<path:folder_name>')
def view_report(folder_name):
    folder_path = os.path.join(RESULTS_FOLDER, folder_name)
    final_report_dir = os.path.join(folder_path, "final_report")
    
    # Try report.html first, then fall back to log.html
    for report_file in ["report.html", "log.html"]:
        report_path = os.path.join(final_report_dir, report_file)
        if os.path.exists(report_path):
            return send_file(report_path)
    
    # If neither file exists, return a more descriptive error
    return f"Rapport non trouvé dans {final_report_dir}. Vérifiez que le dossier existe et contient report.html ou log.html", 404

@app.route('/download_report/<path:folder_name>')
def download_report(folder_name):
    folder_path = os.path.join(RESULTS_FOLDER, folder_name)
    zip_path = os.path.join(RESULTS_FOLDER, f"{folder_name}.zip")
    
    # Créer le zip si nécessaire
    if not os.path.exists(zip_path):
        shutil.make_archive(folder_path, 'zip', folder_path)
    
    return send_file(zip_path, as_attachment=True)

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
    global stop_execution, run, current_process
    stop_execution = True
    run = 0
    if current_process is not None:
        try:
            current_process.terminate()
        except Exception:
            pass
        current_process = None
    return jsonify({"message": "Tests stoppés !"})


from collections import defaultdict

def extract_data(file_path):
    """Extract test names and average values from log files"""
    raw_data = defaultdict(list)

    with open(file_path, 'r') as f:
        for line in f:
            match = re.match(r'(.*?):(\d+\.?\d*)', line)
            if match:
                test_name = match.group(1).strip()
                value = float(match.group(2))
                raw_data[test_name].append(value)

    # Calculer la moyenne par test
    averaged_data = {name: sum(vals)/len(vals) for name, vals in raw_data.items()}
    print(f"Extracted data: {averaged_data}")
    return averaged_data


def create_bar_chart(data, title, ylabel, output_file):
    """Create and save bar chart"""
    if not data:
        print(f"No data to plot for {title}")
        return

    plt.figure(figsize=(10, 6))
    plt.bar(data.keys(), data.values(), color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    plt.title(title, fontsize=14)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks(rotation=15, ha='right', fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Add values on top of bars
    for i, value in enumerate(data.values()):
        plt.text(i, value + max(data.values()) * 0.02, f'{value:.2f}',
                 ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def execute_tests():
    global progress_data, stop_execution, run, current_process, rf_live_log
    rf_live_log = []
    with app.app_context():
        if not selected_tests:
            run = 0
            return
        # Créer un nom de dossier plus descriptif
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        test_names = "_".join([os.path.splitext(f)[0] for f in selected_tests])
        results_dir = os.path.join(RESULTS_FOLDER, f"Tests_{timestamp}_{test_names}")
        os.makedirs(results_dir, exist_ok=True)

        # Définir la variable d'environnement pour le dossier de sortie Flask
        os.environ['FLASK_OUTPUT_DIR'] = results_dir

        total_tests = len(selected_tests)
        progress_data.update({"total": total_tests, "completed": 0})
        output_files = []  # Liste des fichiers output.xml à fusionner
        for i, test_file in enumerate(selected_tests):
            if stop_execution:
                progress_data.update({"current_file": "🛑 Exécution stoppée !", "percentage": 100})
                run = 0
                return
            test_name = os.path.splitext(test_file)[0]
            test_result_dir = os.path.join(results_dir, test_name)
            os.makedirs(test_result_dir, exist_ok=True)
            progress_data.update({"current_file": test_file, "percentage": int(i / total_tests * 100)})
            time.sleep(1)
            current_process = subprocess.Popen(
                ["robot", "--outputdir", test_result_dir, os.path.join(TESTS_FOLDER, test_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            add_rf_log(f"================= {test_file} =================")
            for line in current_process.stdout:
                add_rf_log(line.rstrip())
            current_process.wait()
            # Ajouter le chemin vers output.xml à la liste
            output_file = os.path.join(test_result_dir, "output.xml")
            if os.path.exists(output_file):
                output_files.append(output_file)
            log_step(f"--- Exécution du test : {test_file} ---")
            log_step(f"Code de retour : {current_process.returncode}")
            log_step("----------------------------------------")
            progress_data.update({"completed": i + 1, "percentage": int((i + 1) / total_tests * 100)})
            time.sleep(1)

        # Création du dossier resumer + fusion des résultats avec rebot
        resumer_dir = os.path.join(results_dir, "final_report")
        os.makedirs(resumer_dir, exist_ok=True)
        if output_files:
            subprocess.run(
                ["rebot", "--outputdir", resumer_dir] + output_files,
                capture_output=True,
                text=True
            )

        # Générer les graphiques
        try:
            # Chemin des fichiers de logs (créés dans le répertoire racine)
            cpu_log = os.path.join(os.getcwd(), "cpu_usage.log")
            mem_log = os.path.join(os.getcwd(), "mem_usage.log")

            # Vérifier si les fichiers existent
            if os.path.exists(cpu_log):
                cpu_data = extract_data(cpu_log)
                create_bar_chart(cpu_data,
                                 'CPU Usage by Test',
                                 'CPU Usage (%)',
                                 os.path.join(resumer_dir, 'cpu_usage_chart.png'))
                print(f"CPU chart generated: {os.path.join(resumer_dir, 'cpu_usage_chart.png')}")

            if os.path.exists(mem_log):
                mem_data = extract_data(mem_log)
                create_bar_chart(mem_data,
                                 'Memory Usage by Test',
                                 'Memory Usage (MB)',
                                 os.path.join(resumer_dir, 'mem_usage_chart.png'))
                print(f"Memory chart generated: {os.path.join(resumer_dir, 'mem_usage_chart.png')}")

            print("Charts generated in final_report directory")
        except Exception as e:
            print(f"Error generating charts: {str(e)}")
            import traceback
            traceback.print_exc()

        # Créer l'archive
        shutil.make_archive(results_dir, 'zip', results_dir)

        run = 0
        progress_data.update({
            "current_file": "✅ Tous les tests sont terminés !",
            "percentage": 100
        })
        run = 0
        current_process = None
@app.route('/download_results')
def download_results():
    latest_results = sorted(os.listdir(RESULTS_FOLDER), reverse=True)
    if not latest_results:
        return "Aucun résultat disponible", 404
    
    # Trouver le dernier dossier de résultats (pas un fichier zip)
    latest_folder = None
    for result in latest_results:
        if not result.endswith('.zip'):
            latest_folder = os.path.join(RESULTS_FOLDER, result)
            break
    
    if not latest_folder:
        return "Aucun résultat disponible", 404

    zip_filename = f"{os.path.basename(latest_folder)}.zip"
    zip_filepath = os.path.join(RESULTS_FOLDER, zip_filename)

    # Créer un fichier ZIP du dossier de résultats
    shutil.make_archive(zip_filepath.replace('.zip', ''), 'zip', latest_folder)

    return send_file(zip_filepath, as_attachment=True)

@app.route('/delete_test/<path:folder_name>', methods=['DELETE'])
def delete_test(folder_name):
    try:
        folder_path = os.path.join(RESULTS_FOLDER, folder_name)
        zip_path = os.path.join(RESULTS_FOLDER, f"{folder_name}.zip")
        
        # Supprimer le dossier et le fichier zip s'ils existent
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        if os.path.exists(zip_path):
            os.remove(zip_path)
            
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def log_step(message):
    global execution_logs
    execution_logs.append(message)
    # Limite la taille pour éviter de saturer la mémoire
    if len(execution_logs) > 500:
        execution_logs = execution_logs[-500:]

@app.route('/execution_logs')
def get_execution_logs():
    global execution_logs
    return jsonify({"logs": execution_logs})

@app.route('/rf_live_log')
def get_rf_live_log():
    global rf_live_log
    return jsonify({"log": rf_live_log})

def add_rf_log(line):
    global rf_live_log
    rf_live_log.append(line)
    if len(rf_live_log) > 1000:
        rf_live_log = rf_live_log[-1000:]

def execute_test_command(test_file, test_result_dir):
    """
    Exécute un test Robot Framework et retourne les informations de résultat.
    
    Args:
        test_file (str): Le chemin du fichier de test à exécuter
        test_result_dir (str): Le dossier où sauvegarder les résultats
        
    Returns:
        tuple: (output_file_path, return_code)
    """
    process = subprocess.Popen(
        ["robot", "--outputdir", test_result_dir, os.path.join(TESTS_FOLDER, test_file)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    add_rf_log(f"================= {test_file} =================")
    for line in process.stdout:
        add_rf_log(line.rstrip())
    
    process.wait()
    
    output_file = os.path.join(test_result_dir, "output.xml")
    return output_file if os.path.exists(output_file) else None, process.returncode

@app.route('/execute', methods=['POST'])
def execute_single_test():
    """
    API endpoint pour exécuter un test spécifique.
    Attend un JSON avec les champs:
    - test_file: nom du fichier de test à exécuter
    - test_name: nom du test spécifique à exécuter (optionnel)
    """
    try:
        data = request.get_json()
        if not data or 'test_file' not in data:
            return jsonify({"error": "Le fichier de test est requis"}), 400

        test_file = data['test_file']
        test_name = data.get('test_name')  # Optionnel

        # Vérifier si le fichier existe
        if not os.path.exists(os.path.join(TESTS_FOLDER, test_file)):
            return jsonify({"error": f"Le fichier de test {test_file} n'existe pas"}), 404

        # Créer un dossier de résultats unique
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        test_result_dir = os.path.join(RESULTS_FOLDER, f"Single_Test_{timestamp}_{os.path.splitext(test_file)[0]}")
        os.makedirs(test_result_dir, exist_ok=True)

        # Construire la commande robot
        robot_command = ["robot"]
        if test_name:
            robot_command.extend(["--test", test_name])
        robot_command.extend(["--outputdir", test_result_dir, os.path.join(TESTS_FOLDER, test_file)])

        # Exécuter le test
        process = subprocess.Popen(
            robot_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Capturer les logs en temps réel
        logs = []
        for line in process.stdout:
            log_line = line.rstrip()
            logs.append(log_line)
            add_rf_log(log_line)

        process.wait()

        # Vérifier le résultat
        output_file = os.path.join(test_result_dir, "output.xml")
        if not os.path.exists(output_file):
            return jsonify({
                "error": "Le test n'a pas généré de fichier de sortie",
                "logs": logs,
                "return_code": process.returncode
            }), 500

        # Générer le rapport final
        final_report_dir = os.path.join(test_result_dir, "final_report")
        os.makedirs(final_report_dir, exist_ok=True)
        
        subprocess.run(
            ["rebot", "--outputdir", final_report_dir, output_file],
            capture_output=True,
            text=True
        )

        return jsonify({
            "success": True,
            "test_file": test_file,
            "test_name": test_name,
            "result_dir": test_result_dir,
            "return_code": process.returncode,
            "logs": logs,
            "report_path": os.path.join(final_report_dir, "report.html")
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

app.run(host='0.0.0.0', port=5000)
if __name__ == '__main__':
    app.run(debug=True)
