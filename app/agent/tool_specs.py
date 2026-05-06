TOOL_SPECS = {
    "analizar_sentimientos": {
        "name": "analizar_sentimientos",
        "description": "Obtiene el analisis de sentimientos de las conversaciones digitales.",
        "endpoint": "/analisis/sentimientos",
        "args_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "generar_resumen": {
        "name": "generar_resumen",
        "description": "Genera un resumen automatico de la conversacion.",
        "endpoint": "/analisis/resumen",
        "args_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "analizar_propagacion": {
        "name": "analizar_propagacion",
        "description": "Analiza propagacion, hilos activos, profundidad y nodos respondidos.",
        "endpoint": "/analisis/propagacion",
        "args_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}


def obtener_tool_specs():
    return TOOL_SPECS
