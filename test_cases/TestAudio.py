import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import find_peaks, stft, correlation_lags
import os
from datetime import datetime
import requests
import logging

logger = logging.getLogger(__name__)


def load_and_preprocess(audio_path, target_fs=None):
    """Charge et prétraite un fichier audio"""
    try:
        data, fs = sf.read(audio_path)

        # Conversion mono si stéréo
        if data.ndim > 1:
            data = data.mean(axis=1)

        # Resample si nécessaire
        if target_fs is not None and fs != target_fs:
            data = signal.resample(data, int(len(data) * target_fs / fs))
            fs = target_fs

        # Normalisation
        data = data / (np.max(np.abs(data)) + 1e-10)

        return data, fs
    except Exception as e:
        raise ValueError(f"Erreur lors du chargement de {audio_path}: {str(e)}")


def find_audio_segment(signal, fs, min_duration=0.1, threshold_db=-40):
    """Trouve le segment audio actif principal"""
    # Calcul de l'enveloppe RMS
    window_size = int(fs * 0.05)  # 50ms
    rms = np.sqrt(np.convolve(signal ** 2, np.ones(window_size) / window_size, mode='same'))

    # Seuil en dB
    threshold = 10 ** (threshold_db / 20) * np.max(rms)

    # Détection des régions actives
    active = rms > threshold
    active_diff = np.diff(active.astype(int))
    starts = np.where(active_diff == 1)[0]
    ends = np.where(active_diff == -1)[0]

    # Gestion des bords
    if len(ends) == 0 or (len(starts) > 0 and starts[0] > ends[0]):
        starts = np.insert(starts, 0, 0)
    if len(starts) == 0 or (len(ends) > 0 and ends[-1] < starts[-1]):
        ends = np.append(ends, len(active))

    # Trouver le segment le plus long
    max_duration = 0
    best_start, best_end = 0, len(signal)

    for s, e in zip(starts, ends):
        if e - s > max_duration:
            max_duration = e - s
            best_start, best_end = s, e

    # Vérification durée minimale
    if max_duration < min_duration * fs:
        return signal, 0, 0

    return signal[best_start:best_end], best_start / fs, best_end / fs


def try_multiple_alignments(original, recorded, fs, max_shift_samples=100000):
    """Essaie plusieurs décalages pour trouver la meilleure corrélation"""
    best_corr = -1
    best_shift = 0
    best_aligned = None

    # Essayer des décalages positifs et négatifs
    shifts = np.arange(-max_shift_samples, max_shift_samples, int(fs * 0.1))  # Pas de 100ms

    for shift in shifts:
        if shift > 0:
            if shift >= len(recorded):
                continue
            aligned = recorded[shift:]
            # Tronquer à la longueur minimale
            min_len = min(len(original), len(aligned))
            aligned = aligned[:min_len]
            orig = original[:min_len]
        else:
            if abs(shift) >= len(original):
                continue
            aligned = np.pad(recorded, (abs(shift), 0), mode='constant')
            # Tronquer à la longueur minimale
            min_len = min(len(original), len(aligned))
            aligned = aligned[:min_len]
            orig = original[:min_len]

        # Vérifier que les longueurs sont identiques
        if len(orig) != len(aligned):
            print(f"Warning: Length mismatch - orig: {len(orig)}, aligned: {len(aligned)}")
            continue

        # Calculer la corrélation
        corr = np.corrcoef(orig, aligned)[0, 1]

        if corr > best_corr:
            best_corr = corr
            best_shift = shift
            best_aligned = aligned

    if best_aligned is None:
        raise ValueError("Aucun alignement valide n'a été trouvé")

    return best_aligned, best_shift / fs, best_corr


