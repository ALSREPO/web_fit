# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import init_db
from app.routers import fitnotes, dashboard

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


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Diario De Hierro activo"}


# Configurar el directorio de plantillas Jinja2
templates = Jinja2Templates(directory="app/templates")


# Ruta raíz para evitar el bucle 404
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
  # Si aún no tienes el index.html creado, puedes devolver un texto plano temporalmente:
  # return "<h1>Diario de Hierro - Backend Activo</h1>"

  # O renderizar tu plantilla de Jinja2 cuando la tengas lista:
  return templates.TemplateResponse("index.html", {"request": request})

# Si entra en una ruta no definida, redirige a la raíz
@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def custom_404_handler(request: Request, __):
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

if __name__ == "__main__":
    import uvicorn
    # Cambiado a 0.0.0.0 para que escuche fuera del contenedor si lo corres directo
    uvicorn.run("app.main:app", host="0.0.0.0", port=8888, reload=True)
