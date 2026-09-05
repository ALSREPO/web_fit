# backend/app/api/routers/dashboard.py
# Router FastAPI para endpoints del Dashboard
# Exposición de métricas, resúmenes y sugerencias de entrenamiento en formato JSON para el frontend.

from fastapi import APIRouter, Query, HTTPException
from datetime import date
from backend.app.services.dashboard_service import DashboardService
from backend.app.models.dashboard import (
    NextWorkoutResponse,
    LastWorkoutResponse,
    MetricsSummaryResponse,
    CompactCalendarResponse
)

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard"]
)

@router.get("/next-workout", response_model=NextWorkoutResponse)
async def get_next_workout():
    return DashboardService.get_next_workout_suggestion()

@router.get("/last-workout", response_model=LastWorkoutResponse)
async def get_last_workout():
    data = DashboardService.get_last_workout()
    if not data:
        raise HTTPException(status_code=404, detail="No hay entrenamientos registrados.")
    return data

@router.get("/summary", response_model=MetricsSummaryResponse)
async def get_summary(period: str = Query("month", regex="^(week|month|year|all)$")):
    return DashboardService.get_metrics_summary(period)

@router.get("/calendar-compact", response_model=CompactCalendarResponse)
async def get_calendar_compact(
    year: int = Query(default_factory=lambda: date.today().year),
    month: int = Query(default_factory=lambda: date.today().month, ge=1, le=12)
):
    return DashboardService.get_compact_calendar(year, month)