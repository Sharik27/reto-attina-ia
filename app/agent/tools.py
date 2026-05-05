from langchain_core.tools import tool
from app.services.sentiment import analizar_sentimientos
from app.services.summary import generar_resumen
from app.services.propagation import analizar_propagacion

@tool
def get_sentiment_analysis():
    """Realiza un análisis de sentimientos de la conversación digital para conocer el clima general (positivo, negativo o neutral)."""
    return analizar_sentimientos()

@tool
def get_summary_analysis():
    """Genera un resumen ejecutivo de la conversación, identificando los temas principales y posturas clave."""
    return generar_resumen()

@tool
def get_propagation_analysis(message_id: str = None):
    """
    Analiza cómo se ha propagado un mensaje específico en la red. 
    Mide el alcance, la velocidad y el impacto mediático.
    Si no se proporciona un ID, busca el mensaje más viral.
    """
    return analizar_propagacion(message_id)


