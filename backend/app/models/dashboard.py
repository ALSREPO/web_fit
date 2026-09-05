# backend/app/models/dashboard.py
# definición de modelos Pydantic para la respuesta de los endpoints del Dashboard

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

# 1. Próximo Entrenamiento
class NextWorkoutResponse(BaseModel):
    eta_label: str = Field(..., description="Ej: 'Mañana', 'En 2 días', 'Hoy'")
    routine_name: str = Field(..., description="Nombre sugerido o planificado")
    exercises: List[str] = Field(default_factory=list, description="Lista resumida de ejercicios")

# 2. Último Entrenamiento
class LastWorkoutResponse(BaseModel):
    fecha: date
    category: str
    duration_minutes: Optional[int] = Field(None, description="Duración estimada o parseada")
    total_volume_kg: float
    exercises_count: int

# 3. Resumen General
class MetricsSummaryResponse(BaseModel):
    period: str = Field(..., description="week | month | year | all")
    total_workouts: int
    total_volume_kg: float
    total_hours: float
    total_distance_km: float

# 4. Calendario Compacto
class DayStatus(BaseModel):
    fecha: date
    has_workout: bool
    total_volume_kg: float = 0.0

class CompactCalendarResponse(BaseModel):
    year: int
    month: int
    days: List[DayStatus]