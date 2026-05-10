import os

import httpx


DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"
TIMEOUT_SECONDS = 60.0


def _resolver_api_base_url():
    raw_url = os.getenv("AGENT_API_BASE_URL", "").strip()

    if not raw_url:
        return DEFAULT_API_BASE_URL

    if raw_url.startswith(("http://", "https://")):
        return raw_url.rstrip("/")

    raise ValueError(
        "AGENT_API_BASE_URL debe empezar por http:// o https://. "
        f"Valor recibido: {raw_url}"
    )


API_BASE_URL = _resolver_api_base_url()


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
