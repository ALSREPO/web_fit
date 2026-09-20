# backend/app/services/exercise_service.py

from datetime import date
from typing import Optional, List
from backend.app.database import get_db
from backend.app.models.dashboard import ExerciseMaxWeightResponse, ExerciseSessionHistory, ExerciseSetDetail


class ExerciseService:
    
    @staticmethod
    def get_exercise_max_weight(ejercicio_nombre: str) -> ExerciseMaxWeightResponse:
        """
        Calcula el peso máximo y 1RM estimado para un ejercicio dentro
        de la ventana acotada de los últimos 3 meses.
        """
        conn = get_db()
        try:
            # 1. Obtener el registro con mayor peso en los últimos 3 meses
            # Usamos DATE_TRUNC o la fecha máxima del sistema como referencia
            query = """
                SELECT 
                    W.weight,
                    W.weight_unit,
                    W.reps,
                    W.fecha,
                    -- Fórmula de 1RM Estimado (Epley): Weight * (1 + Reps / 30)
                    ROUND(W.weight * (1 + (W.reps / 30.0)), 2) as estimated_1rm
                FROM v_workout W
                WHERE LOWER(W.ejercicio) = LOWER(?)
                  AND W.weight IS NOT NULL
                  AND W.fecha between (CURRENT_DATE - INTERVAL '3 months') and  CURRENT_DATE
                ORDER BY W.weight DESC, estimated_1rm DESC, W.fecha DESC
                LIMIT 1
            """
            
            row = conn.execute(query, [ejercicio_nombre]).fetchone()

            if not row:
                # Caso: No hay entrenamientos registrados en los últimos 3 meses
                return ExerciseMaxWeightResponse(
                    ejercicio=ejercicio_nombre,
                    period_months=3,
                    max_weight=None,
                    weight_unit="kg",
                    reps_at_max=None,
                    estimated_1rm=None,
                    last_performed_date=None,
                    has_recent_data=False
                )

            weight, unit, reps, fecha_max, est_1rm = row

            return ExerciseMaxWeightResponse(
                ejercicio=ejercicio_nombre,
                period_months=3,
                max_weight=float(weight),
                weight_unit=unit or "kg",
                reps_at_max=int(reps) if reps else None,
                estimated_1rm=float(est_1rm) if est_1rm else None,
                last_performed_date=fecha_max,
                has_recent_data=True
            )

        finally:
            conn.close()
    
    @staticmethod
    def get_exercise_history(ejercicio_nombre: str) -> List[ExerciseSessionHistory]:
        """
        Obtiene el historial cronológico inverso de un ejercicio específico,
        agrupando por fecha y desglosando las series de cada día.
        """
        conn = get_db()
        try:
            query = """
                SELECT 
                    W.fecha,
                    W.weight,
                    W.reps,
                    W.comment
                FROM v_workout W
                WHERE LOWER(W.ejercicio) = LOWER(?)
                  AND W.weight IS NOT NULL
                ORDER BY W.fecha DESC, W.id ASC
            """
            
            rows = conn.execute(query, [ejercicio_nombre]).fetchall()

            # Agrupar series por fecha
            sessions_dict = {}
            for row in rows:
                fecha_val, weight, reps, comment = row
                
                if fecha_val not in sessions_dict:
                    sessions_dict[fecha_val] = {
                        "fecha": fecha_val,
                        "sets": [],
                        "total_volume": 0.0
                    }
                
                w = float(weight) if weight else 0.0
                r = int(reps) if reps else 0
                
                sessions_dict[fecha_val]["sets"].append(
                    ExerciseSetDetail(
                        set_number=len(sessions_dict[fecha_val]["sets"]) + 1,
                        weight=w if w > 0 else None,
                        reps=r if r > 0 else None,
                        comment=comment
                    )
                )
                sessions_dict[fecha_val]["total_volume"] += (w * r)

            history = []
            for fecha_val, data in sessions_dict.items():
                history.append(
                    ExerciseSessionHistory(
                        fecha=fecha_val,
                        total_volume_kg=round(data["total_volume"], 2) if data["total_volume"] > 0 else None,
                        sets=data["sets"]
                    )
                )

            return history

        finally:
            conn.close()