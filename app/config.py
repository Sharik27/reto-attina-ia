import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

TEXT_COLUMN = "text"
ID_COLUMN = "id"
PARENT_COLUMN = "parentId"
TIME_COLUMN = "createdAt"
THREAD_COLUMN = "threadId"

DATA_PATH = "data/Reto_data_20251023_122206.parquet"

# Configuración de IA segura
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "") 
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.3-70b-versatile"