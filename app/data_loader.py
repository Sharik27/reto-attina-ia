import pandas as pd
from app.config import DATA_PATH, TEXT_COLUMN, TIME_COLUMN

def load_data():
    df = pd.read_parquet(DATA_PATH)

    # limpieza básica
    df = df.dropna(subset=[TEXT_COLUMN])
    df[TEXT_COLUMN] = df[TEXT_COLUMN].astype(str)

    # convertir fechas
    df[TIME_COLUMN] = pd.to_datetime(df[TIME_COLUMN], unit='ms', errors='coerce')

    return df