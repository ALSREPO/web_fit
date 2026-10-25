# app/routers/dashboard.py
# Router FastAPI para endpoints del Dashboard
# Exposición de métricas, resúmenes y sugerencias de entrenamiento en formato JSON para el frontend.

import duckdb
from fastapi import APIRouter, Query, Depends
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
                    <a href="/ejercicios/{ex['ejercicio']}" class="font-medium text-slate-200 hover:text-blue-300">{ex['ejercicio']}</a>
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
        <a href="/sesiones/{data['fecha']}" class="block">
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
                    <a href="/ejercicios/{ex['ejercicio']}" class="font-medium text-slate-200 hover:text-blue-300">{ex['ejercicio']}</a>
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
        <a href="/sesiones/{data['fecha']}" class="block">
            <h3 class="text-lg font-bold text-emerald-400">{data['date_label']}</h3>
        </a>
        <div class="mt-3 space-y-4">{sessions_html}</div>
    </section>
    """

@router.get("/fragment/summary-kpis", response_class=HTMLResponse)
async def fragment_summary_kpis(
    period: str = Query("week", pattern="^(week|month|year|all)$"),
    metric: str = Query("sessions_count", pattern="^(sessions_count|volume_kg|distance_km)$"),
    view: str = Query("time", pattern="^(time|type)$")
):
    data = DashboardService.get_summary(period)
    kpis = data["kpis"]
    
    # Seleccionar origen de datos según la vista (Periodo o Tipo)
    raw_data = data["chart_by_time"] if view == "time" else data["chart_by_type"]
    
    # Filtrar ceros en vista tipo si es necesario
    if view == "type":
        chart_data = [item for item in raw_data if item.get(metric, 0) > 0]
    else:
        chart_data = raw_data

    # Calcular el valor máximo estrictamente en función de la métrica seleccionada (soluciona el problema de las barras)
    max_val = max([item.get(metric, 0) for item in chart_data], default=1)
    if max_val == 0:
        max_val = 1

    metric_units = {
        "sessions_count": "sesiones",
        "volume_kg": "kg",
        "distance_km": "km"
    }

    periods_def = [("week", "Semana"), ("month", "Mes"), ("year", "Año"), ("all", "Histórico")]
    
    # Botones de Periodo
    periods_html = ""
    for p_id, p_label in periods_def:
        is_active = (period == p_id)
        btn_class = "bg-blue-600 text-white shadow-sm" if is_active else "text-slate-400 hover:text-slate-200"
        periods_html += f"""
        <button type="button" 
            hx-get="/api/v1/dashboard/fragment/summary-kpis?period={p_id}&metric={metric}&view={view}" 
            hx-target="#summary-card-container" 
            hx-swap="outerHTML"
            class="rounded-lg py-1.5 text-center text-xs font-semibold transition-all {btn_class} cursor-pointer">
            {p_label}
        </button>
        """

    # Botones de Vista (Periodo / Tipo)
    view_time_class = "bg-slate-700 text-slate-100" if view == "time" else "text-slate-400 hover:text-slate-200"
    view_type_class = "bg-slate-700 text-slate-100" if view == "type" else "text-slate-400 hover:text-slate-200"

    # Botones de Métrica
    m_sessions_class = "text-blue-400 underline underline-offset-4" if metric == "sessions_count" else "text-slate-400 hover:text-slate-200"
    m_volume_class = "text-amber-400 underline underline-offset-4" if metric == "volume_kg" else "text-slate-400 hover:text-slate-200"
    m_distance_class = "text-emerald-400 underline underline-offset-4" if metric == "distance_km" else "text-slate-400 hover:text-slate-200"

    # Renderizar Barras del Gráfico
    bars_html = ""
    if not chart_data:
        bars_html = '<div class="flex h-52 w-full items-center justify-center text-xs text-slate-500">No hay datos registrados para este periodo.</div>'
    else:
        total_bars = len(chart_data)
        for idx, item in enumerate(chart_data):
            val = item.get(metric, 0)
            height_percent = max((val / max_val) * 100, 4) if val > 0 else 0
            show_label = not (period == "month" and view == "time") or (idx % 5 == 0 or idx == total_bars - 1)
            
            if metric == "sessions_count":
                bar_color = "bg-blue-500 group-hover:bg-blue-400" if val > 0 else "bg-slate-800/30"
                text_color = "text-blue-400"
            elif metric == "volume_kg":
                bar_color = "bg-amber-500 group-hover:bg-amber-400" if val > 0 else "bg-slate-800/30"
                text_color = "text-amber-400"
            else:
                bar_color = "bg-emerald-500 group-hover:bg-emerald-400" if val > 0 else "bg-slate-800/30"
                text_color = "text-emerald-400"

            formatted_val = f"{val:,.0f}".replace(",", ".")

            bars_html += f"""
            <div class="group relative flex h-full flex-1 flex-col items-center justify-end cursor-pointer">
                <div class="absolute -top-10 rounded bg-slate-950 px-2 py-1 text-[10px] font-mono text-slate-100 shadow-lg border border-slate-700 z-20 whitespace-nowrap pointer-events-none transition-opacity hidden group-hover:block flex flex-col items-center leading-tight">
                    <span class="text-[9px] text-slate-400 font-sans">{item['label']}</span>
                    <span class="font-bold {text_color}">{formatted_val} {metric_units[metric]}</span>
                </div>
                <div class="w-full rounded-t-md transition-all duration-300 shadow-sm {bar_color}" style="height: {height_percent}%"></div>
                <span class="absolute -bottom-6 text-[9px] font-medium text-slate-400 truncate w-full text-center">
                    {item['label'] if show_label else ''}
                </span>
            </div>
            """

    html = f"""
    <section class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-5 shadow-md space-y-6" id="summary-card-container">
        <!-- Header con Selector de Periodo -->
        <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-700/60 pb-3">
            <h2 class="text-base font-bold text-slate-200">Resumen</h2>
            <div class="grid w-full flex-1 grid-cols-4 gap-1 rounded-xl border border-slate-700/40 bg-slate-900/80 p-1 min-w-[280px] sm:w-auto sm:flex-none">
                {periods_html}
            </div>
        </div>

        <!-- Tarjetas KPI -->
        <div class="grid grid-cols-2 gap-3 sm:grid-cols-2">
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
                <p class="mt-1 text-2xl font-bold text-amber-400">{f"{kpis['total_volume_kg']:,.0f}".replace(',', '.')} <span class="text-xs font-normal text-slate-400">kg</span></p>
            </div>
            <div class="rounded-xl border border-slate-700/40 bg-slate-900/50 p-3.5 text-center">
                <span class="text-xs font-medium text-slate-400">Distancia</span>
                <p class="mt-1 text-2xl font-bold text-emerald-400">{kpis['total_distance_km']} <span class="text-xs font-normal text-slate-400">km</span></p>
            </div>
        </div>

        <!-- Controles del Gráfico (Vista y Métrica) -->
        <div class="space-y-4 pt-2">
            <div class="flex flex-wrap items-center justify-between gap-3">
                <div class="flex gap-1 rounded-lg bg-slate-900/60 p-1 border border-slate-700/30">
                    <button type="button" 
                        hx-get="/api/v1/dashboard/fragment/summary-kpis?period={period}&metric={metric}&view=time" 
                        hx-target="#summary-card-container" hx-swap="outerHTML"
                        class="rounded px-2.5 py-1 text-xs font-medium transition-all {view_time_class} cursor-pointer">
                        Periodo
                    </button>
                    <button type="button" 
                        hx-get="/api/v1/dashboard/fragment/summary-kpis?period={period}&metric={metric}&view=type" 
                        hx-target="#summary-card-container" hx-swap="outerHTML"
                        class="rounded px-2.5 py-1 text-xs font-medium transition-all {view_type_class} cursor-pointer">
                        Tipo
                    </button>
                </div>

                <div class="flex gap-3 text-xs font-medium">
                    <button type="button" 
                        hx-get="/api/v1/dashboard/fragment/summary-kpis?period={period}&metric=sessions_count&view={view}" 
                        hx-target="#summary-card-container" hx-swap="outerHTML"
                        class="transition-colors {m_sessions_class} cursor-pointer">
                        Sesiones
                    </button>
                    <button type="button" 
                        hx-get="/api/v1/dashboard/fragment/summary-kpis?period={period}&metric=volume_kg&view={view}" 
                        hx-target="#summary-card-container" hx-swap="outerHTML"
                        class="transition-colors {m_volume_class} cursor-pointer">
                        Volumen (kg)
                    </button>
                    <button type="button" 
                        hx-get="/api/v1/dashboard/fragment/summary-kpis?period={period}&metric=distance_km&view={view}" 
                        hx-target="#summary-card-container" hx-swap="outerHTML"
                        class="transition-colors {m_distance_class} cursor-pointer">
                        Distancia (km)
                    </button>
                </div>
            </div>

            <!-- Área del Gráfico de Barras -->
            <div class="relative h-52 w-full rounded-xl border border-slate-700/40 bg-slate-900/40 p-3 pt-6 pb-8 flex items-end">
                <div class="absolute inset-x-3 top-6 bottom-8 flex flex-col justify-between pointer-events-none opacity-15">
                    <div class="border-b border-slate-400 w-full"></div>
                    <div class="border-b border-slate-400 w-full border-dashed"></div>
                    <div class="border-b border-slate-400 w-full"></div>
                </div>
                <div class="relative flex h-full w-full items-end justify-between gap-1">
                    {bars_html}
                </div>
            </div>
        </div>
    </section>
    """
    return HTMLResponse(content=html)


@router.get("/fragment/calendar", response_class=HTMLResponse)
async def fragment_calendar(
    year: int = Query(default_factory=lambda: date.today().year),
    month: int = Query(default_factory=lambda: date.today().month, ge=1, le=12),
    filter: str = Query(None)
):
    cal_data = CalendarService.get_compact_calendar(year, month)
    
    first_day = date(year, month, 1)
    start_day = first_day.weekday()
    today_str = date.today().strftime('%Y-%m-%d')
    current_year = date.today().year
    current_month = date.today().month
    
    months_esp = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    month_name = months_esp[month - 1]
    
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    min_year = 2018
    years_range = range(min_year, current_year + 2)

    disciplines = [
        {"key": "fuerza", "label": "Fuerza", "color": "bg-red-500", "match": ['fuerza', 'strength', 'pesa']},
        {"key": "carrera", "label": "Carrera", "color": "bg-emerald-500", "match": ['carrera', 'run', 'correr']},
        {"key": "ciclismo", "label": "Ciclismo", "color": "bg-orange-500", "match": ['cicl', 'bici', 'bike']},
        {"key": "natacion", "label": "Natación", "color": "bg-blue-500", "match": ['nataci', 'swim', 'agua']},
    ]

    def get_dot_color(type_str):
        if not type_str: return 'bg-yellow-500'
        lower = type_str.lower()
        for disc in disciplines:
            if any(k in lower for k in disc["match"]):
                return disc["color"]
        return 'bg-yellow-500'

    total_active_days = sum(1 for d in cal_data["days"] if d["has_workout"])

    days_html = ""
    for _ in range(start_day):
        days_html += '<div class="h-10 rounded-lg bg-transparent"></div>'
        
    for day_item in cal_data["days"]:
        day_num = int(day_item["date"].split("-")[2])
        date_str = day_item["date"]
        workouts = day_item["types"]
        
        if filter:
            active_disc = next((d for d in disciplines if d["key"] == filter), None)
            if active_disc:
                workouts = [w for w in workouts if any(k in w.lower() for k in active_disc["match"])]
                has_match = len(workouts) > 0
            else:
                has_match = True
        else:
            has_match = day_item["has_workout"]

        is_today = (date_str == today_str)

        dots_html = ""
        for w_type in workouts:
            color_class = get_dot_color(w_type)
            dots_html += f'<span class="h-1.5 w-1.5 rounded-full {color_class}"></span>'
            
        opacity_class = "opacity-100" if (not filter or has_match) else "opacity-25"
        
        if is_today:
            border_highlight = "border-blue-400 bg-blue-950/40 ring-1 ring-blue-400 font-bold"
        elif filter and has_match:
            border_highlight = "border-blue-500/80 bg-slate-800/60"
        else:
            border_highlight = "border-slate-700/40 bg-slate-900/40"

        tooltip_text = f"Entrenos: {', '.join(workouts)}" if workouts else "Sin entrenamientos"

        days_html += f"""
        <a href="/sesiones/{date_str}" title="{tooltip_text}" class="group relative flex h-10 flex-col items-center justify-between rounded-lg border {border_highlight} p-1 text-xs text-slate-200 transition hover:border-blue-500/50 hover:bg-slate-700/50 {opacity_class}">
            <span class="{'text-blue-400' if is_today else ''}">{day_num}</span>
            <div class="flex items-center justify-center space-x-1">{dots_html}</div>
        </a>
        """

    week_days_headers = "".join([f'<div class="py-1 text-xs font-semibold text-slate-400">{d}</div>' for d in ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá', 'Do']])

    months_options = "".join([f'<option value="{idx}" {"selected" if idx == month else ""} class="bg-slate-800 text-slate-200">{m_name}</option>' for idx, m_name in enumerate(months_esp, start=1)])
    years_options = "".join([f'<option value="{yr}" {"selected" if yr == year else ""} class="bg-slate-800 text-slate-200">{yr}</option>' for yr in years_range])

    legend_html = ""
    for disc in disciplines:
        is_active = (filter == disc["key"])
        next_filter = "" if is_active else disc["key"]
        ring_style = "ring-2 ring-white scale-[1.02]" if is_active else "opacity-75 hover:opacity-100"
        
        legend_html += f"""
        <button type="button"
            hx-get="/api/v1/dashboard/fragment/calendar?year={year}&month={month}&filter={next_filter}"
            hx-target="#compact-calendar-widget"
            hx-swap="outerHTML"
            class="flex items-center justify-center gap-1.5 px-2.5 py-1.5 rounded-lg transition cursor-pointer bg-slate-900/80 border border-slate-700/50 w-full {ring_style}">
            <span class="h-2.5 w-2.5 rounded-full {disc['color']}"></span> 
            <span class="text-xs {'font-bold text-white' if is_active else 'text-slate-300'}">{disc['label']}</span>
        </button>
        """

    html = f"""
    <div class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-5 shadow-md space-y-4" id="compact-calendar-widget">
        <div class="border-b border-slate-700/60 pb-3 flex justify-between items-center">
            <div>
                <h3 class="text-base font-bold text-slate-200">Calendario Mensual</h3>
                <p class="text-[11px] text-slate-400">{total_active_days} días de entrenamiento este mes</p>
            </div>
            
            <button type="button"
                hx-get="/api/v1/dashboard/fragment/calendar?year={current_year}&month={current_month}&filter={filter or ''}"
                hx-target="#compact-calendar-widget"
                hx-swap="outerHTML"
                class="rounded-lg bg-blue-600/20 border border-blue-500/40 px-2.5 py-1 text-[11px] font-semibold text-blue-400 hover:bg-blue-600/30 transition cursor-pointer">
                Hoy
            </button>
        </div>

        <!-- Controles de navegación y selectores -->
        <div class="flex w-full items-center gap-1.5">
            <button type="button" 
                hx-get="/api/v1/dashboard/fragment/calendar?year={prev_year}&month={prev_month}&filter={filter or ''}" 
                hx-target="#compact-calendar-widget" 
                hx-swap="outerHTML"
                class="shrink-0 rounded-lg border border-slate-700/60 bg-slate-900/50 p-2 text-slate-300 transition hover:bg-slate-700 hover:text-white cursor-pointer"
                aria-label="Mes anterior">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
            </button>

            <select name="month" 
                hx-get="/api/v1/dashboard/fragment/calendar" 
                hx-target="#compact-calendar-widget" 
                hx-swap="outerHTML"
                hx-include="#compact-calendar-widget select, #compact-calendar-widget [name='filter']"
                class="min-w-0 flex-1 truncate rounded-lg border border-slate-700/60 bg-slate-900/50 px-2 py-2 text-center text-xs font-medium text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer">
                {months_options}
            </select>

            <select name="year" 
                hx-get="/api/v1/dashboard/fragment/calendar" 
                hx-target="#compact-calendar-widget" 
                hx-swap="outerHTML"
                hx-include="#compact-calendar-widget select, #compact-calendar-widget [name='filter']"
                class="w-20 shrink-0 rounded-lg border border-slate-700/60 bg-slate-900/50 px-2 py-2 text-center text-xs font-medium text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer">
                {years_options}
            </select>

            <button type="button" 
                hx-get="/api/v1/dashboard/fragment/calendar?year={next_year}&month={next_month}&filter={filter or ''}" 
                hx-target="#compact-calendar-widget" 
                hx-swap="outerHTML"
                class="shrink-0 rounded-lg border border-slate-700/60 bg-slate-900/50 p-2 text-slate-300 transition hover:bg-slate-700 hover:text-white cursor-pointer"
                aria-label="Mes siguiente">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
            </button>
        </div>

        <input type="hidden" name="filter" value="{filter or ''}">

        <!-- Leyenda Interactiva en Grid (2 columnas en móvil, 4 en pantallas medianas/grandes) -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 rounded-xl border border-slate-700/40 bg-slate-900/50 p-2.5">
            {legend_html}
        </div>

        <!-- Grid del Calendario -->
        <div class="grid grid-cols-7 gap-1 text-center">
            {week_days_headers}
            {days_html}
        </div>
    </div>
    """
    return HTMLResponse(content=html)