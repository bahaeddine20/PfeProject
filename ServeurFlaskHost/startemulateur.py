import sys
import subprocess
import time


def open_emulator(avd_name, port):
    """Lance l'émulateur avec le nom AVD et le port spécifiés"""
    try:
        # Construction de la commande avec les ports
        command = [
            "emulator",
            f"@{avd_name}",
            "-ports", f"{port},{port + 1}"  # Format: console_port,adb_port
        ]

        subprocess.Popen(command)
        print(f"🚀 Lancement de {avd_name} sur le port {port}...")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        return False


def check_emulator(port):
    """Vérifie si l'émulateur est actif sur le port spécifié"""
    try:
        # Vérification avec la commande adb
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return f"emulator-{port}" in result.stdout
    except:
        return False


if __name__ == "__main__":
    # Vérification des arguments
    if len(sys.argv) != 2 or sys.argv[1] not in ["mobile", "automotive"]:
        print("Usage: python startemulateur.py [mobile|automotive]")
        sys.exit(1)

    device_type = sys.argv[1]
    avd_name = ""
    port = 0

    # Configuration selon le type d'appareil
    if device_type == "mobile":
        avd_name = "Medium_Phone_API_35"
        port = 5556
    else:  # automotive
        avd_name = "Automotive_1408p_landscape_with_Google_Play_API_34-ext9_2"
        port = 5554

    # Lancement de l'émulateur
    if open_emulator(avd_name, port):
        print("⏳ Vérification de l'état de l'émulateur...")
        time.sleep(15)  # Temps d'attente pour le démarrage

        # Vérification de la connexion
        if check_emulator(port):
            print(f"✅ Émulateur {device_type} connecté sur emulator-{port}")
        else:
            print(f"⚠️ Avertissement: Émulateur détecté mais non connecté")
            print("Conseil: Exécutez 'adb connect emulator-{port}' manuellement")