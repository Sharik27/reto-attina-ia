import os

from app.agent.conversational_agent import (
    _formatear_propagacion,
    _formatear_resumen,
    _formatear_sentimientos,
)
from app.agent.tool_calling_agent import responder_con_tool_calling
from app.agent.tools import obtener_propagacion, obtener_resumen, obtener_sentimientos
from app.agent.trace import (
    crear_traza,
    finalizar_traza,
    formatear_traza,
    guardar_traza_jsonl,
    marcar_fallback,
    registrar_error,
    registrar_tool,
)


DEFAULT_MODEL = "gpt-4o-mini"
MAX_TOKENS = 120

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "analizar_sentimientos",
            "description": "Obtiene el analisis de sentimientos de la conversacion.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generar_resumen",
            "description": "Genera un resumen breve de la conversacion.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analizar_propagacion",
            "description": "Analiza propagacion, hilos, profundidad y respuestas de la conversacion.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
]

TOOL_EXECUTORS = {
    "analizar_sentimientos": obtener_sentimientos,
    "generar_resumen": obtener_resumen,
    "analizar_propagacion": obtener_propagacion,
}

TOOL_FORMATTERS = {
    "analizar_sentimientos": _formatear_sentimientos,
    "generar_resumen": _formatear_resumen,
    "analizar_propagacion": _formatear_propagacion,
}


def responder_con_openai_tool_calling(pregunta, incluir_traza=False):
    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    traza = crear_traza(
        pregunta,
        modo_ejecucion="openai_tool_calling",
        modelo=model,
    )

    if not os.getenv("OPENAI_API_KEY"):
        registrar_error(traza, "OPENAI_API_KEY no configurada; se usa fallback deterministico.")
        marcar_fallback(traza)
        respuesta = responder_con_tool_calling(pregunta, guardar_traza=False)
        finalizar_traza(traza)
        guardar_traza_jsonl(traza)
        return _con_traza(respuesta, traza, incluir_traza)

    try:
        tool_calls = _pedir_tool_calls(pregunta)

        if not tool_calls:
            registrar_error(traza, "OpenAI no solicito ninguna herramienta; se usa fallback deterministico.")
            marcar_fallback(traza)
            respuesta = responder_con_tool_calling(pregunta, guardar_traza=False)
            finalizar_traza(traza)
            guardar_traza_jsonl(traza)
            return _con_traza(respuesta, traza, incluir_traza)

        bloques = []

        for tool_call in tool_calls:
            nombre = tool_call.function.name
            if nombre not in TOOL_EXECUTORS:
                continue

            resultado = TOOL_EXECUTORS[nombre]()
            registrar_tool(traza, {
                "name": nombre,
                "args": tool_call.function.arguments,
                "reason": "Tool solicitada por OpenAI.",
            }, resultado)
            bloques.append(TOOL_FORMATTERS[nombre](resultado))

        if not bloques:
            registrar_error(traza, "No se ejecuto ninguna herramienta valida; se usa fallback deterministico.")
            marcar_fallback(traza)
            respuesta = responder_con_tool_calling(pregunta, guardar_traza=False)
            finalizar_traza(traza)
            guardar_traza_jsonl(traza)
            return _con_traza(respuesta, traza, incluir_traza)

        respuesta = _resumir_respuesta("\n\n".join(bloques))
        finalizar_traza(traza)
        guardar_traza_jsonl(traza)
        return _con_traza(respuesta, traza, incluir_traza)
    except Exception as exc:
        registrar_error(traza, exc)
        marcar_fallback(traza)
        respuesta = responder_con_tool_calling(pregunta, guardar_traza=False)
        finalizar_traza(traza)
        guardar_traza_jsonl(traza)
        return _con_traza(respuesta, traza, incluir_traza)


def _pedir_tool_calls(pregunta):
    from openai import OpenAI

    client = OpenAI()
    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un agente de analisis de conversaciones digitales. "
                    "Elige la herramienta mas adecuada. Si el usuario pide un analisis completo, "
                    "puedes llamar las tres herramientas. Responde siempre en espanol."
                ),
            },
            {"role": "user", "content": pregunta},
        ],
        tools=TOOL_DEFINITIONS,
        tool_choice="auto",
        temperature=0,
        max_tokens=MAX_TOKENS,
    )

    message = response.choices[0].message
    return message.tool_calls or []


def _resumir_respuesta(texto):
    lineas = [linea.strip() for linea in texto.splitlines() if linea.strip()]
    return "\n".join(lineas[:12])


def _con_traza(respuesta, traza, incluir_traza):
    if incluir_traza:
        return {
            "respuesta": respuesta,
            "traza": traza,
        }

    return respuesta


if __name__ == "__main__":
    pregunta_usuario = input("Pregunta: ")
    resultado = responder_con_openai_tool_calling(pregunta_usuario, incluir_traza=True)

    print()
    print(resultado["respuesta"])
    print()
    print(formatear_traza(resultado["traza"]))
