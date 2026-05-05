from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from app.services.sentiment import analizar_sentimientos
from app.services.summary import generar_resumen
from app.services.propagation import analizar_propagacion
from app.agent.core import AtinnaAgent

app = FastAPI(title="Atinna AI API", description="Microservicios para el Reto ICESI de Análisis de Conversaciones")
agent = AtinnaAgent()

@app.get("/")
def home():
    return FileResponse("static/index.html")

# --- Endpoints de Servicios MCP ---

@app.get("/analisis/sentimientos")
def get_sentimientos():
    """Servicio MCP #1: Análisis de Clima Semántico"""
    return analizar_sentimientos()

@app.get("/analisis/resumen")
def get_resumen():
    """Servicio MCP #2: Resumen Ejecutivo de la Conversación"""
    return generar_resumen()

@app.get("/analisis/propagacion")
def get_propagacion(message_id: str = Query(None, description="ID del mensaje a analizar")):
    """Servicio MCP #3 (OBLIGATORIO): Análisis de Propagación y Alcance"""
    return analizar_propagacion(message_id)

# --- Endpoint del Agente ---

@app.get("/api/agent/chat")
async def chat(query: str):
    """Agente Conversacional con Tool-Calling (LangGraph)"""
    try:
        response = await agent.process_query(query)
        return {"response": response}
    except Exception as e:
        return {"response": f"Lo siento, ocurrió un error interno: {str(e)}"}

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)