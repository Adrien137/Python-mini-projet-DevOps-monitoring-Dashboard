"""Collecte des métriques système (CPU, mémoire, disque) via psutil."""

import psutil


def get_system_metrics() -> dict:
    """Retourne un snapshot instantané des métriques système.

    Utilise interval=None pour un appel non-bloquant : le pourcentage CPU
    est calculé par rapport au dernier appel (ou 0.0 lors du tout premier
    appel du processus).

    Returns:
        dict avec les clés cpu_percent, memory_percent, disk_percent
        (toutes des valeurs flottantes entre 0 et 100).
    """
    cpu_percent = psutil.cpu_percent(interval=None)
    memory_percent = psutil.virtual_memory().percent
    disk_percent = psutil.disk_usage("/").percent

    return {
        "cpu_percent": cpu_percent,
        "memory_percent": memory_percent,
        "disk_percent": disk_percent,
    }
