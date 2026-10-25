# app/main.py
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import init_db
from app.routers import fitnotes, dashboard, ejercicios
from app.services.day_detail_service import DayDetailService

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
    version="1.0.0",
    description="Análisis de entrenamientos",
    lifespan=lifespan
)


###########################################################
# Configuramos el manejo de archivos estáticos de forma absoluta
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


###########################################################
# Cargamos los routers
app.include_router(fitnotes.router)
app.include_router(dashboard.router)
app.include_router(ejercicios.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Diario De Hierro activo"}


# Configurar el directorio de plantillas Jinja2 de forma absoluta
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# Ruta raíz para evitar el bucle 404
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", context={"request": request})


@app.get("/calendario", response_class=HTMLResponse)
async def calendario_view(request: Request):
    return templates.TemplateResponse(request, "calendario.html", context={"request": request})


@app.get("/ejercicios", response_class=HTMLResponse)
async def ejercicios_view(request: Request):
    return templates.TemplateResponse(request, "ejercicios/list.html", context={"request": request})


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
        "next_fecha": adjacent_dates["next_fecha"]
    })

# Si entra en una ruta no definida, redirige a la raíz
@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def custom_404_handler(request: Request, __):
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8888, reload=True)