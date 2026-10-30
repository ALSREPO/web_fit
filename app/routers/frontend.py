import logging
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Request, status, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.models.login import Usuario
from app.utils.auth import obtener_usuario_actual, usuario_obligatorio, verificar_admin
from app.services.day_detail_service import DayDetailService
from app.services.exercise_service import ExerciseService
from app.config import ENTORNO, ROOT_DIR

templates = Jinja2Templates(directory=str(ROOT_DIR / "app" / "templates"))

logger = logging.getLogger("DIARIO_HIERRO_Frontend")

router = APIRouter(prefix="", tags=["FrontEnd"])


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(request, "index.html", context={
        "request": request, 
        "user": user,
        "entorno": ENTORNO.upper()
    })


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(request, "login/login.html", {"request": request, "entorno": ENTORNO.upper()})


@router.get("/registro", response_class=HTMLResponse)
async def registro_page(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(request, "login/registro.html", {"request": request, "entorno": ENTORNO.upper()})


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


@router.get("/calendario", response_class=HTMLResponse)
async def calendario_view(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(request, "calendario.html", context={"request": request, "user": user, "entorno": ENTORNO.upper()})


@router.get("/sesiones/{fecha}", response_class=HTMLResponse)
async def sesion_detail_view(request: Request, fecha: date, user: Usuario = Depends(obtener_usuario_actual)):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
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
        "user": user,
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


########################
# Módulo de Ejercicios
########################

@router.get("/ejercicios", response_class=HTMLResponse)
async def ejercicios_list_view(
    request: Request, 
    q: str = Query(""), 
    user: Usuario = Depends(obtener_usuario_actual)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    exercises = ExerciseService.get_all_exercises_ordered()
    
    if q:
        q_lower = q.lower().strip()
        exercises = [ex for ex in exercises if q_lower in ex["nombre"].lower()]

    # Si la petición viene de HTMX (desde el buscador), devolvemos solo el fragmento de la lista
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(request, "ejercicios/partials/exercise_list.html", {
            "request": request, 
            "exercises": exercises, 
            "user": user,
            "entorno": ENTORNO.upper()
        })

    return templates.TemplateResponse(request, "ejercicios/list.html", {
        "request": request, 
        "exercises": exercises, 
        "search_query": q, 
        "user": user,
        "entorno": ENTORNO.upper()
    })


@router.get("/ejercicios/{ejercicio}", response_class=HTMLResponse)
async def ejercicio_detail_view(
    request: Request, 
    ejercicio: str,
    user: Usuario = Depends(obtener_usuario_actual)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    stats = ExerciseService.get_exercise_max_weight(ejercicio)
    history = ExerciseService.get_exercise_history(ejercicio, limit=10, offset=0)
    all_exercises = ExerciseService.get_all_exercises_ordered()
    
    next_batch = ExerciseService.get_exercise_history(ejercicio, limit=1, offset=10)
    has_more = len(next_batch) > 0

    return templates.TemplateResponse(request, "ejercicios/detail.html", {
        "request": request,
        "ejercicio": ejercicio,
        "stats": stats,
        "history": history,
        "has_more": has_more,
        "next_offset": 10,
        "exercisesList": all_exercises,
        "user": user,
        "entorno": ENTORNO.upper()
    })


@router.get("/ejercicios/{ejercicio}/more", response_class=HTMLResponse)
async def ejercicio_more_sessions(
    request: Request, 
    ejercicio: str, 
    offset: int = Query(10),
    user: Usuario = Depends(obtener_usuario_actual)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    limit = 10
    history = ExerciseService.get_exercise_history(ejercicio, limit=limit, offset=offset)
    
    next_batch = ExerciseService.get_exercise_history(ejercicio, limit=1, offset=offset + limit)
    has_more = len(next_batch) > 0

    return templates.TemplateResponse(request, "ejercicios/partials/session_rows.html", {
        "request": request,
        "history": history,
        "next_offset": offset + limit,
        "has_more": has_more,
        "ejercicio": ejercicio,
        "user": user,
        "entorno": ENTORNO.upper()
    })


@router.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, user: Usuario = Depends(obtener_usuario_actual)):
    # Si no hay usuario, mandarlo al login
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Si el usuario no tiene nivel de administrador (activo < 20), mandarlo a la home
    if user.activo < 20:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        
    return templates.TemplateResponse(request, "admin.html", {
        "request": request, 
        "user": user, 
        "entorno": ENTORNO.upper()
    })