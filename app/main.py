# backend/app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(
    title="Diario De Hierro API",
    version="0.6.0",
    description="Análisis de entrenamientos"
)

# Configuración CORS (necesaria para dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#########################################################
# 1. Routers de la API (Tienen prioridad)
from backend.app.api.routers import fitnotes, dashboard

app.include_router(fitnotes.router) 
app.include_router(dashboard.router)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Diario De Hierro API activa"}


#########################################################
# 2. Servir el Frontend compilado
frontend_build_dir = "/app/frontend/build"
print("¿Entrará?")
if os.path.exists(frontend_build_dir):
    print("Entra")
    # Sirve los recursos estáticos generados por SvelteKit
    app.mount("/_app", StaticFiles(directory=f"{frontend_build_dir}/_app"), name="static_app")
    
    # Manejador Single Page Application (SPA) para cualquier ruta que no sea de la API
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Si la petición apunta a un archivo estático existente (favicons, manifest, etc.), lo entrega
        possible_file = os.path.join(frontend_build_dir, full_path)
        if full_path != "" and os.path.exists(possible_file):
            return FileResponse(possible_file)
        # Para el resto de rutas navegables de SvelteKit, devuelve el index.html
        return FileResponse(f"{frontend_build_dir}/index.html")