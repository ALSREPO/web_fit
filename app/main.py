# app/main.py
from contextlib import asynccontextmanager
from datetime import date
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


###########################################################
# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="Diario De Hierro",
    version="0.7.0",
    description="Análisis de entrenamientos",
    lifespan=lifespan
)


###########################################################
# Configuramos el manejo de archivos estáticos (CSS, JS y vídeos)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


###########################################################
# Cargamos los routers
app.include_router(fitnotes.router)
app.include_router(dashboard.router)
app.include_router(ejercicios.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Diario De Hierro activo"}


# Configurar el directorio de plantillas Jinja2
templates = Jinja2Templates(directory="app/templates")


# Ruta raíz para evitar el bucle 404
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
  # Si aún no tienes el index.html creado, puedes devolver un texto plano temporalmente:
  #return "<h1>Diario de Hierro - Backend Activo</h1>"

  # O renderizar tu plantilla de Jinja2 cuando la tengas lista:
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
    
    # Mapeo de colores/roles para el mapa muscular SVG
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
        "color_by_id": color_by_id
    })

# Si entra en una ruta no definida, redirige a la raíz
@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def custom_404_handler(request: Request, __):
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

if __name__ == "__main__":
    import uvicorn
    # Cambiado a 0.0.0.0 para que escuche fuera del contenedor si lo corres directo
    uvicorn.run("app.main:app", host="0.0.0.0", port=8888, reload=True)
