from openai import OpenAI
from app.config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL
from app.agent.conversational_agent import (
    _formatear_propagacion,
    _formatear_resumen,
    _formatear_sentimientos,
)
from app.agent.tools import obtener_propagacion, obtener_resumen, obtener_sentimientos
from app.agent.trace import (
    crear_traza,
    finalizar_traza,
    registrar_tool,
    registrar_error,
    guardar_traza_jsonl,
)

# Modelo recomendado por Groq para Tool Calling (Mayo 2026)
TOOL_CALLING_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# Schema correcto para Groq: funciones sin parámetros requieren "required": []
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "analizar_sentimientos",
            "description": (
                "Analiza los datos del dataset de conversaciones de Atinna para determinar "
                "cuántos mensajes son positivos y cuántos negativos. Úsala cuando el usuario "
                "pregunte por sentimientos, ánimos, polaridad o el clima de la conversación."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generar_resumen",
            "description": (
                "Genera un resumen de los temas principales del dataset de conversaciones. "
                "Úsala cuando el usuario pida un resumen, síntesis o quiera saber de qué trata la discusión."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analizar_propagacion",
            "description": (
                "Extrae métricas de propagación del dataset: hilos activos, profundidad de respuestas, "
                "alcance y viralidad. Úsala cuando el usuario pregunte sobre la estructura de la conversación, "
                "hilos o qué tan viral fue un mensaje."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
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

SYSTEM_PROMPT = (
    "Eres Atinna-Analyst, un asistente especializado en analizar conversaciones digitales. "
    "Tienes acceso a herramientas que analizan un dataset real de conversaciones. "
    "Cuando el usuario pregunte sobre sentimientos, resumen o propagación, SIEMPRE debes "
    "llamar a la herramienta correspondiente antes de responder. "
    "Después de obtener los datos, explícalos de forma clara y profesional en español."
)


def responder_con_groq(pregunta, incluir_traza=False):
    if not GROQ_API_KEY:
        return "Error: No se ha configurado la GROQ_API_KEY en config.py"

    client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)
    traza = crear_traza(pregunta, modo_ejecucion="groq_tool_calling", modelo=TOOL_CALLING_MODEL)

    try:
        # 1. El LLM decide qué herramientas usar
        response = client.chat.completions.create(
            model=TOOL_CALLING_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": pregunta},
            ],
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )

        message = response.choices[0].message
        tool_calls = message.tool_calls

        # Si el modelo no usó herramientas, le respondemos de todas formas
        if not tool_calls:
            return message.content or "No pude identificar qué análisis necesitas. Prueba con: sentimientos, resumen o propagación."

        # 2. Ejecutamos cada herramienta que el LLM decidió usar
        tool_outputs = []
        for tool_call in tool_calls:
            nombre = tool_call.function.name
            if nombre in TOOL_EXECUTORS:
                resultado = TOOL_EXECUTORS[nombre]()
                registrar_tool(traza, {"name": nombre}, resultado)
                tool_outputs.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": nombre,
                    "content": str(resultado),
                })

        if not tool_outputs:
            return "No pude ejecutar ninguna herramienta válida."

        # 3. El LLM genera la respuesta final en lenguaje natural
        final_response = client.chat.completions.create(
            model=TOOL_CALLING_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": pregunta},
                message,
                *tool_outputs,
            ],
        )

        respuesta_final = final_response.choices[0].message.content
        finalizar_traza(traza)
        guardar_traza_jsonl(traza)

        if incluir_traza:
            return {"respuesta": respuesta_final, "traza": traza}
        return respuesta_final

    except Exception as e:
        registrar_error(traza, str(e))
        return f"Error en el agente de Groq: {e}"
