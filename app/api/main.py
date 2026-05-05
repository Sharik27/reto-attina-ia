from fastapi import FastAPI
from app.services.sentiment import analizar_sentimientos
from app.services.summary import generar_resumen
from app.services.propagation import analizar_propagacion

app = FastAPI()

@app.get("/")
def home():
    return {"mensaje": "API funcionando"}

@app.get("/analisis/sentimientos")
def sentimientos():
    return {"resultado": analizar_sentimientos()}

@app.get("/analisis/resumen")
def resumen():
    return {"resultado": generar_resumen()}

@app.get("/analisis/propagacion")
def propagacion():
    return {"resultado": analizar_propagacion()}
