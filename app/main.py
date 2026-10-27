# app/main.py
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
from starlette.middleware.base import BaseHTTPMiddleware

from app.database import init_db
from app.routers import fitnotes, dashboard, ejercicios
from app.services.day_detail_service import DayDetailService
from app.config import ENTORNO
from app.core.security import verify_admin
from app.utils.logging_config import configurar_logs, client_ip_ctx  # Importamos el módulo de logs

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa tablas, vistas y datos desde el JSON al arrancar
    init_db()
    yield

# Directorio base absoluto del paquete app/
BASE_DIR = Path(__file__).resolve().parent

###########################################################
# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="Diario De Hierro",
    version="1.1.0",
    description="Análisis de entrenamientos",
    lifespan=lifespan
)


###########################################################
# Configuramos el manejo de archivos estáticos de forma absoluta
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


###########################################################
# Configurar el sistema de logs global
from app.config import LOG_LEVEL

configurar_logs(LOG_LEVEL)
logger = logging.getLogger(f"DIARIO_HIERRO {ENTORNO}")

# 2. El Middleware se queda aquí porque necesita interactuar con la 'app'
class LogIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Capturamos la IP real (Cloudflare -> Docker)
        ip_real = request.headers.get("cf-connecting-ip") or request.headers.get("x-forwarded-for")
        if not ip_real and request.client:
            ip_real = request.client.host
        else:
            ip_real = ip_real.split(",")[0].strip() if ip_real else "IP desconocida"
            
        # Seteamos la IP en el contexto antes de procesar la petición
        token = client_ip_ctx.set(ip_real)
        try:
            response = await call_next(request)
            return response
        finally:
            client_ip_ctx.reset(token)

app.add_middleware(LogIPMiddleware)

logger.info('Iniciando la aplicación Diario de Hierro')   


###########################################################
# Cargamos los routers
app.include_router(fitnotes.router)
app.include_router(dashboard.router)
app.include_router(ejercicios.router)

@app.get("/favicon.svg")
async def get_favicon():
    env_upper = ENTORNO.upper()
    badge_svg = ""
    
    if env_upper == "DEVELOP":
        # Insignia roja con una 'D' blanca en la esquina superior derecha
        badge_svg = '''
        <circle cx="420" cy="92" r="64" fill="#ef4444" />
        <text x="420" y="116" font-family="sans-serif" font-size="72" font-weight="bold" fill="#ffffff" text-anchor="middle">D</text>
        '''
    elif env_upper == "STAGING":
        # Insignia ámbar/naranja con una 'S' oscura en la esquina superior derecha
        badge_svg = '''
        <circle cx="420" cy="92" r="64" fill="#f59e0b" />
        <text x="420" y="116" font-family="sans-serif" font-size="72" font-weight="bold" fill="#020617" text-anchor="middle">S</text>
        '''

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
      <!-- Fondo oscuro idéntico a la app -->
      <rect width="512" height="512" rx="96" fill="#020617" />
      
      <!-- Mancuerna vectorial -->
      <g fill="#3b82f6">
        <!-- Barra central -->
        <rect x="180" y="236" width="152" height="40" rx="6" />
        
        <!-- Lado Izquierdo (Discos) -->
        <rect x="80" y="220" width="28" height="72" rx="10" />
        <rect x="108" y="190" width="32" height="132" rx="12" />
        <rect x="140" y="160" width="40" height="192" rx="14" />
        
        <!-- Lado Derecho (Discos) -->
        <rect x="332" y="160" width="40" height="192" rx="14" />
        <rect x="372" y="190" width="32" height="132" rx="12" />
        <rect x="404" y="220" width="28" height="72" rx="10" />
      </g>
      
      {badge_svg}
    </svg>'''
    
    return Response(content=svg_content, media_type="image/svg+xml")

@app.get("/manifest.json")
async def get_manifest():
    # Definir sufijo según el entorno
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
        "icons": [
            {
                "src": "/favicon.svg",
                "sizes": "512x512",
                "type": "image/svg+xml",
                "purpose": "any maskable"
            }
        ]
    }
    return JSONResponse(manifest_data)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Diario De Hierro activo"}


# Configurar el directorio de plantillas Jinja2 de forma absoluta
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# Ruta raíz para evitar el bucle 404
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", context={
        "request": request, 
        "entorno": ENTORNO.upper()
    })

@app.get("/sw.js")
async def service_worker():
    return FileResponse(BASE_DIR / "static" / "sw.js", media_type="application/javascript")

@app.get("/calendario", response_class=HTMLResponse)
async def calendario_view(request: Request):
    return templates.TemplateResponse(request, "calendario.html", context={"request": request, "entorno": ENTORNO.upper()})


@app.get("/ejercicios", response_class=HTMLResponse)
async def ejercicios_view(request: Request):
    return templates.TemplateResponse(request, "ejercicios/list.html", context={"request": request, "entorno": ENTORNO.upper()})


@app.get("/sesiones/{fecha}", response_class=HTMLResponse)
async def sesion_detail_view(request: Request, fecha: date):
    detail = DayDetailService.get_day_detail(fecha)
    adjacent_dates = DayDetailService.get_adjacent_workout_dates(fecha)
    
    has_strength = False
    has_cardio = False
    if detail and isinstance(detail, dict) and detail.get("sessions"):
        for s in detail["sessions"]:
            tipo = s.get("tipo_ejercicio", "").lower()
            if any(k in tipo for k in ['carrera', 'nataci', 'ciclismo', 'running', 'cycling', 'swimming']):
                has_cardio = True
            else:
                has_strength = True

    show_duration = has_cardio or (has_strength and has_cardio)
    show_volume = has_strength or (has_strength and has_cardio)
    show_distance = has_cardio or (has_strength and has_cardio)

    role_priority = {"Principal": 2, "Asistencial": 1}
    color_by_id = {}
    
    if detail and isinstance(detail, dict) and detail.get("muscles"):
        for muscle in detail["muscles"]:
            role = muscle.get("role")
            for m_id in muscle.get("svg_ids", []):
                if m_id not in color_by_id or role_priority.get(role, 0) > role_priority.get(color_by_id[m_id], 0):
                    color_by_id[m_id] = role

    return templates.TemplateResponse(request, "sesiones/detail.html", {
        "request": request,
        "fecha": str(fecha),
        "detail": detail,
        "color_by_id": color_by_id,
        "show_duration": show_duration,
        "show_volume": show_volume,
        "show_distance": show_distance,
        "prev_fecha": adjacent_dates["prev_fecha"],
        "next_fecha": adjacent_dates["next_fecha"],
        "entorno": ENTORNO.upper()
    })

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, username: str = Depends(verify_admin)):
    return templates.TemplateResponse(request, "admin.html", {"request": request, "entorno": ENTORNO.upper()})


# Si entra en una ruta no definida, redirige a la raíz
@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def custom_404_handler(request: Request, __):
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8888, reload=True)