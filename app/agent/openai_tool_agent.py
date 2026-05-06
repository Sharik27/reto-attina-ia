import os

from app.agent.conversational_agent import (
    _formatear_propagacion,
    _formatear_resumen,
    _formatear_sentimientos,
)
from app.agent.tool_calling_agent import responder_con_tool_calling
from app.agent.tools import obtener_propagacion, obtener_resumen, obtener_sentimientos


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
    if not os.getenv("OPENAI_API_KEY"):
        respuesta = responder_con_tool_calling(pregunta)
        return _con_traza(respuesta, _crear_traza(pregunta, fallback=True), incluir_traza)

    try:
        tool_calls = _pedir_tool_calls(pregunta)

        if not tool_calls:
            respuesta = responder_con_tool_calling(pregunta)
            return _con_traza(respuesta, _crear_traza(pregunta, fallback=True), incluir_traza)

        bloques = []
        tools_ejecutadas = []

        for tool_call in tool_calls:
            nombre = tool_call.function.name
            if nombre not in TOOL_EXECUTORS:
                continue

            resultado = TOOL_EXECUTORS[nombre]()
            tools_ejecutadas.append({
                "name": nombre,
                "args": tool_call.function.arguments,
                "resultado": resultado,
            })
            bloques.append(TOOL_FORMATTERS[nombre](resultado))

        if not bloques:
            respuesta = responder_con_tool_calling(pregunta)
            return _con_traza(respuesta, _crear_traza(pregunta, fallback=True), incluir_traza)

        respuesta = _resumir_respuesta("\n\n".join(bloques))
        traza = _crear_traza(pregunta, fallback=False, tools_ejecutadas=tools_ejecutadas)
        return _con_traza(respuesta, traza, incluir_traza)
    except Exception as exc:
        respuesta = responder_con_tool_calling(pregunta)
        traza = _crear_traza(pregunta, fallback=True, errores=[str(exc)])
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


def _crear_traza(pregunta, fallback, tools_ejecutadas=None, errores=None):
    return {
        "pregunta": pregunta,
        "modo": "openai_tool_calling",
        "modelo": os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
        "tools_ejecutadas": tools_ejecutadas or [],
        "errores": errores or [],
        "fallback_usado": fallback,
    }


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
    print("Trazabilidad:")
    print(resultado["traza"])
