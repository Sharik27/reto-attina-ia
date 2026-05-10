from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from app.services.sentiment import analizar_sentimientos
from app.services.summary import generar_resumen
from app.services.propagation import analizar_propagacion

app = FastAPI(title="Atinna Analytics API", version="1.0.0")

# Permitir peticiones desde la interfaz web local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir la carpeta UI
app.mount("/ui", StaticFiles(directory="ui"), name="ui")

# --- Endpoints de análisis individuales (MCPs) ---

@app.get("/")
def home():
    return {"mensaje": "Atinna Analytics API funcionando", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/analisis/sentimientos")
def sentimientos():
    return {"resultado": analizar_sentimientos()}

@app.get("/analisis/resumen")
def resumen():
    return {"resultado": generar_resumen()}

@app.get("/analisis/propagacion")
def propagacion():
    return {"resultado": analizar_propagacion()}

# --- Endpoint de Chat (Agente Conversacional) ---

class ChatRequest(BaseModel):
    pregunta: str
    modo: str = "basico"  # "basico" o "inteligente"

@app.post("/chat")
def chat(request: ChatRequest):
    from app.agent.conversational_agent import responder
    respuesta = responder(request.pregunta, modo=request.modo)
    return {
        "pregunta": request.pregunta,
        "modo": request.modo,
        "respuesta": respuesta,
    }
