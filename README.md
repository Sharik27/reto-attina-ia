# IA Reto Attina - Agente Conversacional

### Desarrolladores
* Sharik Camila Rueda
* Mariana De La Cruz
* Juan Camilo Molina
* Alexis Delgado
* Valentina Gomez

## Descripcion del proyecto

Este proyecto implementa un sistema de analisis de conversaciones digitales. El sistema expone servicios de analisis mediante FastAPI y construye un agente conversacional que consume esos servicios como herramientas (tools).

El proyecto incluye:

- Analisis de sentimientos.
- Generacion de resumen.
- Analisis de propagacion.
- Agente conversacional con Tool Calling hibrido.
- Tools HTTP conectadas a endpoints FastAPI.
- Observabilidad local mediante trazas estructuradas.

## Arquitectura

El sistema implementa un agente con **Tool Calling hibrido**, combinando un planner deterministico(basado en reglas) y un modelo LLM mediante OpenAI, con fallback para control de costos y estabilidad.

La arquitectura separa:

- Servicios analiticos en FastAPI.
- Tools HTTP que llaman los endpoints.
- Agente deterministico basado en reglas (sin costo).
- Agente opcional con OpenAI Tool Calling.
- Trazabilidad local para auditoria y debugging.

## Instalacion

### Crear entorno virtual

```bash
python -m venv venv
```

### Activar entorno (Windows - Git Bash)

```bash
source venv/Scripts/activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

## Configuracion

### Variable de entorno

```bash
export OPENAI_API_KEY="YOUR_API_KEY_HERE"
```

Esta variable es opcional. Si no se configura, el sistema usa el planner deterministico como fallback y puede funcionar sin conexion a OpenAI.

## Ejecucion del sistema

### Levantar API - Terminal 1

```bash
uvicorn app.api.main:app --reload
```
- Dejar esta terminal corriendo.
- La API expone los endpoints que consumen los agentes.

## Ejecutar el agente (Terminal 2)

Elegir uno de los siguientes modos de ejecución:

### Opción A: Agente determinístico (sin API Key)
```bash
python -m app.agent.tool_calling_agent
```
- No requiere conexión a OpenAI
- Usa un planner basado en reglas
- Recomendado como modo por defecto


### Opción B: Agente con OpenAI (Tool Calling real)

```bash
python -m app.agent.openai_tool_agent
```
- Requiere configurar `OPENAI_API_KEY`
- Usa un modelo LLM para decidir las tools
- Mantiene fallback automático al modo determinístico

## Ejemplos de uso

Preguntas sugeridas para probar el agente:

```text
muestrame sentimientos
```

```text
muestrame propagacion
```

```text
haz analisis completo
```

## Observabilidad

El sistema implementa observabilidad local mediante trazas estructuradas.

Cada ejecucion registra:

- duracion
- tools utilizadas
- modo de ejecucion
- uso de fallback

Las trazas se guardan en:

```text
logs/agent_traces.jsonl
```

Estas trazas permiten revisar ejecuciones del agente, depurar errores, auditar decisiones y analizar desempeno sin depender de herramientas externas.

## FinOps

El uso de OpenAI esta limitado y controlado, priorizando el planner deterministico como modo por defecto para reducir costos.

El sistema aplica estas medidas:

- OpenAI es opcional.
- Se usa un modelo economico cuando se habilita Tool Calling real.
- El agente mantiene fallback deterministico.
- No se requiere OpenAI para ejecutar el flujo base.

## Flujo del sistema

```text
Usuario -> Agente -> Tool Calling -> Tools -> API -> Respuesta + Traza
```

## Notas importantes

- La API debe estar siempre activa en una terminal independiente.
- Los agentes se ejecutan en otra terminal separada.
- Ambos agentes consumen los mismos endpoints HTTP.
- Si no hay API activa, los agentes no podrán funcionar correctamente.
- No subir API keys al repositorio.
- Reemplazar cualquier API key de ejemplo por `YOUR_API_KEY_HERE`.
- `logs/` esta ignorado en `.gitignore`.
- El sistema funciona sin conexion a OpenAI usando el planner deterministico.
