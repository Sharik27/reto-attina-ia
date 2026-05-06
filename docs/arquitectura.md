# Arquitectura del Sistema

## Descripcion general

El proyecto implementa un sistema de analisis de conversaciones digitales. La base del sistema esta en FastAPI y expone tres servicios principales:

- Analisis de sentimientos: `/analisis/sentimientos`
- Resumen: `/analisis/resumen`
- Propagacion: `/analisis/propagacion`

Sobre estos servicios se construye un agente conversacional en `app/agent/`. El agente no reemplaza los endpoints de Fase 2; los consume como herramientas externas mediante HTTP.

## Arquitectura general

La arquitectura separa servicios de analisis y agente conversacional:

```text
Usuario
  -> Agente conversacional
  -> Tools HTTP
  -> Endpoints FastAPI
  -> Servicios de analisis
  -> Respuesta natural
```

Componentes principales:

- `app/api/main.py`: expone los endpoints FastAPI.
- `app/services/sentiment.py`: calcula sentimientos.
- `app/services/summary.py`: genera resumen.
- `app/services/propagation.py`: calcula metricas de propagacion.
- `app/agent/tools.py`: llama los endpoints HTTP.
- `app/agent/tool_specs.py`: define el catalogo formal de tools.
- `app/agent/planner.py`: decide tools con reglas.
- `app/agent/tool_calling_agent.py`: ejecuta Tool Calling deterministico.
- `app/agent/openai_tool_agent.py`: ejecuta Tool Calling real con OpenAI.
- `app/agent/trace.py`: registra trazas simples.

## Flujo del agente

El flujo principal es:

```text
Pregunta del usuario
  -> seleccion de modo
  -> decision de tool
  -> llamada HTTP al endpoint
  -> formateo de respuesta
  -> respuesta final
```

Ejemplo:

```text
"Como se propago el mensaje?"
  -> analizar_propagacion
  -> GET /analisis/propagacion
  -> respuesta con hilos, profundidad y nodos respondidos
```

Cuando el usuario pide un analisis completo, el sistema ejecuta un flujo secuencial:

```text
analizar_propagacion
analizar_sentimientos
generar_resumen
```

## Tool Calling hibrido

La arquitectura actual es hibrida.

### Modo 1: Tool Calling deterministico

El modo deterministico usa `planner.py`. La decision se toma con reglas y palabras clave.

Ventajas:

- no consume API paga
- es estable
- es facil de auditar
- funciona como fallback

Ejemplo de tool call:

```json
{
  "name": "analizar_propagacion",
  "args": {},
  "reason": "La pregunta menciona propagacion, hilos, profundidad o respuestas."
}
```

### Modo 2: Tool Calling real con OpenAI

El modo OpenAI esta en `openai_tool_agent.py`. Usa `OPENAI_API_KEY` desde variable de entorno y `gpt-4o-mini` como modelo economico.

Caracteristicas:

- no guarda la API key en archivos
- no llama al modelo al importar modulos
- usa maximo una llamada LLM por pregunta
- limita tokens
- usa `temperature=0`
- ejecuta las mismas tools HTTP
- vuelve al planner deterministico si no hay API key o si ocurre un error

## Evolucion del sistema

Primero se implemento el planner deterministico para demostrar Tool Use y Planning sin costo. Despues se agrego Tool Calling real con OpenAI para permitir que un LLM decida que herramienta usar.

El planner se mantiene porque aporta:

- resiliencia
- costo cero
- fallback automatico
- estabilidad para demo academica

La arquitectura no asume que todo sea LLM. Combina reglas y LLM opcional.

## MCP

MCP significa Model Context Protocol. En el proyecto no se implementa todavia un servidor MCP formal, pero la arquitectura ya sigue una idea compatible: el agente consume herramientas externas con interfaces claras.

Equivalencia actual:

| Servicio | Endpoint | Tool |
| --- | --- | --- |
| Sentimientos | `/analisis/sentimientos` | `analizar_sentimientos` |
| Resumen | `/analisis/resumen` | `generar_resumen` |
| Propagacion | `/analisis/propagacion` | `analizar_propagacion` |

Para implementar MCP formal haria falta:

- crear un servidor MCP
- registrar las tres herramientas
- definir schemas de entrada y salida
- conectar un cliente MCP desde el agente

No se implementa por ahora para evitar complejidad adicional.

## Microservicios

Los servicios de Fase 2 funcionan como modulos independientes detras de endpoints HTTP. Esto se acerca a una arquitectura de microservicios ligera:

- cada analisis tiene una responsabilidad clara
- el agente consume servicios por HTTP
- los servicios pueden evolucionar sin cambiar el agente, mientras mantengan el contrato

Esta separacion ayuda a no romper los endpoints actuales y permite agregar nuevos agentes o integraciones en el futuro.

## A2A como evolucion futura

A2A significa Agent-to-Agent. Podria usarse si el sistema crece a multiples agentes:

```text
Agente principal
  -> Agente analista
  -> Agente evaluador
  -> Agente FinOps
```

No se implementa todavia porque el proyecto actual solo necesita un agente conversacional. Se deja como extension futura para Multi-Agent Collaboration.
