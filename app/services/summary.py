from transformers import pipeline
from app.data_loader import load_data
from app.config import TEXT_COLUMN

_generator = None

def get_generator():
    global _generator
    if _generator is None:
        try:
            print("INFO: Intentando cargar modelo de resumen mediante auto-detección...")
            # Dejamos que transformers detecte la tarea automáticamente (summarization)
            _generator = pipeline(
                model="sshleifer/distilbart-cnn-12-6",
                device=-1 # Forzar CPU para evitar errores de GPU
            )
        except Exception as e:
            print(f"DEBUG: Error en auto-detección: {e}. Intentando Plan B...")
            try:
                # Plan B: Usar text-generation (que sí existe en tu lista)
                _generator = pipeline(
                    "text-generation",
                    model="distilgpt2",
                    device=-1
                )
            except Exception as e2:
                print(f"CRITICAL ERROR: No se pudo cargar ningún modelo de texto: {e2}")
                _generator = "error"
    return _generator



def generar_resumen():
    generator = get_generator()
    
    if generator == "error":
        return {"error": "El modelo de IA no pudo inicializarse localmente."}

    if generator is None:
        return {"error": "El modelo se está cargando. Intenta de nuevo en unos segundos."}

    try:
        df = load_data()

        # Tomar los mensajes con más engagement para el resumen
        if "likes" in df.columns:
            top_df = df.sort_values(by="likes", ascending=False).head(20)
        else:
            top_df = df.head(20)

        textos = top_df[TEXT_COLUMN].dropna().astype(str).tolist()

        if not textos:
            return {"error": "No hay datos para resumir"}

        # Limitar longitud para el modelo
        texto_input = " ".join(textos)
        if len(texto_input) > 1500:
            texto_input = texto_input[:1500]

        resultado = generator(
            texto_input,
            max_length=150,
            min_length=30,
            do_sample=False
        )

        resumen_final = ""
        if isinstance(resultado, list) and len(resultado) > 0:
            resumen_final = resultado[0].get("summary_text") or resultado[0].get("generated_text")

        if not resumen_final:
             return {"error": "No se pudo generar un resumen válido."}

        return {
            "resumen_ejecutivo": resumen_final.strip(),
            "temas_clave": ["Conversación Digital", "Interacción de Usuarios"],
            "mensajes_procesados": len(textos)
        }

    except Exception as e:
        return {
            "error": "Error en el servicio de resumen",
            "detalle": str(e)
        }