def align_signals(original, recorded, fs):
    """Aligne les deux signaux en utilisant la corrélation croisée"""
    # Print initial lengths for debugging
    print(f"Original length: {len(original)}, Recorded length: {len(recorded)}")

    corr = signal.correlate(recorded, original, mode='full', method='fft')
    lags = correlation_lags(len(recorded), len(original), mode='full')
    best_lag = lags[np.argmax(corr)]

    print(f"Best lag: {best_lag} samples ({best_lag / fs:.3f} seconds)")

    # Ensure we have enough samples after alignment
    if best_lag > 0:
        if best_lag >= len(recorded):
            raise ValueError("Best lag is larger than recorded signal length")
        aligned = recorded[best_lag:]
        original = original[:len(aligned)]
    elif best_lag < 0:
        if abs(best_lag) >= len(original):
            raise ValueError("Best lag is larger than original signal length")
        aligned = np.pad(recorded, (abs(best_lag), 0), mode='constant')
        aligned = aligned[:len(original)]
    else:
        aligned = recorded[:len(original)]

    # Ensure both signals have exactly the same length
    min_len = min(len(original), len(aligned))
    original = original[:min_len]
    aligned = aligned[:min_len]

    print(f"Final lengths - Original: {len(original)}, Aligned: {len(aligned)}")

    return original, aligned, best_lag / fs


def calculate_metrics(original, recorded, fs):
    """Calcule les métriques de qualité audio"""
    noise = original - recorded

    # SNR
    signal_power = np.mean(original ** 2)
    noise_power = np.mean(noise ** 2)
    snr = 10 * np.log10(signal_power / (noise_power + 1e-10))

    # Corrélation
    corr = np.corrcoef(original, recorded)[0, 1]

    # MSE et RMSE
    mse = np.mean(noise ** 2)
    rmse = np.sqrt(mse)

    # Rapport d'énergie
    energy_ratio = np.sum(recorded ** 2) / (np.sum(original ** 2) + 1e-10)

    # MOS estimé basé sur plusieurs paramètres
    # 1. Composante SNR (40% du score)
    snr_score = np.clip((snr + 10) / 40, 0, 1)  # -10dB = 0, 30dB = 1

    # 2. Composante corrélation (30% du score)
    corr_score = np.clip(corr, 0, 1)

    # 3. Composante clarté (30% du score)
    f_orig = np.abs(np.fft.rfft(original))
    f_rec = np.abs(np.fft.rfft(recorded))
    freqs = np.fft.rfftfreq(len(original), 1 / fs)

    # Poids pour les fréquences vocales importantes (300-3400Hz)
    weight = np.zeros_like(freqs)
    weight[(freqs >= 300) & (freqs <= 3400)] = 1
    weight[(freqs > 3400) & (freqs <= 8000)] = 0.5

    clarity = np.sum(weight * f_rec) / (np.sum(weight * f_orig) + 1e-10)
    clarity_score = np.clip(clarity, 0, 1)

    # Calcul du MOS final (échelle 1-5)
    mos = 1 + 4 * (0.4 * snr_score + 0.3 * corr_score + 0.3 * clarity_score)
    mos = np.clip(mos, 1, 5)

    # Rapport de clarté en dB
    clarity_db = 10 * np.log10(clarity + 1e-10)

    return {
        'snr': snr,
        'correlation': corr,
        'mse': mse,
        'rmse': rmse,
        'energy_ratio': energy_ratio,
        'max_diff': np.max(np.abs(noise)),
        'mean_diff': np.mean(np.abs(noise)),
        'mos': mos,
        'clarity': clarity,
        'clarity_db': clarity_db
    }


