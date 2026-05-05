import pandas as pd
from app.config import DATA_PATH, TEXT_COLUMN, TIME_COLUMN

def load_data():
    df = pd.read_parquet(DATA_PATH)

    # limpieza básica
    df = df.dropna(subset=[TEXT_COLUMN])
    df[TEXT_COLUMN] = df[TEXT_COLUMN].astype(str)

    # convertir fechas
    fecha_numerica = pd.to_numeric(df[TIME_COLUMN], errors="coerce")
    valores_no_nulos = df[TIME_COLUMN].notna().sum()

    if fecha_numerica.notna().sum() == valores_no_nulos:
        max_value = fecha_numerica.dropna().max()
        unit = "ms" if max_value > 10_000_000_000 else "s"
        df[TIME_COLUMN] = pd.to_datetime(fecha_numerica, unit=unit, errors="coerce")
    else:
        df[TIME_COLUMN] = pd.to_datetime(df[TIME_COLUMN], errors="coerce")

    return df
