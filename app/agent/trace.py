def crear_traza(pregunta, plan):
    return {
        "pregunta": pregunta,
        "plan": plan,
        "tools_ejecutadas": [],
        "errores": [],
        "fallback_usado": False,
    }


def registrar_tool(traza, tool_call, resultado):
    traza["tools_ejecutadas"].append({
        "name": tool_call["name"],
        "args": tool_call.get("args", {}),
        "reason": tool_call.get("reason", ""),
        "resultado": resultado,
    })
    return traza


def registrar_error(traza, error):
    traza["errores"].append(str(error))
    return traza


def marcar_fallback(traza):
    traza["fallback_usado"] = True
    return traza
