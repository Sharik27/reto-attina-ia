from transformers import pipeline
from app.data_loader import load_data
from app.config import TEXT_COLUMN

# cargar modelo UNA sola vez (importante)
sentiment_pipeline = pipeline("sentiment-analysis")

def analizar_sentimientos():
    df = load_data()

    textos = df[TEXT_COLUMN].tolist()

    # limitar para pruebas (muy importante)
    textos = textos[:50]

    resultados = sentiment_pipeline(
        textos,
        truncation=True,
        max_length=512
    )

    # contar resultados
    conteo = {"POSITIVE": 0, "NEGATIVE": 0}

    for r in resultados:
        conteo[r["label"]] += 1

    total = len(resultados)

    return {
        "total": total,
        "positivo": conteo["POSITIVE"],
        "negativo": conteo["NEGATIVE"]
    }