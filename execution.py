import os
import subprocess
import datetime
import shutil
import requests
from typing import List, Optional, Tuple, Dict, Any
import matplotlib.pyplot as plt
import re
from collections import defaultdict

# Constants
TESTS_FOLDER = "test_cases"
RESULTS_FOLDER = "resultats"

from config import get_host_url, get_appium_url, get_remote_adb_host

url_host = get_host_url()
def send_results_to_api(zip_path: str) -> Dict[str, Any]:
    """
    Envoie le fichier ZIP des résultats à l'API Flask.
    
    Args:
        zip_path (str): Chemin vers le fichier ZIP à envoyer
        
    Returns:
        Dict contenant la réponse de l'API
    """
    try:
        if not os.path.exists(zip_path):
            return {
                "success": False,
                "error": f"Le fichier ZIP {zip_path} n'existe pas"
            }

        # Préparer la requête
        url = url_host+"/upload-zip"
        files = {'file': open(zip_path, 'rb')}

        # Envoyer la requête
        response = requests.post(url, files=files)
        
        # Fermer le fichier
        files['file'].close()

        # Vérifier la réponse
        if response.status_code == 200:
            return {
                "success": True,
                "message": "Fichier ZIP envoyé avec succès",
                "response": response.json()
            }
        else:
            return {
                "success": False,
                "error": f"Erreur lors de l'envoi du fichier: {response.text}",
                "status_code": response.status_code
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Erreur lors de l'envoi du fichier: {str(e)}"
        }

