from fastapi import FastAPI
from app.services.sentimientos import analizar_sentimientos

app = FastAPI()

@app.get("/")
def home():
    return {"mensaje": "API funcionando"}

@app.get("/analisis/sentimientos")
def sentimientos():
    return {"resultado": analizar_sentimientos()}