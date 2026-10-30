from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.responses import FileResponse, JSONResponse, Response, RedirectResponse
from fastapi.staticfiles import StaticFiles
import logging
from starlette.middleware.base import BaseHTTPMiddleware
import sys
import os

from app.database import init_db
from app.routers import fitnotes, dashboard, login, frontend
from app.config import ENTORNO, LOG_LEVEL
from app.utils.logging_config import configurar_logs, client_ip_ctx

# Forzamos a Python a mirar en la raíz del proyecto para encontrar 'database'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.init_db import inicializar_base_de_datos

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Diario De Hierro",
    version="1.1.0",
    description="Análisis de entrenamientos",
    lifespan=lifespan
)

# Archivos estáticos
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Configurar logs
configurar_logs(LOG_LEVEL)
logger = logging.getLogger(f"DIARIO_HIERRO {ENTORNO}")

# Middleware de IP
class LogIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip_real = request.headers.get("cf-connecting-ip") or request.headers.get("x-forwarded-for")
        if not ip_real and request.client:
            ip_real = request.client.host
        else:
            ip_real = ip_real.split(",")[0].strip() if ip_real else "IP desconocida"
            
        token = client_ip_ctx.set(ip_real)
        try:
            return await call_next(request)
        finally:
            client_ip_ctx.reset(token)

app.add_middleware(LogIPMiddleware)
logger.info('Iniciando la aplicación Diario de Hierro')  

# --- Inclusión de Routers ---
app.include_router(login.router)
app.include_router(fitnotes.router)
app.include_router(dashboard.router)
app.include_router(frontend.router)  # El frontend va al final para capturar las páginas raíz

# Endpoints de Sistema (Favicon, Manifest, Health)
@app.get("/favicon.svg")
async def get_favicon():
    env_upper = ENTORNO.upper()
    badge_svg = ""
    
    if env_upper == "DEVELOP":
        badge_svg = '<circle cx="420" cy="92" r="64" fill="#ef4444" /><text x="420" y="116" font-family="sans-serif" font-size="72" font-weight="bold" fill="#ffffff" text-anchor="middle">D</text>'
    elif env_upper == "STAGING":
        badge_svg = '<circle cx="420" cy="92" r="64" fill="#f59e0b" /><text x="420" y="116" font-family="sans-serif" font-size="72" font-weight="bold" fill="#020617" text-anchor="middle">S</text>'

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
      <rect width="512" height="512" rx="96" fill="#020617" />
      <g fill="#3b82f6">
        <rect x="180" y="236" width="152" height="40" rx="6" />
        <rect x="80" y="220" width="28" height="72" rx="10" />
        <rect x="108" y="190" width="32" height="132" rx="12" />
        <rect x="140" y="160" width="40" height="192" rx="14" />
        <rect x="332" y="160" width="40" height="192" rx="14" />
        <rect x="372" y="190" width="32" height="132" rx="12" />
        <rect x="404" y="220" width="28" height="72" rx="10" />
      </g>
      {badge_svg}
    </svg>'''
    return Response(content=svg_content, media_type="image/svg+xml")

@app.get("/manifest.json")
async def get_manifest():
    suffix = ""
    env_upper = ENTORNO.upper()
    if env_upper == "DEVELOP":
        suffix = " - Dev"
    elif env_upper == "STAGING":
        suffix = " - Pre"
    
    manifest_data = {
        "name": f"Diario de Hierro{suffix}",
        "short_name": f"Diario de Hierro{suffix}",
        "description": "Análisis de entrenamientos y rendimiento",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#020617",
        "theme_color": "#020617",
        "icons": [{
            "src": "/favicon.svg",
            "sizes": "512x512",
            "type": "image/svg+xml",
            "purpose": "any maskable"
        }]
    }
    return JSONResponse(manifest_data)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Diario De Hierro activo"}

@app.get("/sw.js")
async def service_worker():
    return FileResponse(BASE_DIR / "static" / "sw.js", media_type="application/javascript")

# Manejador global de 404 para redirigir rutas huérfanas
@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def custom_404_handler(request: Request, __):
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8888, reload=True)