def plot_comparison(original, recorded, noise, fs, metrics, time_shift, test_type="enregistrement"):
    """Sauvegarde les graphiques de comparaison"""
    # Décimer les signaux pour la visualisation
    decimation_factor = 10
    time = np.arange(len(original))[::decimation_factor] / fs
    orig_plot = original[::decimation_factor]
    rec_plot = recorded[::decimation_factor]
    noise_plot = noise[::decimation_factor]

    # Créer la figure avec un titre principal
    plt.figure(figsize=(15, 15))
    plt.suptitle(f'Analyse de Qualité Audio - Test de {test_type}', fontsize=16, y=0.95)

    # Signaux alignés
    plt.subplot(4, 2, 1)
    plt.plot(time, orig_plot, label='Original')
    plt.plot(time, rec_plot, alpha=0.7, label=f'Enregistrement (décalage: {time_shift:.3f}s)')
    plt.title('Signaux alignés')
    plt.xlabel('Temps [s]')
    plt.ylabel('Amplitude')
    plt.legend()

    # Différence
    plt.subplot(4, 2, 2)
    plt.plot(time, noise_plot, color='red')
    plt.title('Signal de différence')
    plt.xlabel('Temps [s]')
    plt.ylabel('Amplitude')

    # Spectrogramme original
    plt.subplot(4, 2, 3)
    f, t, Sxx = stft(original, fs, nperseg=512, noverlap=256)
    plt.pcolormesh(t, f, 20 * np.log10(np.abs(Sxx) + 1e-10), shading='gouraud', cmap='viridis')
    plt.colorbar(label='dB')
    plt.title('Spectrogramme - Original')
    plt.xlabel('Temps [s]')
    plt.ylabel('Fréquence [Hz]')

    # Spectrogramme enregistré
    plt.subplot(4, 2, 4)
    f, t, Sxx = stft(recorded, fs, nperseg=512, noverlap=256)
    plt.pcolormesh(t, f, 20 * np.log10(np.abs(Sxx) + 1e-10), shading='gouraud', cmap='viridis')
    plt.colorbar(label='dB')
    plt.title('Spectrogramme - Enregistré')
    plt.xlabel('Temps [s]')
    plt.ylabel('Fréquence [Hz]')

    # Analyse fréquentielle (FFT)
    plt.subplot(4, 2, 5)
    n_fft = min(4096, len(original))
    f_orig = np.fft.rfft(original[:n_fft])
    f_rec = np.fft.rfft(recorded[:n_fft])
    freqs = np.fft.rfftfreq(n_fft, 1 / fs)
    plt.semilogx(freqs, 20 * np.log10(np.abs(f_orig) + 1e-10), label='Original')
    plt.semilogx(freqs, 20 * np.log10(np.abs(f_rec) + 1e-10), alpha=0.7, label='Enregistré')
    plt.title('Spectre de fréquence')
    plt.xlabel('Fréquence [Hz]')
    plt.ylabel('Amplitude [dB]')
    plt.legend()
    plt.grid(True)

    # Corrélation temporelle
    plt.subplot(4, 2, 6)
    corr = np.correlate(original[::decimation_factor], recorded[::decimation_factor], mode='full')
    lags = np.arange(-len(original[::decimation_factor]) + 1, len(original[::decimation_factor]))
    plt.plot(lags / fs * decimation_factor, corr)
    plt.title('Corrélation temporelle')
    plt.xlabel('Décalage [s]')
    plt.ylabel('Corrélation')
    plt.grid(True)

    # Enveloppe RMS
    plt.subplot(4, 2, 7)
    window_size = int(fs * 0.05)
    rms_orig = np.sqrt(np.convolve(original[::decimation_factor] ** 2, np.ones(window_size//decimation_factor) / (window_size//decimation_factor), mode='same'))
    rms_rec = np.sqrt(np.convolve(recorded[::decimation_factor] ** 2, np.ones(window_size//decimation_factor) / (window_size//decimation_factor), mode='same'))
    plt.plot(time, rms_orig, label='Original')
    plt.plot(time, rms_rec, alpha=0.7, label='Enregistré')
    plt.title('Enveloppe RMS')
    plt.xlabel('Temps [s]')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid(True)

    # Différence spectrale
    plt.subplot(4, 2, 8)
    diff_spectrum = 20 * np.log10(np.abs(f_orig) + 1e-10) - 20 * np.log10(np.abs(f_rec) + 1e-10)
    plt.semilogx(freqs, diff_spectrum)
    plt.title('Différence spectrale')
    plt.xlabel('Fréquence [Hz]')
    plt.ylabel('Différence [dB]')
    plt.grid(True)

    plt.tight_layout()

    # Créer une boîte de texte avec les métriques et le statut du test
    test_status = "✅ TEST RÉUSSI" if (metrics['correlation'] >= 0.4 and 
                                     metrics['mos'] >= 3.0 and metrics['clarity'] >= 0.8) else "❌ TEST ÉCHEC"
    
    metrics_text = (
        f"{test_status}\n\n"
        f"Type de test: {test_type.upper()}\n\n"
        f"Métriques de Qualité:\n"
        f"• SNR: {metrics['snr']:.2f} dB\n"
        f"• Corrélation: {metrics['correlation']:.3f} (seuil: 0.4)\n"
        f"• MOS: {metrics['mos']:.2f}/5 (seuil: 3.0)\n"
        f"• Clarté: {metrics['clarity']:.3f} (seuil: 0.8)\n\n"
        f"Métriques Additionnelles:\n"
        f"• RMSE: {metrics['rmse']:.4f}\n"
        f"• Rapport d'énergie: {metrics['energy_ratio']:.3f}\n"
        f"• Clarté (dB): {metrics['clarity_db']:.2f} dB\n"
        f"• Décalage temporel: {time_shift:.3f} s"
    )

    # Ajouter la boîte de texte avec un fond blanc semi-transparent
    plt.gcf().text(0.95, 0.5, metrics_text, 
                  bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=1'),
                  fontsize=10, ha='right', va='center')

    # Sauvegarder la figure dans le dossier de rapport Flask
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Utiliser le dossier de sortie de Flask
    output_dir = os.path.join(os.environ.get('FLASK_OUTPUT_DIR', '.'), 'plots')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'audio_comparison_{test_type}_{timestamp}.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    return output_file


def find_best_segments(original, recorded, fs, search_window_ms=1000):
    """Trouve le meilleur alignement entre les deux signaux"""
    # Convertir la fenêtre de recherche en samples
    search_samples = int(search_window_ms * fs / 1000)  # Convertir ms en samples
    
    # Réduire la taille des signaux pour l'alignement initial
    # Utiliser un sous-échantillonnage plus agressif pour accélérer la recherche
    decimation_factor = 50  # Augmenté de 10 à 50 pour accélérer
    orig_decimated = original[::decimation_factor]
    rec_decimated = recorded[::decimation_factor]
    search_samples_decimated = search_samples // decimation_factor
    
    # Pour chaque décalage possible dans la fenêtre de recherche
    best_corr = -1
    best_shift = 0
    
    print("Recherche du meilleur alignement...")
    
    # Chercher le meilleur décalage initial sur le signal décimé
    for shift in range(-search_samples_decimated, search_samples_decimated + 1, 2):  # Pas de 2 pour accélérer
        if shift > 0:
            if shift >= len(rec_decimated):
                continue
            rec_shifted = rec_decimated[shift:]
            min_len = min(len(orig_decimated), len(rec_shifted))
            orig = orig_decimated[:min_len]
            rec_shifted = rec_shifted[:min_len]
        else:
            if abs(shift) >= len(orig_decimated):
                continue
            rec_shifted = np.pad(rec_decimated, (abs(shift), 0), mode='constant')
            min_len = min(len(orig_decimated), len(rec_shifted))
            rec_shifted = rec_shifted[:min_len]
            orig = orig_decimated[:min_len]

        # Calculer la corrélation
        corr = np.corrcoef(orig, rec_shifted)[0, 1]
        
        if corr > best_corr:
            best_corr = corr
            best_shift = shift * decimation_factor

    print("Alignement initial trouvé, ajustement fin...")
    
    # Ajustement fin autour du meilleur décalage trouvé
    fine_search = 50  # Réduit de 100 à 50 samples pour l'ajustement fin
    best_corr = -1
    final_shift = best_shift
    
    for shift in range(best_shift - fine_search, best_shift + fine_search + 1, 2):  # Pas de 2 pour accélérer
        if shift > 0:
            if shift >= len(recorded):
                continue
            rec_shifted = recorded[shift:]
            min_len = min(len(original), len(rec_shifted))
            orig = original[:min_len]
            rec_shifted = rec_shifted[:min_len]
        else:
            if abs(shift) >= len(original):
                continue
            rec_shifted = np.pad(recorded, (abs(shift), 0), mode='constant')
            min_len = min(len(original), len(rec_shifted))
            rec_shifted = rec_shifted[:min_len]
            orig = original[:min_len]

        corr = np.corrcoef(orig, rec_shifted)[0, 1]
        
        if corr > best_corr:
            best_corr = corr
            final_shift = shift

    # Appliquer le meilleur décalage
    if final_shift > 0:
        best_rec = recorded[final_shift:]
        min_len = min(len(original), len(best_rec))
        best_orig = original[:min_len]
        best_rec = best_rec[:min_len]
    else:
        best_rec = np.pad(recorded, (abs(final_shift), 0), mode='constant')
        min_len = min(len(original), len(best_rec))
        best_rec = best_rec[:min_len]
        best_orig = original[:min_len]

    # Calculer les positions temporelles
    orig_start = 0
    rec_start = final_shift / fs

    print(f"\nDétails de l'alignement:")
    print(f"Position originale: {orig_start:.3f}s")
    print(f"Position enregistrée: {rec_start:.3f}s")
    print(f"Ajustement: {final_shift / fs * 1000:.1f}ms")
    print(f"Corrélation initiale: {best_corr:.3f}")

    return best_orig, best_rec, orig_start, rec_start, best_corr


def audio_quality_test(original_path, recorded_path, snr_threshold=-1, corr_threshold=0.4,
                       mos_threshold=3.0, clarity_threshold=0.8, test_type="enregistrement"):
    """Test complet de qualité audio"""
    print(f"\n{' Début du test audio ':=^80}")
    print(f"Original: {original_path}")
    print(f"Enregistré: {recorded_path}")
    print(f"Date du test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # Chargement des fichiers
        original, fs = load_and_preprocess(original_path)
        recorded, _ = load_and_preprocess(recorded_path, target_fs=fs)

        # Découpage des segments actifs
        orig_trimmed, orig_start, orig_end = find_audio_segment(original, fs)
        rec_trimmed, rec_start, rec_end = find_audio_segment(recorded, fs)

        print(f"Original - Durée: {len(original) / fs:.2f}s -> Segment actif: {len(orig_trimmed) / fs:.2f}s")
        print(f"Enregistré - Durée: {len(recorded) / fs:.2f}s -> Segment actif: {len(rec_trimmed) / fs:.2f}s")

        # Trouver le meilleur alignement
        best_orig, best_rec, orig_seg_start, rec_seg_start, best_corr = find_best_segments(
            orig_trimmed, rec_trimmed, fs, search_window_ms=1000
        )

        # Aligner les segments
        orig_aligned, rec_aligned, time_shift = align_signals(best_orig, best_rec, fs)
        print(f"Décalage temporel final: {time_shift:.3f} secondes")

        # Calcul des métriques
        metrics = calculate_metrics(orig_aligned, rec_aligned, fs)
        noise = orig_aligned - rec_aligned

        # Affichage
        print("\n=== Résultats ===")
        print(f"Décalage temporel: {time_shift:.3f} secondes")
        for k, v in metrics.items():
            print(f"{k:>12}: {v:.4f}" if isinstance(v, float) else f"{k:>12}: {v}")

        # Sauvegarder les graphiques
        plot_file = plot_comparison(orig_aligned, rec_aligned, noise, fs, metrics, time_shift, test_type)
        logger.info(f"Graphiques sauvegardés dans: {plot_file}")

        # Ajouter le chemin du graphique aux métriques
        metrics['plot_file'] = plot_file

        # Résultat du test
        test_passed = (
                       (metrics['correlation'] >= corr_threshold) and
                       (metrics['mos'] >= mos_threshold) and
                       (metrics['clarity'] >= clarity_threshold))

        print(f"\n=== Résultat: {'SUCCÈS' if test_passed else 'ÉCHEC'} ===")
        print(f"SNR: {metrics['snr']:.2f} dB (seuil: {snr_threshold} dB)")
        print(f"Corrélation: {metrics['correlation']:.3f} (seuil: {corr_threshold})")
        print(f"MOS: {metrics['mos']:.2f}/5 (seuil: {mos_threshold})")
        print(f"Clarté: {metrics['clarity']:.3f} (seuil: {clarity_threshold})")

        return test_passed, metrics

    except Exception as e:
        print(f"\n!!! Erreur lors du test: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False, None


def compare_with_latest_recorded(original_audio, latest_audio_path='latest_download.wav', api_url='http://localhost:6000/latest-audio'):
    """
    Télécharge le dernier audio enregistré via l'API Flask et le compare à l'original.
    :param original_audio: Chemin du fichier original (wav)
    :param latest_audio_path: Chemin où sauvegarder le fichier téléchargé
    :param api_url: URL de l'API Flask pour récupérer le dernier audio enregistré
    :return: (test_passed, metrics)
    """
    # Télécharger le dernier audio enregistré
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        with open(latest_audio_path, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        print(f"Erreur lors du téléchargement de l'audio enregistré: {e}")
        return False, {"error": str(e)}

    # Comparer avec la fonction audio_quality_test
    try:
        test_passed, metrics = audio_quality_test(original_audio, latest_audio_path, test_type="enregistrement")
        return test_passed, metrics
    except Exception as e:
        print(f"Erreur lors de la comparaison audio: {e}")
        return False, {"error": str(e)}

def compare_with_latest_recorded_play(original_audio, latest_audio_path='latest_playback.wav', api_url='http://localhost:6000/latest-audio-record-play'):
    """
    Télécharge le dernier audio lu via l'API Flask et le compare à l'original.
    :param original_audio: Chemin du fichier original (wav)
    :param latest_audio_path: Chemin où sauvegarder le fichier téléchargé
    :param api_url: URL de l'API Flask pour récupérer le dernier audio lu
    :return: (test_passed, metrics)
    """
    # Télécharger le dernier audio lu
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        with open(latest_audio_path, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        print(f"Erreur lors du téléchargement de l'audio lu: {e}")
        return False, {"error": str(e)}

    # Comparer avec la fonction audio_quality_test
    try:
        test_passed, metrics = audio_quality_test(original_audio, latest_audio_path, test_type="lecture")
        return test_passed, metrics
    except Exception as e:
        print(f"Erreur lors de la comparaison audio: {e}")
        return False, {"error": str(e)}



if __name__ == "__main__":
    # Exemple d'utilisation
    original_file = "test.wav"
    recorded_file = "azerty.wav"

    # Test avec l'ensemble du signal
    passed, metrics = audio_quality_test(original_file, recorded_file)

    if passed:
        print("\nTest audio réussi avec succès!")
    else:
        print("\nLe test audio a échoué.")
        if metrics:
            print("Raisons possibles:")
            if metrics['snr'] < 20:
                print(f"- SNR trop faible ({metrics['snr']:.2f} dB)")
            if metrics['correlation'] < 0.9:
                print(f"- Corrélation trop faible ({metrics['correlation']:.3f})")
            if metrics['energy_ratio'] < 0.5 or metrics['energy_ratio'] > 1.5:
                print(f"- Rapport d'énergie anormal ({metrics['energy_ratio']:.3f})")
            if metrics['mos'] < 3.0:
                print(f"- MOS trop faible ({metrics['mos']:.2f}/5)")
            if metrics['clarity'] < 0.8:
                print(f"- Clarté insuffisante ({metrics['clarity']:.3f})")