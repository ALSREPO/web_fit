# app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
from typing import Optional

from backend.app.services.csv_service import CSVService
from backend.app.models.fitnotes import CSVUploadResponse

app = FastAPI(
    title="FitNotes Dashboard API",
    version="0.1.2",
    description="Backend en FastAPI + DuckDB para análisis de entrenamientos"
)

# Configuración CORS para conexión con SvelteKit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción se especifica el puerto de SvelteKit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 1. Endpoint: Solo guardar el fichero físicamente con su nombre original
@app.post("/api/v1/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo enviado debe ser un archivo .csv")
    
    # Se guarda manteniendo el nombre original suministrado por FitNotes
    destination_path = UPLOAD_DIR / file.filename
    with destination_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {
        "filename": file.filename,
        "saved_path": str(destination_path),
        "message": "Archivo subido correctamente con su nombre original."
    }

# 2. Endpoint: Procesar e importar datos a DuckDB
@app.post("/api/v1/import-data", response_model=CSVUploadResponse)
async def import_data(filename: Optional[str] = Query(None, description="Nombre del archivo a importar. Si se omite, procesa el más reciente.")):
    if filename:
        file_to_import = UPLOAD_DIR / filename
    else:
        file_to_import = CSVService.get_latest_csv_file(UPLOAD_DIR)
        
    if not file_to_import or not file_to_import.exists():
        raise HTTPException(status_code=444, detail="No se encontró ningún archivo CSV para importar.")
        
    try:
        records_count = CSVService.parse_and_store_csv(file_to_import)
        return CSVUploadResponse(
            filename=file_to_import.name,
            total_records=records_count,
            message="Datos procesados e importados correctamente en DuckDB."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la importación: {str(e)}")

# 3. Endpoint: Consultar registros
@app.get("/api/v1/records")
async def get_records(limit: int = 100):
    return CSVService.get_all_records(limit=limit)

# 4. Endpoint: Mantenimiento y limpieza de CSVs antiguos
@app.delete("/api/v1/clean-old-csvs")
async def clean_old_csvs():
    try:
        result = CSVService.delete_old_csv_files(UPLOAD_DIR)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al limpiar archivos antiguos: {str(e)}")


@app.get("/")
async def root():
    return {"status": "ok", "message": "FitNotes Analytics API activa"}