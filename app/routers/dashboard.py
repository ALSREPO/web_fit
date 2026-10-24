# app/routers/dashboard.py
# Router FastAPI para endpoints del Dashboard
# Exposición de métricas, resúmenes y sugerencias de entrenamiento en formato JSON para el frontend.

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse
from datetime import date
from typing import List
from app.services.dashboard_service import DashboardService
from app.services.calendar_service import CalendarService
from app.services.day_detail_service import DayDetailService
from app.services.exercise_service import ExerciseService
from app.models.dashboard import (
    WorkoutCardResponse,
    MetricsSummaryResponse,
    CompactCalendarResponse,
    DayDetailResponse,
    ExerciseMaxWeightResponse,
    ExerciseSessionHistory,
    ExerciseChartPoint,
    AllExercisesOrdered
)

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard"]
)

@router.get("/next-workout", response_model=WorkoutCardResponse)
async def get_next_workout():
    return DashboardService.get_next_workout()

@router.get("/last-workout", response_model=WorkoutCardResponse)
async def get_last_workout():
    return DashboardService.get_last_workout()

@router.get("/summary", response_model=MetricsSummaryResponse)
async def get_summary(period: str = Query("month", pattern="^(week|month|year|all)$")):
    return DashboardService.get_summary(period)

@router.get("/calendar-compact", response_model=CompactCalendarResponse)
async def get_calendar_compact(
    year: int = Query(default_factory=lambda: date.today().year),
    month: int = Query(default_factory=lambda: date.today().month, ge=1, le=12)
):
    return CalendarService.get_compact_calendar(year, month)

@router.get("/day-detail/{fecha}", response_model=DayDetailResponse)
async def get_day_detail(fecha: date):
    return DayDetailService.get_day_detail(fecha)


@router.get("/exercise-max/{ejercicio}", response_model=ExerciseMaxWeightResponse)
async def get_exercise_max(ejercicio: str):
    """
    Obtiene el peso máximo alcanzado y el 1RM estimado para un ejercicio
    específico dentro de los últimos 3 meses.
    """
    return ExerciseService.get_exercise_max_weight(ejercicio)


@router.get("/exercise-history/{ejercicio}", response_model=List[ExerciseSessionHistory])
async def get_exercise_history(
    ejercicio: str, 
    limit: int = 10, 
    offset: int = 0
):
    return ExerciseService.get_exercise_history(ejercicio, limit=limit, offset=offset)


@router.get("/exercise-chart/{ejercicio}", response_model=List[ExerciseChartPoint])
async def get_exercise_chart(
    ejercicio: str, 
    timeframe: str = "30d"  # '7d', '30d', '12m', 'all'
):
    return ExerciseService.get_exercise_chart_data(ejercicio, timeframe)


@router.get("/all-exercises-ordered", response_model=List[AllExercisesOrdered])
def get_exercises_list():
    return ExerciseService.get_all_exercises_ordered()


# html para el frontend

@router.get("/fragment/next-workout", response_class=HTMLResponse)
async def fragment_next_workout():
    data = DashboardService.get_next_workout()
    if not data.get("has_workout"):
        return """
        <section class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-5 shadow-md">
            <p class="mb-1 text-xs font-medium text-slate-400">Próximo entrenamiento</p>
            <p class="mt-2 text-sm text-slate-400">No hay nada programado</p>
        </section>
        """
    
    sessions_html = ""
    for s in data["sessions"]:
        exercises_html = "".join([f"""
            <li class="flex items-start gap-2.5">
                <span class="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500"></span>
                <div class="flex flex-col">
                    <a href="/historico/{ex['ejercicio']}" class="font-medium text-slate-200 hover:text-blue-300">{ex['ejercicio']}</a>
                    <span class="font-mono text-xs text-slate-400">{ex['detalle']}</span>
                </div>
            </li>
        """ for ex in s["ejercicios"]])
        
        sessions_html += f"""
        <div class="mt-3">
            <p class="text-base font-semibold text-slate-100">{s['tipo_ejercicio']}</p>
            <ul class="mt-2 space-y-2.5 pl-2 text-sm text-slate-300">{exercises_html}</ul>
        </div>
        """

    return f"""
    <section class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-5 shadow-md">
        <p class="mb-1 text-xs font-medium text-slate-400">Próximo entrenamiento</p>
        <a href="/detalle/{data['fecha']}" class="block">
            <h3 class="text-lg font-bold text-amber-400">{data['date_label']}</h3>
        </a>
        <div class="mt-3 space-y-4">{sessions_html}</div>
    </section>
    """


