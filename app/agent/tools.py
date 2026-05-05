import os

import httpx


API_BASE_URL = os.getenv("AGENT_API_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT_SECONDS = 60.0


def _get(endpoint):
    url = f"{API_BASE_URL}{endpoint}"
    with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.json()


def obtener_sentimientos():
    return _get("/analisis/sentimientos")


def obtener_resumen():
    return _get("/analisis/resumen")


def obtener_propagacion():
    return _get("/analisis/propagacion")
