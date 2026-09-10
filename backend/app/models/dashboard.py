# backend/app/models/dashboard.py
# Definición de modelos Pydantic para la respuesta de los endpoints del Dashboard

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


# 1. y 2. Próximo y Último Entrenamiento
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


# 3. Resumen General y Gráfico Semanal
class DailyActivity(BaseModel):
    day_name: str = Field(..., description="Lun, Mar, Mié...")
    fecha: date
    has_workout: bool
    volume_kg: float = 0.0
    distance_km: float = 0.0




class SummaryKpis(BaseModel):
    days_count: int = Field(..., description="Días distintos con entrenamiento")
    sessions_count: int = Field(..., description="Número total de sesiones/tipos completados")
    total_volume_kg: float = Field(..., description="Volumen total movido en fuerza")
    total_distance_km: float = Field(..., description="Distancia total recorrida en cardio")


class ChartDataPoint(BaseModel):
    label: str = Field(..., description="Ej: 'Lun', 'Semana 12', 'Ene' o 'Fuerza', 'Correr'")
    volume_kg: float = 0.0
    distance_km: float = 0.0
    sessions_count: int = 0


class MetricsSummaryResponse(BaseModel):
    period: str = Field(..., description="week | month | year | all")
    kpis: SummaryKpis
    chart_by_time: List[ChartDataPoint] = Field(default_factory=list)
    chart_by_type: List[ChartDataPoint] = Field(default_factory=list)


# 4. Calendario Compacto
class DayStatus(BaseModel):
    date: str  # Formato 'YYYY-MM-DD' para coincidir directamente con el frontend
    has_workout: bool
    types: List[str] = []

class CompactCalendarResponse(BaseModel):
    year: int
    month: int
    days: List[DayStatus]


# 5. Detalle del Día (Módulo 4)
class DaySetItem(BaseModel):
    set_number: int
    weight: Optional[float] = None
    weight_unit: Optional[str] = None
    reps: Optional[int] = None
    distance: Optional[float] = None
    distance_unit: Optional[str] = None
    time_spent: Optional[str] = None
    volume_kg: Optional[float] = None
    comment: Optional[str] = None
    detalle: str = ""


class DayExerciseItem(BaseModel):
    ejercicio: str
    tipo_ejercicio: str
    summary: str = ""
    total_volume_kg: float = 0.0
    sets: List[DaySetItem] = Field(default_factory=list)


class DaySessionDetail(BaseModel):
    tipo_ejercicio: str
    duration_seconds: float = 0.0
    total_volume_kg: float = 0.0
    total_distance_km: float = 0.0
    exercises: List[DayExerciseItem] = Field(default_factory=list)


class MuscleActivation(BaseModel):
    musculo: str
    role: str = Field(..., description="Principal o Asistencial")
    svg_ids: List[str] = Field(default_factory=list)


class DayDetailResponse(BaseModel):
    has_workout: bool
    fecha: Optional[date] = None
    date_label: Optional[str] = None
    duration_seconds: float = 0.0
    duration_label: Optional[str] = None
    total_volume_kg: float = 0.0
    total_distance_km: float = 0.0
    sessions: List[DaySessionDetail] = Field(default_factory=list)
    muscles: List[MuscleActivation] = Field(default_factory=list)