def execute_single_test(test_file: str, test_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute a single test from a Robot Framework file.
    
    Args:
        test_file (str): Name of the .robot file to execute
        test_name (str, optional): Specific test name to execute. If None, all tests in file will run.
        
    Returns:
        Dict containing execution results including:
        - success (bool): Whether the test execution was successful
        - test_file (str): Name of the test file
        - test_name (str): Name of the specific test (if any)
        - result_dir (str): Directory containing test results
        - return_code (int): Return code from robot execution
        - logs (List[str]): Execution logs
        - report_path (str): Path to the generated report
    """
    try:
        # Verify test file exists
        test_file_path = os.path.join(TESTS_FOLDER, test_file)
        if not os.path.exists(test_file_path):
            return {
                "success": False,
                "error": f"Test file {test_file} does not exist"
            }

        # Create unique results directory
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        test_result_dir = os.path.join(RESULTS_FOLDER, f"Tests_{timestamp}_{os.path.splitext(test_file)[0]}")
        os.makedirs(test_result_dir, exist_ok=True)

        # Définir la variable d'environnement pour le dossier de sortie Flask
        os.environ['FLASK_OUTPUT_DIR'] = test_result_dir

        # Build robot command
        robot_command = ["robot"]
        if test_name:
            robot_command.extend(["--test", test_name])
        robot_command.extend(["--outputdir", test_result_dir, test_file_path])

        # Execute test
        process = subprocess.Popen(
            robot_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Capture logs
        logs = []
        for line in process.stdout:
            line = line.rstrip()
            print(line, flush=True)
            logs.append(line)

        process.wait()

        # Check result
        output_file = os.path.join(test_result_dir, "output.xml")
        if not os.path.exists(output_file):
            return {
                "success": False,
                "error": "Test did not generate output file",
                "logs": logs,
                "return_code": process.returncode
            }

        # Generate final report
        final_report_dir = os.path.join(test_result_dir, "final_report")
        os.makedirs(final_report_dir, exist_ok=True)
        
        subprocess.run(
            ["rebot", "--outputdir", final_report_dir, output_file],
            capture_output=True,
            text=True
        )

        # Create zip archive of results
        zip_path = shutil.make_archive(test_result_dir, 'zip', test_result_dir)
        
        # Envoyer le fichier ZIP à l'API
        api_result = send_results_to_api(zip_path)
        if not api_result["success"]:
            print(f"Attention: Erreur lors de l'envoi du fichier ZIP à l'API: {api_result.get('error')}")

        return {
            "success": True,
            "test_file": test_file,
            "test_name": test_name,
            "result_dir": test_result_dir,
            "return_code": process.returncode,
            "logs": logs,
            "report_path": os.path.join(final_report_dir, "report.html"),
            "zip_path": zip_path,
            "api_result": api_result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def execute_test_list(test_files: List[str]) -> Dict[str, Any]:
    """
    Execute multiple Robot Framework test files.
    
    Args:
        test_files (List[str]): List of .robot files to execute
        
    Returns:
        Dict containing execution results including:
        - success (bool): Whether all tests were successful
        - results (List[Dict]): Results for each test file
        - combined_report_path (str): Path to the combined report
    """
    try:
        # Create results directory
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        test_names = "_".join([os.path.splitext(f)[0] for f in test_files])
        results_dir = os.path.join(RESULTS_FOLDER, f"Tests_{timestamp}_{test_names}")
        os.makedirs(results_dir, exist_ok=True)

        # Définir la variable d'environnement pour le dossier de sortie Flask
        os.environ['FLASK_OUTPUT_DIR'] = results_dir

        cpu_log = os.path.join(os.getcwd(), "cpu_usage.log")
        mem_log = os.path.join(os.getcwd(), "mem_usage.log")

        # Vider les fichiers
        with open(cpu_log, "w") as f:
            pass

        with open(mem_log, "w") as f:
            pass

        output_files = []
        results = []

        for test_file in test_files:
            # Execute each test file
            result = execute_single_test(test_file)
            results.append(result)
            
            if result["success"]:
                output_file = os.path.join(result["result_dir"], "output.xml")
                if os.path.exists(output_file):
                    output_files.append(output_file)

        # Generate combined report if we have output files
        combined_report_path = None
        if output_files:
            final_report_dir = os.path.join(results_dir, "final_report")
            os.makedirs(final_report_dir, exist_ok=True)
            
            subprocess.run(
                ["rebot", "--outputdir", final_report_dir] + output_files,
                capture_output=True,
                text=True
            )
            combined_report_path = os.path.join(final_report_dir, "report.html")

        # Générer les graphiques CPU et mémoire
        try:
            # Chemin des fichiers de logs (créés dans le répertoire racine)
            cpu_log = os.path.join(os.getcwd(), "cpu_usage.log")
            mem_log = os.path.join(os.getcwd(), "mem_usage.log")

            # Vérifier si les fichiers existent et générer les graphiques
            if os.path.exists(cpu_log):
                cpu_data = extract_data(cpu_log)
                if cpu_data:
                    cpu_chart_path = os.path.join(final_report_dir, 'cpu_usage_chart.png')
                    create_bar_chart(cpu_data,
                                   'CPU Usage by Test',
                                   'CPU Usage (%)',
                                   cpu_chart_path)
                    print(f"CPU chart generated: {cpu_chart_path}")

            if os.path.exists(mem_log):
                mem_data = extract_data(mem_log)
                if mem_data:
                    mem_chart_path = os.path.join(final_report_dir, 'mem_usage_chart.png')
                    create_bar_chart(mem_data,
                                   'Memory Usage by Test',
                                   'Memory Usage (MB)',
                                   mem_chart_path)
                    print(f"Memory chart generated: {mem_chart_path}")

            print("Charts generated in final_report directory")
        except Exception as e:
            print(f"Error generating charts: {str(e)}")
            import traceback
            traceback.print_exc()
        # Create zip archive of results

        zip_path = shutil.make_archive(results_dir, 'zip', results_dir)
        
        # Envoyer le fichier ZIP à l'API
        api_result = send_results_to_api(zip_path)
        if not api_result["success"]:
            print(f"Attention: Erreur lors de l'envoi du fichier ZIP à l'API: {api_result.get('error')}")

        return {
            "success": all(r["success"] for r in results),
            "results": results,
            "combined_report_path": combined_report_path,
            "results_dir": results_dir,
            "zip_path": zip_path,
            "api_result": api_result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def execute_test_with_tags(test_file: str, tags: List[str]) -> Dict[str, Any]:
    """
    Execute tests from a Robot Framework file that match specific tags.
    
    Args:
        test_file (str): Name of the .robot file to execute
        tags (List[str]): List of tags to match
        
    Returns:
        Dict containing execution results
    """
    try:
        # Verify test file exists
        test_file_path = os.path.join(TESTS_FOLDER, test_file)
        if not os.path.exists(test_file_path):
            return {
                "success": False,
                "error": f"Test file {test_file} does not exist"
            }

        # Create results directory
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        test_result_dir = os.path.join(RESULTS_FOLDER, f"Tests_{timestamp}_{os.path.splitext(test_file)[0]}")
        os.makedirs(test_result_dir, exist_ok=True)

        # Définir la variable d'environnement pour le dossier de sortie Flask
        os.environ['FLASK_OUTPUT_DIR'] = test_result_dir

        # Build robot command with tags
        robot_command = ["robot"]
        for tag in tags:
            robot_command.extend(["--include", tag])
        robot_command.extend(["--outputdir", test_result_dir, test_file_path])

        # Execute test
        process = subprocess.Popen(
            robot_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Capture logs
        logs = []
        for line in process.stdout:
            line = line.rstrip()
            print(line, flush=True)
            logs.append(line)

        process.wait()

        # Check result
        output_file = os.path.join(test_result_dir, "output.xml")
        if not os.path.exists(output_file):
            return {
                "success": False,
                "error": "Test did not generate output file",
                "logs": logs,
                "return_code": process.returncode
            }

        # Generate final report
        final_report_dir = os.path.join(test_result_dir, "final_report")
        os.makedirs(final_report_dir, exist_ok=True)
        
        subprocess.run(
            ["rebot", "--outputdir", final_report_dir, output_file],
            capture_output=True,
            text=True
        )

        # Create zip archive of results
        zip_path = shutil.make_archive(test_result_dir, 'zip', test_result_dir)
        
        # Envoyer le fichier ZIP à l'API
        api_result = send_results_to_api(zip_path)
        if not api_result["success"]:
            print(f"Attention: Erreur lors de l'envoi du fichier ZIP à l'API: {api_result.get('error')}")

        return {
            "success": True,
            "test_file": test_file,
            "tags": tags,
            "result_dir": test_result_dir,
            "return_code": process.returncode,
            "logs": logs,
            "report_path": os.path.join(final_report_dir, "report.html"),
            "zip_path": zip_path,
            "api_result": api_result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


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
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Robot Framework Test Executor")
    parser.add_argument(
        "--list",
        nargs="+",
        help="List of .robot test files to execute"
    )
    parser.add_argument(
        "--single",
        nargs=2,
        metavar=("FILE", "TEST_NAME"),
        help="Execute a single test case from a .robot file"
    )
    parser.add_argument(
        "--tags",
        nargs="+",
        metavar=("FILE", "TAG"),
        help="Execute tests from a .robot file with given tags (first arg is file)"
    )

    args = parser.parse_args()

    if args.list:
        result = execute_test_list(args.list)
        for res in result.get("results", []):
            print(f"\n=== Logs for {res.get('test_file')} ===")
            for line in res.get("logs", []):
                print(line)
        print(result)
    elif args.single:
        file, test_name = args.single
        result = execute_single_test(file, test_name)
        print(f"\n=== Logs for {file} ===")
        for line in result.get("logs", []):
            print(line)
        print(result)
    elif args.tags:
        file = args.tags[0]
        tags = args.tags[1:]
        result = execute_test_with_tags(file, tags)
        print(f"\n=== Logs for {file} with tags {tags} ===")
        for line in result.get("logs", []):
            print(line)
        print(result)
    else:
        print("No valid argument passed. Use --help for options.")
