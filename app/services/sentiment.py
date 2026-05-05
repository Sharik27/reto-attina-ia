from transformers import pipeline
from app.data_loader import load_data
from app.config import TEXT_COLUMN

# Cargar modelo local
sentiment_pipeline = pipeline("sentiment-analysis")

def analizar_sentimientos():
    try:
        df = load_data()
        # Analizar una muestra representativa
        sample_size = min(len(df), 200)
        sample_df = df.sample(sample_size)

        textos = sample_df[TEXT_COLUMN].dropna().astype(str).tolist()

        if not textos:
            return {"error": "No hay datos disponibles para análisis."}

        resultados = sentiment_pipeline(textos, truncation=True, max_length=512)

        conteo = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
        for r in resultados:
            label = r["label"].upper()
            if label in conteo:
                conteo[label] += 1
            else:
                conteo["NEUTRAL"] += 1

        clima = "Positivo" if conteo["POSITIVE"] > conteo["NEGATIVE"] else "Negativo"
        if abs(conteo["POSITIVE"] - conteo["NEGATIVE"]) < (sample_size * 0.1):
            clima = "Neutral/Mixto"

        return {
            "total_analizado": len(resultados),
            "conteo": conteo,
            "clima_general": clima,
            "confianza_promedio": sum([r['score'] for r in resultados]) / len(resultados) if resultados else 0
        }

    except Exception as e:
        return {"error": "Error en el servicio de sentimientos", "detalle": str(e)}


