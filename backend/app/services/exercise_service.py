# backend/app/services/exercise_service.py

from typing import List, Optional, Dict, Any
from datetime import date, timedelta
from backend.app.database import get_db
from backend.app.models.dashboard import ExerciseMaxWeightResponse, ExerciseSessionHistory, ExerciseSetDetail, ExerciseChartPoint


class ExerciseService:
    
    DIAS_ESP = ['lun', 'mar', 'mié', 'jue', 'vie', 'sáb', 'dom']
    MESES_ESP = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

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
    def get_exercise_chart_data(ejercicio_nombre: str, timeframe: str) -> List[Dict[str, Any]]:
        conn = get_db()
        try:
            today = date.today()
            series_dict = {}
            timeframe_list = []

            # 1. Generar serie temporal completa con etiquetas en español
            if timeframe == '7d': # Semana
                start_date = today - timedelta(days=6)
                curr = start_date
                while curr <= today:
                    key = curr.strftime('%Y-%m-%d')
                    label_str = ExerciseService.DIAS_ESP[curr.weekday()]
                    timeframe_list.append((key, label_str, curr))
                    curr += timedelta(days=1)

            elif timeframe == '30d': # Mes (30 días)
                start_date = today - timedelta(days=29)
                curr = start_date
                while curr <= today:
                    key = curr.strftime('%Y-%m-%d')
                    label_str = curr.strftime('%d') # "01", "02"...
                    timeframe_list.append((key, label_str, curr))
                    curr += timedelta(days=1)

            elif timeframe == '12m': # Año (Últimos 12 meses)
                for i in range(11, -1, -1):
                    y = today.year
                    m = today.month - i
                    while m <= 0:
                        m += 12
                        y -= 1
                    dt = date(y, m, 1)
                    key = dt.strftime('%Y-%m')
                    label_str = ExerciseService.MESES_ESP[dt.month - 1]
                    timeframe_list.append((key, label_str, dt))

            else: # 'all' - Histórico por años
                min_year_row = conn.execute(
                    "SELECT MIN(YEAR(fecha)) FROM v_workout WHERE LOWER(ejercicio) = LOWER(?) AND weight IS NOT NULL",
                    [ejercicio_nombre]
                ).fetchone()
                start_year = min_year_row[0] if min_year_row and min_year_row[0] else today.year
                
                for y in range(start_year, today.year + 1):
                    dt = date(y, 1, 1)
                    key = str(y)
                    label_str = str(y)
                    timeframe_list.append((key, label_str, dt))

            # Inicializar estrucutra con valor 0
            for key, label_str, dt_obj in timeframe_list:
                series_dict[key] = {
                    "period": key,
                    "label": label_str,
                    "fecha_ref": dt_obj.isoformat(),
                    "total_volume": 0.0,
                    "max_estimated_1rm": 0.0,
                    "max_weight": 0.0,
                    "total_reps": 0,
                    "total_sessions": 0
                }

            # 2. Consultar registros de DuckDB
            if timeframe == '7d':
                group_by = "STRFTIME('%Y-%m-%d', fecha)"
                date_filter = "WHERE fecha >= CURRENT_DATE - INTERVAL 6 DAY"
            elif timeframe == '30d':
                group_by = "STRFTIME('%Y-%m-%d', fecha)"
                date_filter = "WHERE fecha >= CURRENT_DATE - INTERVAL 29 DAY"
            elif timeframe == '12m':
                group_by = "STRFTIME('%Y-%m', fecha)"
                date_filter = "WHERE fecha >= CURRENT_DATE - INTERVAL 12 MONTH"
            else:
                group_by = "STRFTIME('%Y', fecha)"
                date_filter = ""

            query = f"""
                SELECT 
                    {group_by} AS group_key,
                    SUM(weight * reps) AS total_volume,
                    MAX(weight * (1 + reps / 30.0)) AS max_est_1rm,
                    MAX(weight) AS max_weight,
                    SUM(reps) AS total_reps,
                    COUNT(DISTINCT fecha) AS total_sessions
                FROM v_workout
                {date_filter} {"AND" if date_filter else "WHERE"} LOWER(ejercicio) = LOWER(?) AND weight IS NOT NULL
                GROUP BY group_key
            """

            rows = conn.execute(query, [ejercicio_nombre]).fetchall()

            for row in rows:
                g_key, vol, rm, max_w, reps, sessions = row
                g_key_str = str(g_key)
                if g_key_str in series_dict:
                    series_dict[g_key_str]["total_volume"] = round(float(vol or 0), 1)
                    series_dict[g_key_str]["max_estimated_1rm"] = round(float(rm or 0), 1)
                    series_dict[g_key_str]["max_weight"] = round(float(max_w or 0), 1)
                    series_dict[g_key_str]["total_reps"] = int(reps or 0)
                    series_dict[g_key_str]["total_sessions"] = int(sessions or 0)

            return list(series_dict.values())
        finally:
            conn.close()
    
    @staticmethod
    def get_all_exercises_ordered() -> List[Dict[str, Any]]:
        conn = get_db()
        try:
            # Selecciona todos los ejercicios distintos calculando el volumen reciente (últimos 90 días)
            query = """
                SELECT 
                    ejercicio,
                    SUM(CASE WHEN fecha >= CURRENT_DATE - INTERVAL 90 DAY THEN ((coalesce(weight,0)+1) * (coalesce(reps,0)+1)) + coalesce(distance,0) ELSE 0 END) AS recent_volume,
                    MAX(fecha) AS last_performed
                FROM v_workout
                WHERE ejercicio IS NOT NULL AND TRIM(ejercicio) != ''
                GROUP BY ejercicio
                ORDER BY recent_volume DESC, last_performed DESC, ejercicio ASC
            """
            rows = conn.execute(query).fetchall()
            return [
                {
                    "nombre": row[0],
                    "recent_volume": round(float(row[1] or 0), 1),
                    "last_performed": str(row[2]) if row[2] else None
                }
                for row in rows
            ]
        finally:
            conn.close()