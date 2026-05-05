import pandas as pd
import os

from app.config import DATA_PATH, TEXT_COLUMN, TIME_COLUMN

_cached_df = None

def find_parquet_file():
    import os
    # 1. Probar ruta exacta del config
    if os.path.exists(DATA_PATH):
        return DATA_PATH
    
    # 2. Buscar cualquier .parquet en la raíz o en data/
    search_dirs = [".", "data"]
    for d in search_dirs:
        if os.path.exists(d):
            files = [f for f in os.listdir(d) if f.endswith(".parquet")]
            if files:
                return os.path.join(d, files[0])
    return DATA_PATH # fallback para que el error sea claro después

def load_data():
    global _cached_df
    if _cached_df is not None:
        return _cached_df

    target_path = DATA_PATH
    
    if not os.path.exists(target_path):
        # Fallback to look in root if not in data/
        root_path = os.path.basename(DATA_PATH)
        if os.path.exists(root_path):
            target_path = root_path
        else:
            raise FileNotFoundError(f"No se encontró el archivo {DATA_PATH}. Por favor verifica la carpeta data/.")

    print(f"DEBUG: Cargando datos desde {target_path}...")
    df = pd.read_parquet(target_path)

    # limpieza básica
    if TEXT_COLUMN in df.columns:
        df = df.dropna(subset=[TEXT_COLUMN])
        df[TEXT_COLUMN] = df[TEXT_COLUMN].astype(str)

    # convertir fechas si existe la columna
    if TIME_COLUMN in df.columns:
        df[TIME_COLUMN] = pd.to_datetime(df[TIME_COLUMN], unit='ms', errors='coerce')

    _cached_df = df
    return df