@router.get("/fragment/last-workout", response_class=HTMLResponse)
async def fragment_last_workout():
    data = DashboardService.get_last_workout()
    if not data.get("has_workout"):
        return """
        <section class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-5 shadow-md">
            <p class="mb-1 text-xs font-medium text-slate-400">Entrenamiento anterior</p>
            <p class="mt-2 text-sm text-slate-400">Sin entrenamientos registrados</p>
        </section>
        """
    
    sessions_html = ""
    for s in data["sessions"]:
        exercises_html = "".join([f"""
            <li class="flex items-start gap-2.5">
                <span class="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500"></span>
                <div class="flex flex-col">
                    <a href="/historico/{ex['ejercicio']}" class="font-medium text-slate-200 hover:text-blue-300">{ex['ejercicio']}</a>
                    <span class="font-mono text-xs text-slate-400">{ex['detalle']}</span>
                </div>
            </li>
        """ for ex in s["ejercicios"]])
        
        sessions_html += f"""
        <div class="mt-3">
            <p class="text-base font-semibold text-slate-100">{s['tipo_ejercicio']}</p>
            <ul class="mt-2 space-y-2.5 pl-2 text-sm text-slate-300">{exercises_html}</ul>
        </div>
        """

    return f"""
    <section class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-5 shadow-md">
        <p class="mb-1 text-xs font-medium text-slate-400">Entrenamiento anterior</p>
        <a href="/detalle/{data['fecha']}" class="block">
            <h3 class="text-lg font-bold text-emerald-400">{data['date_label']}</h3>
        </a>
        <div class="mt-3 space-y-4">{sessions_html}</div>
    </section>
    """

@router.get("/fragment/summary-kpis", response_class=HTMLResponse)
async def fragment_summary_kpis(period: str = Query("month", pattern="^(week|month|year|all)$")):
    res = DashboardService.get_summary(period)
    kpis = res["kpis"]
    
    return f"""
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-2" id="summary-kpis">
        <div class="rounded-xl border border-slate-700/40 bg-slate-900/50 p-3.5 text-center">
            <span class="text-xs font-medium text-slate-400">Días</span>
            <p class="mt-1 text-2xl font-bold text-slate-100">{kpis['days_count']}</p>
        </div>
        <div class="rounded-xl border border-slate-700/40 bg-slate-900/50 p-3.5 text-center">
            <span class="text-xs font-medium text-slate-400">Sesiones</span>
            <p class="mt-1 text-2xl font-bold text-blue-400">{kpis['sessions_count']}</p>
        </div>
        <div class="rounded-xl border border-slate-700/40 bg-slate-900/50 p-3.5 text-center">
            <span class="text-xs font-medium text-slate-400">Volumen</span>
            <p class="mt-1 text-2xl font-bold text-amber-400">{kpis['total_volume_kg']:,} <span class="text-xs font-normal text-slate-400">kg</span></p>
        </div>
        <div class="rounded-xl border border-slate-700/40 bg-slate-900/50 p-3.5 text-center">
            <span class="text-xs font-medium text-slate-400">Distancia</span>
            <p class="mt-1 text-2xl font-bold text-emerald-400">{kpis['total_distance_km']} <span class="text-xs font-normal text-slate-400">km</span></p>
        </div>
    </div>
    """


