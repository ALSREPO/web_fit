# backend/app/services/exercise_service.py

from typing import List, Optional
from datetime import date
from backend.app.database import get_db
from backend.app.models.dashboard import ExerciseMaxWeightResponse, ExerciseSessionHistory, ExerciseSetDetail, ExerciseChartPoint


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
    def get_exercise_history(
        ejercicio_nombre: str, 
        limit: int = 10, 
        offset: int = 0
    ) -> List[ExerciseSessionHistory]:
        """
        Obtiene el historial cronológico inverso paginado.
        """
        conn = get_db()
        try:
            # Subconsulta para obtener las fechas paginadas primero
            query = """
                WITH target_dates AS (
                    SELECT DISTINCT fecha
                    FROM v_workout
                    WHERE LOWER(ejercicio) = LOWER(?) AND weight IS NOT NULL
                    ORDER BY fecha DESC
                    LIMIT ? OFFSET ?
                )
                SELECT 
                    W.fecha,
                    W.weight,
                    W.reps,
                    W.comment
                FROM v_workout W
                JOIN target_dates D ON W.fecha = D.fecha
                WHERE LOWER(W.ejercicio) = LOWER(?) AND W.weight IS NOT NULL
                ORDER BY W.fecha DESC, W.id ASC
            """
            
            rows = conn.execute(query, [ejercicio_nombre, limit, offset, ejercicio_nombre]).fetchall()

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

    @staticmethod
    def get_exercise_chart_data(ejercicio_nombre: str, timeframe: str) -> List[dict]:
        """
        Calcula agregaciones por periodo (semana/30días, 12meses, histórico).
        timeframe opciones: '7d', '30d', '12m', 'all'
        """
        conn = get_db()
        try:
            # Definir filtro de fecha y agrupación según el timeframe
            if timeframe == '7d':
                date_filter = "WHERE fecha >= CURRENT_DATE - INTERVAL 7 DAY"
                group_by = "STRFTIME('%Y-%m-%d', fecha)"
                label_fmt = "STRFTIME('%d %b', fecha)"
            elif timeframe == '30d':
                date_filter = "WHERE fecha >= CURRENT_DATE - INTERVAL 30 DAY"
                group_by = "STRFTIME('%Y-%m-%d', fecha)"
                label_fmt = "STRFTIME('%d %b', fecha)"
            elif timeframe == '12m':
                date_filter = "WHERE fecha >= CURRENT_DATE - INTERVAL 12 MONTH"
                group_by = "STRFTIME('%Y-%m', fecha)"
                label_fmt = "STRFTIME('%b %Y', fecha)"
            else:  # 'all' - Histórico por año
                date_filter = ""
                group_by = "STRFTIME('%Y', fecha)"
                label_fmt = "STRFTIME('%Y', fecha)"

            query = f"""
                SELECT 
                    {group_by} AS group_key,
                    MIN(fecha) AS label_date,
                    SUM(weight * reps) AS total_volume,
                    MAX(weight * (1 + reps / 30.0)) AS max_est_1rm,
                    MAX(weight) AS max_weight,
                    SUM(reps) AS total_reps,
                    COUNT(DISTINCT fecha) AS total_sessions
                FROM v_workout
                {date_filter} {"AND" if date_filter else "WHERE"} LOWER(ejercicio) = LOWER(?) AND weight IS NOT NULL
                GROUP BY group_key
                ORDER BY group_key ASC
            """

            rows = conn.execute(query, [ejercicio_nombre]).fetchall()

            result = []
            for row in rows:
                g_key, label_date, vol, rm, max_w, reps, sessions = row
                result.append({
                    "period": str(g_key),
                    "label": str(label_date),
                    "total_volume": round(float(vol or 0), 1),
                    "max_estimated_1rm": round(float(rm or 0), 1),
                    "max_weight": round(float(max_w or 0), 1),
                    "total_reps": int(reps or 0),
                    "total_sessions": int(sessions or 0)
                })

            return result
        finally:
            conn.close()