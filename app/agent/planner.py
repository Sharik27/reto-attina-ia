import unicodedata

from app.agent.tool_specs import TOOL_SPECS


def _normalizar(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    return "".join(caracter for caracter in texto if unicodedata.category(caracter) != "Mn")


def _crear_tool_call(name, reason):
    spec = TOOL_SPECS[name]
    return {
        "name": spec["name"],
        "args": {},
        "reason": reason,
    }


def planear_tool_calls(pregunta):
    pregunta = _normalizar(pregunta)

    if _contiene(pregunta, ["analisis completo", "analisis", "diagnostico", "panorama", "todo", "general"]):
        return [
            _crear_tool_call(
                "analizar_propagacion",
                "El usuario pidio un analisis general; la propagacion da la estructura de la conversacion.",
            ),
            _crear_tool_call(
                "analizar_sentimientos",
                "El usuario pidio un analisis general; los sentimientos aportan percepcion agregada.",
            ),
            _crear_tool_call(
                "generar_resumen",
                "El usuario pidio un analisis general; el resumen sintetiza el contenido.",
            ),
        ]

    if _contiene(pregunta, ["sentimiento", "sentimientos", "emocion", "emociones", "polaridad", "positivo", "positiva", "negativo", "negativa", "negatividad"]):
        return [
            _crear_tool_call(
                "analizar_sentimientos",
                "La pregunta menciona sentimientos, polaridad o emociones.",
            )
        ]

    if _contiene(pregunta, ["propagacion", "propago", "propaga", "difusion", "viralidad", "hilos", "profundidad", "respuestas", "mensaje", "conversacion"]):
        return [
            _crear_tool_call(
                "analizar_propagacion",
                "La pregunta menciona propagacion, hilos, profundidad o respuestas.",
            )
        ]

    if _contiene(pregunta, ["resumen", "resume", "sintesis", "sintetiza", "temas", "explica"]):
        return [
            _crear_tool_call(
                "generar_resumen",
                "La pregunta solicita resumen, sintesis o temas principales.",
            )
        ]

    return []


def _contiene(texto, claves):
    return any(clave in texto for clave in claves)
