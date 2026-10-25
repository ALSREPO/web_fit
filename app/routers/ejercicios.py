# app/routers/ejercicios.py
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.exercise_service import ExerciseService

router = APIRouter(prefix="/ejercicios", tags=["Histórico ejercicios"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
async def ejercicios_list_view(request: Request, q: str = Query("")):
    exercises = ExerciseService.get_all_exercises_ordered()
    
    if q:
        q_lower = q.lower().strip()
        exercises = [ex for ex in exercises if q_lower in ex["nombre"].lower()]

    # Si la petición viene de HTMX (desde el buscador), devolvemos solo el fragmento de la lista
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(request, "ejercicios/partials/exercise_list.html", {"request": request, "exercises": exercises})

    return templates.TemplateResponse(request, "ejercicios/list.html", {"request": request, "exercises": exercises, "search_query": q})

@router.get("/{ejercicio}", response_class=HTMLResponse)
async def ejercicios_detail_view(request: Request, ejercicio: str):
    stats = ExerciseService.get_exercise_max_weight(ejercicio)
    history = ExerciseService.get_exercise_history(ejercicio, limit=10, offset=0)
    all_exercises = ExerciseService.get_all_exercises_ordered()

    return templates.TemplateResponse(request, "ejercicios/detail.html", {
        "request": request,
        "ejercicio": ejercicio,
        "stats": stats,
        "history": history,
        "exercisesList": all_exercises
    })

@router.get("/{ejercicio}/more", response_class=HTMLResponse)
async def ejercicios_more_sessions(request: Request, ejercicio: str, offset: int = Query(10)):
    """Endpoint para cargar más sesiones de forma infinita con HTMX."""
    history = ExerciseService.get_exercise_history(ejercicio, limit=10, offset=offset)
    return templates.TemplateResponse(request, "ejercicios/partials/session_rows.html", {
        "request": request,
        "history": history,
        "next_offset": offset + 10,
        "has_more": len(history) == 10
    })