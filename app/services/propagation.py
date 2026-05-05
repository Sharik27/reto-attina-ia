import pandas as pd

from app.data_loader import load_data
from app.config import ID_COLUMN, PARENT_COLUMN, THREAD_COLUMN, TIME_COLUMN

def analizar_propagacion():
    df = load_data()

    columnas = [ID_COLUMN, PARENT_COLUMN, THREAD_COLUMN, TIME_COLUMN]
    df = df[columnas].copy()

    total_mensajes = int(len(df))
    total_hilos = int(df[THREAD_COLUMN].nunique(dropna=True))
    mensajes_raiz = int(df[PARENT_COLUMN].isna().sum())
    respuestas = int(total_mensajes - mensajes_raiz)

    hijos_por_padre = (
        df.dropna(subset=[PARENT_COLUMN])
        .groupby(PARENT_COLUMN)
        .size()
        .sort_values(ascending=False)
    )

    padres = {
        fila[ID_COLUMN]: fila[PARENT_COLUMN]
        for _, fila in df[[ID_COLUMN, PARENT_COLUMN]].dropna(subset=[ID_COLUMN]).iterrows()
    }

    cache_profundidad = {}

    def calcular_profundidad(mensaje_id):
        if mensaje_id in cache_profundidad:
            return cache_profundidad[mensaje_id]

        visitados = set()
        profundidad = 0
        actual = mensaje_id

        while actual in padres:
            padre = padres.get(actual)
            if padre is None or padre != padre or padre in visitados:
                break

            visitados.add(actual)
            profundidad += 1
            actual = padre

        cache_profundidad[mensaje_id] = profundidad
        return profundidad

    profundidades = [
        calcular_profundidad(mensaje_id)
        for mensaje_id in df[ID_COLUMN].dropna().tolist()
    ]
    profundidad_maxima = int(max(profundidades, default=0))

    hilos = (
        df.groupby(THREAD_COLUMN, dropna=True)
        .agg(
            mensajes=(ID_COLUMN, "count"),
            primer_mensaje=(TIME_COLUMN, "min"),
            ultimo_mensaje=(TIME_COLUMN, "max"),
        )
        .sort_values("mensajes", ascending=False)
        .head(10)
        .reset_index()
    )

    hilos_mas_activos = []
    for _, fila in hilos.iterrows():
        primer_mensaje = fila["primer_mensaje"]
        ultimo_mensaje = fila["ultimo_mensaje"]
        hilos_mas_activos.append({
            "threadId": str(fila[THREAD_COLUMN]),
            "mensajes": int(fila["mensajes"]),
            "primer_mensaje": None if pd.isna(primer_mensaje) else primer_mensaje.isoformat(),
            "ultimo_mensaje": None if pd.isna(ultimo_mensaje) else ultimo_mensaje.isoformat(),
        })

    nodos_mas_respondidos = [
        {
            "id": str(mensaje_id),
            "respuestas_directas": int(total),
        }
        for mensaje_id, total in hijos_por_padre.head(10).items()
    ]

    return {
        "total_mensajes": total_mensajes,
        "total_hilos": total_hilos,
        "mensajes_raiz": mensajes_raiz,
        "respuestas": respuestas,
        "profundidad_maxima": profundidad_maxima,
        "hilos_mas_activos": hilos_mas_activos,
        "nodos_mas_respondidos": nodos_mas_respondidos,
    }
