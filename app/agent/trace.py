import json
import os
import time
from datetime import datetime, timezone


def crear_traza(pregunta, plan=None, modo_ejecucion="tool_calling_deterministico", modelo=None):
    return {
        "pregunta": pregunta,
        "timestamp_inicio": _ahora_iso(),
        "timestamp_fin": None,
        "duracion_ms": None,
        "modo_ejecucion": modo_ejecucion,
        "modelo": modelo,
        "plan": plan or [],
        "tools_ejecutadas": [],
        "numero_tools": 0,
        "resumen_tools": [],
        "errores": [],
        "fallback_usado": False,
        "_inicio_perf": time.perf_counter(),
    }


def registrar_tool(traza, tool_call, resultado):
    nombre = tool_call["name"]
    traza["tools_ejecutadas"].append({
        "name": nombre,
        "args": tool_call.get("args", {}),
        "reason": tool_call.get("reason", ""),
        "status": "ok",
    })
    traza["numero_tools"] = len(traza["tools_ejecutadas"])
    traza["resumen_tools"] = [tool["name"] for tool in traza["tools_ejecutadas"]]
    return traza


def registrar_error(traza, error):
    traza["errores"].append(str(error))
    return traza


def marcar_fallback(traza):
    traza["fallback_usado"] = True
    return traza


def finalizar_traza(traza):
    traza["timestamp_fin"] = _ahora_iso()
    inicio = traza.get("_inicio_perf")
    if inicio is not None:
        traza["duracion_ms"] = round((time.perf_counter() - inicio) * 1000, 2)

    traza["numero_tools"] = len(traza.get("tools_ejecutadas", []))
    traza["resumen_tools"] = [
        tool.get("name")
        for tool in traza.get("tools_ejecutadas", [])
        if tool.get("name")
    ]
    traza.pop("_inicio_perf", None)
    return traza


def formatear_traza(traza):
    lineas = [
        "Trazabilidad local:",
        f"- Modo: {traza.get('modo_ejecucion')}",
        f"- Modelo: {traza.get('modelo') or 'no aplica'}",
        f"- Inicio: {traza.get('timestamp_inicio')}",
        f"- Fin: {traza.get('timestamp_fin')}",
        f"- Duracion: {traza.get('duracion_ms')} ms",
        f"- Tools ejecutadas: {traza.get('numero_tools', 0)}",
        f"- Resumen tools: {', '.join(traza.get('resumen_tools') or []) or 'ninguna'}",
        f"- Fallback usado: {traza.get('fallback_usado')}",
    ]

    errores = traza.get("errores") or []
    if errores:
        lineas.append("- Errores:")
        lineas.extend(f"  - {error}" for error in errores)

    return "\n".join(lineas)


def guardar_traza_jsonl(traza, ruta="logs/agent_traces.jsonl"):
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    traza_segura = _sin_campos_privados(traza)
    with open(ruta, "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(traza_segura, ensure_ascii=False) + "\n")

    return ruta


def _ahora_iso():
    return datetime.now(timezone.utc).isoformat()


def _sin_campos_privados(valor):
    if isinstance(valor, dict):
        return {
            clave: _sin_campos_privados(contenido)
            for clave, contenido in valor.items()
            if not clave.startswith("_") and "api_key" not in clave.lower()
        }

    if isinstance(valor, list):
        return [_sin_campos_privados(item) for item in valor]

    return valor
