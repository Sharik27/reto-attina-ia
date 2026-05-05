from transformers import pipeline
from app.data_loader import load_data

# Inicializar el modelo (compatible con tu versión)
try:
    generator = pipeline(
        "text-generation",
        model="sshleifer/distilbart-cnn-12-6"
    )
except Exception as e:
    print(f"Error cargando modelo: {e}")
    generator = None


def generar_resumen():
    if generator is None:
        return {"error": "El modelo no se pudo cargar"}

    try:
        df = load_data()

        # Tomar solo algunos textos (para evitar sobrecarga)
        textos = df["text"].dropna().astype(str).tolist()[:5]

        if not textos:
            return {"error": "No hay datos para resumir"}

        texto_completo = " ".join(textos)

        # ⚠️ IMPORTANTE: limitar tamaño (los modelos no aceptan texto infinito)
        texto_completo = texto_completo[:1000]

        prompt = f"Resume el siguiente texto:\n{texto_completo}"

        resultado = generator(
            prompt,
            max_length=150,
            do_sample=False
        )

        resumen = resultado[0]["generated_text"]

        return {
            "resumen": resumen
        }

    except Exception as e:
        return {
            "error": "No se pudo generar el resumen",
            "detalle": str(e)
        }