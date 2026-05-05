from app.data_loader import load_data
from app.config import ID_COLUMN, PARENT_COLUMN

def analizar_propagacion():
    df = load_data()

    relaciones = df[[ID_COLUMN, PARENT_COLUMN]]

    return relaciones.head()