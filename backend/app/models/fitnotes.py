# app/models/fitnotes.py
# Esquema de Datos y Modelos Pydantic

from datetime import date, time as TimeType
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class FitNotesRecordBase(BaseModel):
    fecha: date = Field(..., description="Fecha de la serie/sesión (YYYY-MM-DD)")
    exercise: str = Field(..., description="Nombre del ejercicio")
    category: str = Field(..., description="Categoría asignada en FitNotes")
    weight: Optional[float] = Field(None, description="Peso levantado")
    weight_unit: Optional[str] = Field("kgs", description="Unidad de peso (kgs/lbs)")
    reps: Optional[int] = Field(None, description="Número de repeticiones")
    distance: Optional[float] = Field(None, description="Distancia (si aplica)")
    distance_unit: Optional[str] = Field(None, description="Unidad de distancia")
    time_spent: Optional[str] = Field(None, description="Tiempo de la serie/ejercicio")
    comment: Optional[str] = Field(None, description="Notas escritas en la serie")

    model_config = ConfigDict(from_attributes=True)

class FitNotesRecordCreate(FitNotesRecordBase):
    pass

class FitNotesRecordResponse(FitNotesRecordBase):
    id: int = Field(..., description="ID auto-incrementa generado por DuckDB")

# Modelo de resumen por sesión (agrupación diaria)
class WorkoutSetDetail(BaseModel):
    set_number: int
    weight: Optional[float]
    weight_unit: Optional[str]
    reps: Optional[int]
    comment: Optional[str]

class ExerciseInSession(BaseModel):
    exercise_name: str
    category: str
    sets: List[WorkoutSetDetail]
    total_volume: float
    max_weight: float

class WorkoutSession(BaseModel):
    fecha: date
    exercises_count: int
    total_sets: int
    total_volume: float
    exercises: List[ExerciseInSession]

class CSVUploadResponse(BaseModel):
    filename: str
    total_records: int
    message: str