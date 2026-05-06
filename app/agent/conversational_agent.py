import html

from app.agent.prompts import PROMPT_BASE
from app.agent.tools import (
    obtener_propagacion,
    obtener_resumen,
    obtener_sentimientos,
)


def _normalizar(texto):
    return texto.lower().strip()


def _formatear_sentimientos(respuesta):
    resultado = respuesta.get("resultado", respuesta)
    total = resultado.get("total", 0)
    positivo = resultado.get("positivo", 0)
    negativo = resultado.get("negativo", 0)

    return (
        "Analisis de sentimientos:\n"
        f"- Total analizado: {total}\n"
        f"- Positivos: {positivo}\n"
        f"- Negativos: {negativo}"
    )


def _formatear_resumen(respuesta):
    resultado = respuesta.get("resultado", respuesta)
    resumen = resultado.get("resumen")

    if not resumen:
        return f"No se pudo obtener un resumen limpio. Respuesta recibida: {resultado}"

    resumen = resumen.replace("Resume el siguiente texto:", "")
    resumen = " ".join(resumen.split())
    resumen = html.unescape(resumen)

    mitad = len(resumen) // 2
    if resumen[:mitad].strip() and resumen[:mitad].strip() == resumen[mitad:].strip():
        resumen = resumen[:mitad].strip()

    return f"Resumen de la conversacion:\n{resumen}"


def _formatear_propagacion(respuesta):
    resultado = respuesta.get("resultado", respuesta)
    hilos = resultado.get("hilos_mas_activos", [])
    nodos = resultado.get("nodos_mas_respondidos", [])

    lineas = [
        "Analisis de propagacion:",
        f"- Total de mensajes: {resultado.get('total_mensajes', 0)}",
        f"- Total de hilos: {resultado.get('total_hilos', 0)}",
        f"- Mensajes raiz: {resultado.get('mensajes_raiz', 0)}",
        f"- Respuestas: {resultado.get('respuestas', 0)}",
        f"- Profundidad maxima: {resultado.get('profundidad_maxima', 0)}",
    ]

    if hilos:
        hilo = hilos[0]
        lineas.append(
            "- Hilo mas activo: "
            f"{hilo.get('threadId')} con {hilo.get('mensajes')} mensajes"
        )

    if nodos:
        nodo = nodos[0]
        lineas.append(
            "- Nodo mas respondido: "
            f"{nodo.get('id')} con {nodo.get('respuestas_directas')} respuestas directas"
        )

    return "\n".join(lineas)


def _es_analisis_completo(pregunta):
    claves = ["analisis completo", "diagnostico", "panorama", "todo", "general"]
    return any(clave in pregunta for clave in claves)


def _requiere_sentimientos(pregunta):
    claves = ["sentimiento", "sentimientos", "emocion", "emociones", "polaridad", "positivo", "negativo"]
    return any(clave in pregunta for clave in claves)


def _requiere_resumen(pregunta):
    claves = ["resumen", "resume", "sintesis", "sintetiza", "temas", "explica"]
    return any(clave in pregunta for clave in claves)


def _requiere_propagacion(pregunta):
    claves = ["propagacion", "difusion", "viralidad", "hilos", "profundidad", "respuestas"]
    return any(clave in pregunta for clave in claves)


def responder(pregunta):
    pregunta_normalizada = _normalizar(pregunta)

    try:
        if _es_analisis_completo(pregunta_normalizada):
            propagacion = _formatear_propagacion(obtener_propagacion())
            sentimientos = _formatear_sentimientos(obtener_sentimientos())
            resumen = _formatear_resumen(obtener_resumen())
            return "\n\n".join([propagacion, sentimientos, resumen])

        if _requiere_propagacion(pregunta_normalizada):
            return _formatear_propagacion(obtener_propagacion())

        if _requiere_sentimientos(pregunta_normalizada):
            return _formatear_sentimientos(obtener_sentimientos())

        if _requiere_resumen(pregunta_normalizada):
            return _formatear_resumen(obtener_resumen())

        return (
            "Puedo ayudarte con sentimientos, resumen o propagacion. "
            "Pregunta por uno de esos analisis o pide un analisis completo."
        )
    except Exception as exc:
        return f"No pude completar la consulta del agente: {exc}"


if __name__ == "__main__":
    print(PROMPT_BASE)
    print()
    pregunta_usuario = input("Pregunta: ")
    print()
    print(responder(pregunta_usuario))
