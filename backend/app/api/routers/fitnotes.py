# backend/app/api/routers/fitnotes.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pathlib import Path
import shutil
from typing import Optional

from backend.app.services.csv_service import CSVService
from backend.app.models.fitnotes import CSVUploadResponse

# Directorio de subidas relativo a la raíz del backend
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(
    prefix="/api/v1",
    tags=["FitNotes Data & Ingestion"]
)

# 1. Endpoint: Guardar el fichero físicamente con su nombre original
@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo enviado debe ser un archivo .csv")
    
    destination_path = UPLOAD_DIR / file.filename
    with destination_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {
        "filename": file.filename,
        "saved_path": str(destination_path),
        "message": "Archivo subido correctamente con su nombre original."
    }

# 2. Endpoint: Procesar e importar datos a DuckDB
@router.post("/import-data", response_model=CSVUploadResponse)
async def import_data(filename: Optional[str] = Query(None, description="Nombre del archivo a importar. Si se omite, procesa el más reciente.")):
    if filename:
        file_to_import = UPLOAD_DIR / filename
    else:
        file_to_import = CSVService.get_latest_csv_file(UPLOAD_DIR)
        
    if not file_to_import or not file_to_import.exists():
        raise HTTPException(status_code=404, detail="No se encontró ningún archivo CSV para importar.")
        
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
@router.get("/records")
async def get_records(limit: int = 100):
    return CSVService.get_all_records(limit=limit)

# 4. Endpoint: Mantenimiento y limpieza de CSVs antiguos
@router.delete("/clean-old-csvs")
async def clean_old_csvs():
    try:
        result = CSVService.delete_old_csv_files(UPLOAD_DIR)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al limpiar archivos antiguos: {str(e)}")