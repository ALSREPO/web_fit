# backend/app/models/dashboard.py
# Definición de modelos Pydantic para la respuesta de los endpoints del Dashboard

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class ExerciseDetailItem(BaseModel):
    ejercicio: str = Field(..., description="Nombre del ejercicio")
    detalle: str = Field(..., description="Ej: '(85kgs x 5),(90kgs x 5)' o '5000m en 00:33:05, 6.62 min/km'")


class WorkoutSessionDetail(BaseModel):
    tipo_ejercicio: str = Field(..., description="Fuerza, Correr, Natación, Ciclismo, etc.")
    ejercicios: List[ExerciseDetailItem] = Field(default_factory=list)


class WorkoutCardResponse(BaseModel):
    has_workout: bool = Field(True, description="Indica si existen datos para esta tarjeta")
    fecha: Optional[date] = None
    date_label: Optional[str] = Field(None, description="Ej: 'Ayer · Jueves 8 May' o 'En 3 días · Domingo 11 May'")
    sessions: List[WorkoutSessionDetail] = Field(default_factory=list, description="Lista de disciplinas o sesiones del día")
    

# 1. Próximo Entrenamiento
class NextWorkoutResponse(BaseModel):
    has_workout: bool = Field(True, description="Indica si hay entrenamiento programado")
    date_label: Optional[str] = Field(None, description="Ej: 'Mañana · Viernes 16 May'")
    routine_name: Optional[str] = Field(None, description="Ej: 'Fuerza - Sentadillas' o 'Cardio - Correr'")
    exercises_count: int = 0
    exercises: List[str] = Field(default_factory=list)


# 2. Último Entrenamiento
class LastWorkoutResponse(BaseModel):
    fecha: date
    date_label: str = Field(..., description="Ej: 'Miércoles 14 May'")
    session_type: str = Field(..., description="Ej: 'Fuerza' o 'Cardio'")
    exercises_count: int
    duration_minutes: Optional[str] = Field(None, description="Tiempo transcurrido o duración en formato varchar")
    total_volume_kg: float = 0.0
    total_distance_m: float = 0.0


# 3. Resumen General y Gráfico Semanal
class DailyActivity(BaseModel):
    day_name: str = Field(..., description="Lun, Mar, Mié...")
    fecha: date
    has_workout: bool
    volume_kg: float = 0.0
    distance_km: float = 0.0


class MetricsSummaryResponse(BaseModel):
    period: str = Field(..., description="week | month | year | all")
    total_workouts: int
    total_volume_kg: float
    total_hours: float
    total_distance_km: float
    weekly_chart: List[DailyActivity] = Field(default_factory=list)


# 4. Calendario Compacto
class DayStatus(BaseModel):
    fecha: date
    has_workout: bool
    total_volume_kg: float = 0.0


class CompactCalendarResponse(BaseModel):
    year: int
    month: int
    days: List[DayStatus]