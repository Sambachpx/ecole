"""Client HTTP du micro-service de métadonnées audio (TP #11)."""

import os
import urllib.parse

import httpx

METADATA_SERVICE_URL = os.getenv(
    "METADATA_SERVICE_URL", "http://localhost:8001/metadata"
)


def extract_metadata(file_path: str) -> tuple[str, int]:
    """Récupère (titre, durée) d'un fichier audio via le micro-service.

    Le fichier doit déjà exister sur disque : l'appelant le sauvegarde
    (et persiste la Song) avant cet appel.
    """
    absolute_path = os.path.abspath(file_path)
    params = {"file_path": urllib.parse.quote(absolute_path)}
    resp = httpx.get(METADATA_SERVICE_URL, params=params, timeout=10.0)
    resp.raise_for_status()
    data = resp.json()
    return str(data["name"]), int(data["duration"])
