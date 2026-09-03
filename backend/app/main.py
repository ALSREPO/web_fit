# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FitNotes Dashboard API",
    version="0.1.4",
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

#########################################################
# Cargamos los routers de la API

from backend.app.api.routers import fitnotes
app.include_router(fitnotes.router)


@app.get("/")
async def root():
    return {"status": "ok", "message": "FitNotes Analytics API activa"}