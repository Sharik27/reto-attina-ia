from app.agent.conversational_agent import (
    _formatear_propagacion,
    _formatear_resumen,
    _formatear_sentimientos,
    responder as responder_basico,
)
from app.agent.planner import planear_tool_calls
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


def responder_con_tool_calling(pregunta, incluir_traza=False, guardar_traza=True):
    plan = planear_tool_calls(pregunta)
    traza = crear_traza(
        pregunta,
        plan,
        modo_ejecucion="tool_calling_deterministico",
    )

    if not plan:
        respuesta = responder_basico(pregunta)
        marcar_fallback(traza)
        finalizar_traza(traza)
        if guardar_traza:
            guardar_traza_jsonl(traza)
        return _con_traza(respuesta, traza, incluir_traza)

    try:
        bloques = []

        for tool_call in plan:
            nombre = tool_call["name"]
            executor = TOOL_EXECUTORS[nombre]
            formatter = TOOL_FORMATTERS[nombre]

            resultado = executor()
            registrar_tool(traza, tool_call, resultado)
            bloques.append(formatter(resultado))

        respuesta = "\n\n".join(bloques)
        finalizar_traza(traza)
        if guardar_traza:
            guardar_traza_jsonl(traza)
        return _con_traza(respuesta, traza, incluir_traza)
    except Exception as exc:
        registrar_error(traza, exc)
        marcar_fallback(traza)
        respuesta = responder_basico(pregunta)
        finalizar_traza(traza)
        if guardar_traza:
            guardar_traza_jsonl(traza)
        return _con_traza(respuesta, traza, incluir_traza)


def _con_traza(respuesta, traza, incluir_traza):
    if incluir_traza:
        return {
            "respuesta": respuesta,
            "traza": traza,
        }

    return respuesta


if __name__ == "__main__":
    pregunta_usuario = input("Pregunta: ")
    resultado = responder_con_tool_calling(pregunta_usuario, incluir_traza=True)

    print()
    print(resultado["respuesta"])
    print()
    print(formatear_traza(resultado["traza"]))
