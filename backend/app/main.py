# app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
from backend.app.services.csv_service import CSVService
from backend.app.models.fitnotes import CSVUploadResponse

app = FastAPI(
    title="FitNotes Dashboard API",
    version="1.0.0",
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

@app.post("/api/v1/upload-csv", response_model=CSVUploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo enviado debe ser un archivo .csv")
    
    saved_path = UPLOAD_DIR / "latest_fitnotes.csv"
    with saved_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    records_count = CSVService.parse_and_store_csv(saved_path)
    
    return CSVUploadResponse(
        filename=file.filename,
        total_records=records_count,
        message="CSV de FitNotes parseado y almacenado correctamente en DuckDB"
    )

@app.get("/api/v1/records")
async def get_records(limit: int = 100):
    return CSVService.get_all_records(limit=limit)

@app.get("/")
async def root():
    return {"status": "ok", "message": "FitNotes Analytics API activa"}