# 🧠 Reto ICESI — Atinna Analytics Agent

Sistema de análisis de conversaciones digitales con Agente Conversacional inteligente. Desarrollado para el reto de ICESI sobre **LLM/NLP y Agentes Conversacionales**.

---

## 📋 Descripción

Este proyecto expone tres microservicios de análisis (MCPs) sobre un dataset de conversaciones digitales en formato Parquet, y los integra con un **Agente Conversacional** que decide qué herramienta llamar según la pregunta del usuario.

---

## ⚙️ Servicios MCP Implementados

| Servicio | Endpoint | Descripción |
|---|---|---|
| Análisis de Sentimientos | `GET /analisis/sentimientos` | Clasifica mensajes en positivos/negativos usando HuggingFace Transformers |
| Resumen de Conversación | `GET /analisis/resumen` | Genera un resumen de los temas principales usando `distilbart-cnn-12-6` |
| Análisis de Propagación *(Obligatorio)* | `GET /analisis/propagacion` | Analiza hilos, profundidad, alcance y viralidad de mensajes |
| Chat con el Agente | `POST /chat` | Punto de entrada del Agente Conversacional (soporta modo básico e inteligente) |

---

## 🤖 Modos del Agente

El sistema soporta **dos modos de operación**:

### Modo 1 — Básico (Determinístico)
- No requiere API Key.
- Usa un **planner basado en palabras clave** para identificar la intención del usuario.
- Llama directamente a los servicios de análisis y devuelve los resultados formateados.
- Implementado en: `app/agent/conversational_agent.py`

### Modo 2 — Inteligente (LLM / Tool-Calling)
- Requiere una **API Key de Groq** (gratuita en [console.groq.com](https://console.groq.com/keys)).
- Usa **Llama 4 Scout** en Groq con **Tool Calling** real para razonar sobre la intención del usuario.
- El LLM recibe el Schema de las herramientas disponibles, decide cuáles llamar y genera una respuesta natural en español.
- Implementado en: `app/agent/groq_agent.py`

---

## 🚀 Instalación y Uso

### 1. Clonar el repositorio e instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. (Opcional) Configurar API Key de Groq para el modo inteligente

Edita `app/config.py` y añade tu clave:

```python
GROQ_API_KEY = "tu_api_key_aqui"
```

Consigue tu key gratuita en: https://console.groq.com/keys

### 3. Colocar el dataset

Asegúrate de que el archivo Parquet esté en:

```
data/Reto_data_20251023_122206.parquet
```

### 4. Levantar la API

```bash
python -m uvicorn app.api.main:app --reload
```

La API estará disponible en: `http://localhost:8000`

### 5. Usar el Agente por consola

```bash
python -m app.agent.conversational_agent
```

Verás un menú para elegir entre Modo 1 (básico) o Modo 2 (inteligente con Groq).

### 6. Interfaz Web

Abre el archivo `ui/index.html` directamente en el navegador. Asegúrate de que la API esté corriendo en el puerto 8000.

---

## 🗂️ Estructura del Proyecto

```
reto-attina-ia/
├── app/
│   ├── api/
│   │   └── main.py              # FastAPI — Endpoints REST (MCPs + Chat)
│   ├── agent/
│   │   ├── conversational_agent.py  # Agente determinístico + selector de modo
│   │   ├── groq_agent.py            # Agente inteligente con Groq Tool Calling
│   │   ├── tool_calling_agent.py    # Agente tool-calling determinístico
│   │   ├── planner.py               # Planner de intenciones
│   │   ├── tools.py                 # Wrappers de herramientas
│   │   ├── tool_specs.py            # Especificaciones de herramientas
│   │   ├── prompts.py               # Prompts base del agente
│   │   └── trace.py                 # Trazabilidad de ejecución
│   ├── services/
│   │   ├── sentiment.py     # Servicio de análisis de sentimientos
│   │   ├── summary.py       # Servicio de resumen
│   │   └── propagation.py   # Servicio de análisis de propagación
│   ├── data_loader.py       # Carga del dataset Parquet
│   └── config.py            # Configuración global (columnas, rutas, API Keys)
├── ui/
│   └── index.html           # Interfaz web de chat
├── data/
│   └── Reto_data_20251023_122206.parquet
├── docs/
├── test/
└── requirements.txt
```

---

## 🛠️ Stack Tecnológico

- **Backend**: Python, FastAPI, Uvicorn
- **IA/NLP**: HuggingFace Transformers, PyTorch
- **LLM (Modo Inteligente)**: Groq Cloud — Llama 4 Scout (`meta-llama/llama-4-scout-17b-16e-instruct`)
- **Datos**: Pandas, PyArrow (Parquet)
- **Interfaz**: HTML5, CSS3, JavaScript (Vanilla)

---

## 📊 Criterios del Reto Cubiertos

| Criterio | Estado |
|---|---|
| 3 Servicios MCP funcionales (Sentimientos, Resumen, Propagación) | ✅ |
| Agente Conversacional con identificación de intención | ✅ |
| Tool-Calling con LLM real (Groq) | ✅ |
| Respuesta natural generada por el LLM | ✅ |
| Interfaz de demo (web + terminal) | ✅ |
| Framework avanzado para puntos extra | ✅ (Groq Tool Calling) |
