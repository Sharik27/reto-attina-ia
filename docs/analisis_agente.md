# Analisis del Agente

## Prompt engineering

El agente usa instrucciones base para definir su comportamiento:

- responder en espanol
- usar herramientas cuando sean necesarias
- no inventar metricas
- explicar fallos de herramientas
- mantener respuestas concretas

El prompt base esta en `app/agent/prompts.py`. En el modo OpenAI, el mensaje de sistema indica que el modelo debe elegir la herramienta mas adecuada y responder en espanol.

## ReAct vs Tool Calling

### ReAct

ReAct combina razonamiento, accion y observacion.

Ejemplo conceptual:

```text
Thought: El usuario pregunta por propagacion.
Action: analizar_propagacion
Observation: Hay varios hilos activos.
Final: La conversacion se propago principalmente...
```

ReAct es util cuando un LLM razona en varias etapas, pero puede aumentar costo y complejidad.

### Tool Calling

Tool Calling usa llamadas estructuradas a herramientas.

Ejemplo:

```json
{
  "name": "analizar_sentimientos",
  "args": {},
  "reason": "La pregunta menciona sentimientos negativos."
}
```

En este proyecto Tool Calling ya existe en dos formas:

- deterministica: `planner.py`
- real con LLM: `openai_tool_agent.py`

Se recomienda Tool Calling sobre ReAct para esta demo porque es mas controlado, auditable y compatible con los endpoints HTTP.

## Design patterns

### Planning

Implementado en `planner.py`. Decide que tools ejecutar segun la pregunta.

### Tool Use

Implementado en `tools.py`. Las tools llaman endpoints HTTP y no servicios internos.

### Sequential Workflow

Implementado cuando el usuario pide un analisis completo:

```text
propagacion -> sentimientos -> resumen
```

### Human-in-the-Loop

Aplicado como regla de trabajo: antes de modificar archivos o hacer cambios importantes, se pide autorizacion explicita.

### Reflection

No se implementa todavia. Podria agregarse para que el agente revise su respuesta antes de entregarla.

### Multi-Agent Collaboration

No se implementa todavia. Podria aplicarse con agentes especializados en analisis, evaluacion y costos.

## Observabilidad

La observabilidad permite revisar:

- prompts
- tools ejecutadas
- errores
- latencia
- costos
- calidad de respuesta

Actualmente existe una observabilidad minima:

- `trace.py`: registra pregunta, plan, tools ejecutadas, errores y fallback.
- `openai_tool_agent.py`: puede devolver una traza local con modo, modelo, tools y errores.

Herramientas futuras:

- LangSmith: recomendable si se adopta LangChain.
- Langfuse: util para trazas, costos y prompts sin depender totalmente de LangChain.
- Phoenix Arize: util si se agregan embeddings, RAG o analisis mas profundo.
- Ragas: util para evaluacion formal de respuestas, especialmente en sistemas RAG.

No se implementan todavia para evitar dependencias externas y mantener compatibilidad con Python 3.13.

## LangChain

LangChain queda como alternativa futura. El sistema actual no lo necesita porque ya tiene:

- definicion de tools
- planner
- tool calling real con OpenAI
- trazas simples

Mapeo posible:

| Proyecto actual | LangChain |
| --- | --- |
| `tool_specs.py` | definicion de tools |
| `tools.py` | funciones ejecutables |
| `prompts.py` | prompt template |
| `tool_calling_agent.py` | agent executor |
| `openai_tool_agent.py` | modelo con tool calling |
| `trace.py` | callbacks/tracing |

Se podria integrar despues si se necesita mas estandarizacion o trazabilidad.

## Governance y CrewAI

CrewAI permite crear equipos de agentes con roles definidos, por ejemplo:

- agente analista
- agente evaluador
- agente financiero
- agente supervisor

No se implementa porque el proyecto actual solo requiere un agente conversacional. Agregar CrewAI aumentaria complejidad y costo sin ser necesario para la demo actual.

La governance actual se expresa en:

- fallback deterministico
- control de llamadas a OpenAI
- separacion entre agente y servicios
- autorizacion humana antes de cambios

## Memoria de largo plazo

Tipos de memoria posibles:

- Buffer memory: guarda mensajes recientes.
- Summary memory: guarda resumen de conversaciones.
- Entity memory: guarda entidades relevantes.
- Vector memory: permite busqueda semantica con embeddings.

No se implementa memoria todavia. La recomendacion es:

1. empezar con memoria de sesion
2. agregar summary memory si las conversaciones crecen
3. usar vector memory solo si se necesitan consultas historicas complejas

## FinOps

FinOps busca controlar el costo de la tecnologia.

La arquitectura actual aplica FinOps porque tiene dos modos:

- planner deterministico: costo cero de API
- OpenAI Tool Calling: uso opcional y controlado

Medidas de control:

- modelo economico `gpt-4o-mini`
- maximo una llamada LLM por pregunta
- limite de tokens
- `temperature=0`
- fallback automatico sin API key
- no hacer pruebas masivas

Comparacion:

| Opcion | Costo variable | Ventaja | Riesgo |
| --- | --- | --- | --- |
| Tool Calling deterministico | Bajo | Gratis y estable | No hay decision LLM |
| OpenAI Tool Calling | Medio/controlado | Decision real por LLM | Costo por tokens |
| Hugging Face local | Bajo | Sin API paga | Consumo local alto |
| Ollama local | Bajo/medio | LLM local | Instalacion y hardware |
| LangSmith/Langfuse | Variable | Observabilidad | Configuracion externa |

## Transfer learning y destilacion LLM

Transfer learning consiste en adaptar un modelo preentrenado a una tarea especifica. Podria aplicarse a:

- sentimiento en conversaciones digitales
- deteccion de temas
- clasificacion de riesgo

No se implementa porque requiere dataset etiquetado, entrenamiento, validacion y recursos computacionales.

La destilacion LLM usa un modelo grande como teacher y uno mas pequeno como student. Puede reducir costo y latencia, pero agregaria un pipeline de entrenamiento y evaluacion.

Para esta demo se justifica no implementarlo porque el objetivo principal es demostrar servicios de analisis y agentes con tools, no entrenar modelos.

## Conclusion

El agente combina implementacion practica y decisiones academicas defendibles:

- Tool Calling deterministico para estabilidad y costo cero.
- Tool Calling real con OpenAI para demostrar decision por LLM.
- Fallback automatico para resiliencia.
- Observabilidad minima sin dependencias externas.
- Documentacion de temas avanzados sin sobrecomplicar el proyecto.