@router.get("/fragment/calendar", response_class=HTMLResponse)
async def fragment_calendar(
    year: int = Query(default_factory=lambda: date.today().year),
    month: int = Query(default_factory=lambda: date.today().month, ge=1, le=12)
):
    # Usamos directamente tu servicio existente
    cal_data = CalendarService.get_compact_calendar(year, month)
    
    first_day = date(year, month, 1)
    start_day = first_day.weekday() # Lunes = 0, Domingo = 6
    
    months_esp = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    month_name = months_esp[month - 1]
    
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    def get_dot_color(type_str):
        if not type_str: return 'bg-yellow-500'
        lower = type_str.lower()
        if any(k in lower for k in ['fuerza', 'strength', 'pesa']): return 'bg-red-500'
        if any(k in lower for k in ['nataci', 'swim', 'agua']): return 'bg-blue-500'
        if any(k in lower for k in ['carrera', 'run', 'correr']): return 'bg-emerald-500'
        if any(k in lower for k in ['cicl', 'bici', 'bike']): return 'bg-orange-500'
        if any(k in lower for k in ['mma', 'bjj', 'jiu', 'luta', 'boxeo']): return 'bg-purple-500'
        return 'bg-yellow-500'

    days_html = ""
    # Días vacíos de relleno al inicio del mes
    for _ in range(start_day):
        days_html += '<div class="h-10 rounded-lg bg-transparent"></div>'
        
    for day_item in cal_data["days"]:
        day_num = int(day_item["date"].split("-")[2])
        date_str = day_item["date"]
        workouts = day_item["types"]
        
        dots_html = ""
        for w_type in workouts:
            color_class = get_dot_color(w_type)
            dots_html += f'<span class="h-1.5 w-1.5 rounded-full {color_class}"></span>'
            
        days_html += f"""
        <a href="/detalle/{date_str}" class="group relative flex h-10 flex-col items-center justify-between rounded-lg border border-slate-700/40 bg-slate-900/40 p-1 text-xs text-slate-200 transition hover:border-blue-500/50 hover:bg-slate-700/50">
            <span>{day_num}</span>
            <div class="flex items-center justify-center space-x-1">{dots_html}</div>
        </a>
        """

    week_days_headers = "".join([f'<div class="py-1 text-xs font-semibold text-slate-400">{d}</div>' for d in ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá', 'Do']])

    html = f"""
    <div class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-5 shadow-md space-y-4" id="compact-calendar-widget">
        <div class="border-b border-slate-700/60 pb-3 flex justify-between items-center">
            <h3 class="text-base font-bold text-slate-200">Calendario Mensual</h3>
            <span class="text-xs font-mono text-slate-400">{month_name} {year}</span>
        </div>

        <!-- Botones de navegación de mes con HTMX -->
        <div class="flex w-full items-center justify-between gap-2">
            <button type="button" 
                hx-get="/api/v1/dashboard/fragment/calendar?year={prev_year}&month={prev_month}" 
                hx-target="#compact-calendar-widget" 
                hx-swap="outerHTML"
                class="rounded-lg border border-slate-700/60 bg-slate-900/50 px-3 py-1.5 text-xs text-slate-300 transition hover:bg-slate-700 hover:text-white cursor-pointer">
                ← {months_esp[prev_month - 1][:3]}
            </button>
            
            <span class="text-xs font-semibold text-slate-200">{month_name} {year}</span>

            <button type="button" 
                hx-get="/api/v1/dashboard/fragment/calendar?year={next_year}&month={next_month}" 
                hx-target="#compact-calendar-widget" 
                hx-swap="outerHTML"
                class="rounded-lg border border-slate-700/60 bg-slate-900/50 px-3 py-1.5 text-xs text-slate-300 transition hover:bg-slate-700 hover:text-white cursor-pointer">
                {months_esp[next_month - 1][:3]} →
            </button>
        </div>

        <!-- Leyenda de colores -->
        <div class="flex w-full flex-wrap items-center justify-between gap-2 rounded-xl border border-slate-700/40 bg-slate-900/50 p-2.5 text-xs text-slate-400">
            <span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-red-500"></span> Fuerza</span>
            <span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-emerald-500"></span> Carrera</span>
            <span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-orange-500"></span> Ciclismo</span>
            <span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-blue-500"></span> Natación</span>
        </div>

        <!-- Grid del Calendario -->
        <div class="grid grid-cols-7 gap-1 text-center">
            {week_days_headers}
            {days_html}
        </div>
    </div>
    """
    return HTMLResponse(content=html)