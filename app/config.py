# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Ruta raíz del proyecto (un nivel por encima de 'app/')
ROOT_DIR = Path(__file__).parent.parent

# Cargar explícitamente el archivo .env desde la raíz
load_dotenv(ROOT_DIR / ".env")

# Leer la variable de entorno (por defecto DEVELOP si no existe)
ENTORNO = os.getenv("ENTORNO", "DEVELOP").upper()

# Construir dinámicamente la carpeta de datos (ej: data_DEVELOP, data_PRO...)
DATA_DIR = ROOT_DIR / "data" / f"data_{ENTORNO}"
UPLOAD_DIR = ROOT_DIR / "data" / "uploads" # común a todos los entornos

# Asegurar que la carpeta de datos del entorno actual exista físicamente
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Leer las variables de .env
ADMIN_USER = os.getenv("ADMIN_USER", "ALS")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "ALS")