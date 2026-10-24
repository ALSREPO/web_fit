from typing import List, Optional, Dict, Any
from datetime import date, timedelta
from math import pow
from backend.app.database import get_db
from backend.app.models.dashboard import (
    CardioProjections,
    ExerciseMaxWeightResponse,
    ExerciseSessionHistory,
    ExerciseSetDetail,
    ExerciseChartPoint
)


class ExerciseService:
    
    DIAS_ESP = ['lun', 'mar', 'mié', 'jue', 'vie', 'sáb', 'dom']
    MESES_ESP = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

    @staticmethod
    def _format_seconds(seconds: float) -> str:
        seconds = int(round(seconds))
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}h {minutes:02d}m"
        return f"{minutes}m {secs:02d}s"

    @staticmethod
    def _calculate_riegel_time(base_dist_m: float, base_time_s: float, target_dist_m: float) -> str:
        if base_dist_m <= 0 or base_time_s <= 0:
            return "N/A"
        t2_seconds = base_time_s * pow(target_dist_m / base_dist_m, 1.06)
        return ExerciseService._format_seconds(t2_seconds)

    @staticmethod
    def get_exercise_max_weight(ejercicio_nombre: str) -> ExerciseMaxWeightResponse:
        conn = get_db()
        try:
            nombre_lower = ejercicio_nombre.lower()
            
            # Identificar disciplina exacta
            is_swimming = any(k in nombre_lower for k in ['nataci', 'natacion', 'swimming'])
            is_cycling = any(k in nombre_lower for k in ['ciclismo', 'bici', 'cycling', 'rodillo'])
            is_running = any(k in nombre_lower for k in ['correr', 'running', 'trot', 'carrera'])
            is_cardio = is_swimming or is_cycling or is_running

            if is_cardio:
                cardio_type = 'swimming' if is_swimming else ('cycling' if is_cycling else 'running')
                
                # Buscamos la sesión con el mejor ritmo / velocidad en los últimos 3 meses
                query_cardio = """
                    SELECT 
                        W.distance,
                        W.tiempo_segundos,
                        W.ritmo_min_km,
                        W.fecha
                    FROM v_workout W
                    WHERE LOWER(W.ejercicio) = LOWER(?)
                      AND W.distance IS NOT NULL
                      AND W.distance >= 200
                      AND W.tiempo_segundos IS NOT NULL
                      AND W.fecha BETWEEN (CURRENT_DATE - INTERVAL '3 months') AND CURRENT_DATE
                    ORDER BY W.ritmo_min_km ASC
                    LIMIT 1
                """
                row = conn.execute(query_cardio, [ejercicio_nombre]).fetchone()

                if not row:
                    return ExerciseMaxWeightResponse(
                        ejercicio=ejercicio_nombre,
                        period_months=3,
                        has_recent_data=False,
                        is_cardio=True,
                        cardio_type=cardio_type
                    )

                distance_m, time_s, ritmo_min_km, fecha = row
                best_pace = round(float(ritmo_min_km), 2) if ritmo_min_km else None

                # Configurar objetivos según el deporte
                if is_swimming:
                    # Natación: Distancias clave (400m, 800m, 1500m, 3800m) y ritmo en min/100m
                    # Convertimos ritmo min/km a min/100m para que sea natural en natación
                    if best_pace:
                        best_pace = round(best_pace / 10.0, 2)
                    pace_label = "min/100m"
                    
                    projections = CardioProjections(
                        pace_label=pace_label,
                        best_pace=best_pace,
                        target_1_label="100m",
                        target_1_time=ExerciseService._calculate_riegel_time(distance_m, time_s, 100),
                        target_2_label="400m",
                        target_2_time=ExerciseService._calculate_riegel_time(distance_m, time_s, 400),
                        target_3_label="800m",
                        target_3_time=ExerciseService._calculate_riegel_time(distance_m, time_s, 800),
                        target_4_label="1.500m",
                        target_4_time=ExerciseService._calculate_riegel_time(distance_m, time_s, 1500),
                        target_5_label="3.800m (Ironman)",
                        target_5_time=ExerciseService._calculate_riegel_time(distance_m, time_s, 3800)
                    )
                elif is_cycling:
                    # Ciclismo: Distancias clave (10km, 20km, 40km, 90km)
                    pace_label = "min/km"
                    projections = CardioProjections(
                        pace_label=pace_label,
                        best_pace=best_pace,
                        target_1_label="10 km",
                        target_1_time=ExerciseService._calculate_riegel_time(distance_m, time_s, 10000),
                        target_2_label="20 km",
                        target_2_time=ExerciseService._calculate_riegel_time(distance_m, time_s, 20000),
                        target_3_label="40 km (Crono)",
                        target_3_time=ExerciseService._calculate_riegel_time(distance_m, time_s, 40000),
                        target_4_label="90 km (Half)",
                        target_4_time=ExerciseService._calculate_riegel_time(distance_m, time_s, 90000),
                        target_5_label="180 K (Ironman)",
                        target_5_time=ExerciseService._calculate_riegel_time(distance_m, time_s, 180000)
                    )
                else:
                    # Running: 1k, 5k, 10k, 21k (las que teníamos)
                    pace_label = "min/km"
                    projections = CardioProjections(
                        pace_label=pace_label,
                        best_pace=best_pace,
                        target_1_label="1 km",
                        target_1_time=ExerciseService._calculate_riegel_time(distance_m, time_s, 1000),
                        target_2_label="5 km",
                        target_2_time=ExerciseService._calculate_riegel_time(distance_m, time_s, 5000),
                        target_3_label="10 km",
                        target_3_time=ExerciseService._calculate_riegel_time(distance_m, time_s, 10000),
                        target_4_label="21.1 k (Media)",
                        target_4_time=ExerciseService._calculate_riegel_time(distance_m, time_s, 21097.5),
                        target_5_label="42.2 k (Maratón)",
                        target_5_time=ExerciseService._calculate_riegel_time(distance_m, time_s, 42195.0)
                    )

                return ExerciseMaxWeightResponse(
                    ejercicio=ejercicio_nombre,
                    period_months=3,
                    has_recent_data=True,
                    is_cardio=True,
                    cardio_type=cardio_type,
                    cardio_projections=projections,
                    last_performed_date=str(fecha)
                )

            else:
                # --- LÓGICA FUERZA ---
                query_fuerza = """
                    SELECT 
                        W.weight,
                        W.weight_unit,
                        W.reps,
                        W.fecha,
                        ROUND(W.weight * (1 + (W.reps / 30.0)), 2) as estimated_1rm
                    FROM v_workout W
                    WHERE LOWER(W.ejercicio) = LOWER(?)
                      AND W.weight IS NOT NULL
                      AND W.fecha BETWEEN (CURRENT_DATE - INTERVAL '3 months') AND CURRENT_DATE
                    ORDER BY W.weight DESC, estimated_1rm DESC, W.fecha DESC
                    LIMIT 1
                """
                row = conn.execute(query_fuerza, [ejercicio_nombre]).fetchone()

                if not row:
                    return ExerciseMaxWeightResponse(
                        ejercicio=ejercicio_nombre,
                        period_months=3,
                        has_recent_data=False,
                        is_cardio=False
                    )

                weight, unit, reps, fecha_max, est_1rm = row

                return ExerciseMaxWeightResponse(
                    ejercicio=ejercicio_nombre,
                    period_months=3,
                    has_recent_data=True,
                    is_cardio=False,
                    max_weight=float(weight),
                    weight_unit=unit or "kg",
                    reps_at_max=int(reps) if reps else None,
                    estimated_1rm=float(est_1rm) if est_1rm else None,
                    last_performed_date=str(fecha_max)
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
        Obtiene el historial cronológico inverso paginado (Soporta fuerza y cardio).
        """
        conn = get_db()
        try:
            query = """
                WITH target_dates AS (
                    SELECT DISTINCT fecha
                    FROM v_workout
                    WHERE LOWER(ejercicio) = LOWER(?) AND 
                        (coalesce(weight,0) != 0 or
                         coalesce(reps,0) != 0 or
                         coalesce(distance,0) != 0 or
                         coalesce(tiempo_segundos,0) != 0
                        )
                    ORDER BY fecha DESC
                    LIMIT ? OFFSET ?
                )
                SELECT 
                    W.fecha,
                    W.weight,
                    W.reps,
                    W.comment,
                    W.distance,
                    W.distance_unit,
                    W.tiempo_segundos,
                    W.ritmo_min_km
                FROM v_workout W
                JOIN target_dates D ON W.fecha = D.fecha
                WHERE LOWER(W.ejercicio) = LOWER(?) AND 
                        (coalesce(W.weight,0) != 0 or
                         coalesce(W.reps,0) != 0 or
                         coalesce(W.distance,0) != 0 or
                         coalesce(W.tiempo_segundos,0) != 0
                        )
                ORDER BY W.fecha DESC, W.id ASC
            """
            
            rows = conn.execute(query, [ejercicio_nombre, limit, offset, ejercicio_nombre]).fetchall()

            sessions_dict = {}
            for row in rows:
                (
                    fecha_val, weight, reps, comment,
                    dist, dist_unit, t_seg, ritmo
                ) = row
                
                if fecha_val not in sessions_dict:
                    sessions_dict[fecha_val] = {
                        "fecha": fecha_val,
                        "sets": [],
                        "total_volume": 0.0,
                        "total_distance": 0.0
                    }
                
                w = float(weight) if weight else 0.0
                r = int(reps) if reps else 0
                d = float(dist) if dist else 0.0
                
                sessions_dict[fecha_val]["sets"].append(
                    ExerciseSetDetail(
                        set_number=len(sessions_dict[fecha_val]["sets"]) + 1,
                        weight=w if w > 0 else None,
                        reps=r if r > 0 else None,
                        comment=comment,
                        distance=d if d > 0 else None,
                        distance_unit=dist_unit if dist else None,
                        tiempo_segundos=float(t_seg) if t_seg else None,
                        ritmo_min_km=ritmo if ritmo else None
                    )
                )
                sessions_dict[fecha_val]["total_volume"] += (w * r)
                sessions_dict[fecha_val]["total_distance"] += d

            history = []
            for fecha_val, data in sessions_dict.items():
                history.append(
                    ExerciseSessionHistory(
                        fecha=fecha_val,
                        total_volume_kg=round(data["total_volume"], 2) if data["total_volume"] > 0 else None,
                        total_distance=round(data["total_distance"], 2) if data["total_distance"] > 0 else None,
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

            # 1. Generar serie temporal completa
            if timeframe == '7d':
                start_date = today - timedelta(days=6)
                curr = start_date
                while curr <= today:
                    key = curr.strftime('%Y-%m-%d')
                    label_str = ExerciseService.DIAS_ESP[curr.weekday()]
                    timeframe_list.append((key, label_str, curr))
                    curr += timedelta(days=1)

            elif timeframe == '30d':
                start_date = today - timedelta(days=29)
                curr = start_date
                while curr <= today:
                    key = curr.strftime('%Y-%m-%d')
                    label_str = curr.strftime('%d')
                    timeframe_list.append((key, label_str, curr))
                    curr += timedelta(days=1)

            elif timeframe == '12m':
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

            else:  # 'all'
                min_year_row = conn.execute(
                    "SELECT MIN(YEAR(fecha)) FROM v_workout WHERE LOWER(ejercicio) = LOWER(?)",
                    [ejercicio_nombre]
                ).fetchone()
                start_year = min_year_row[0] if min_year_row and min_year_row[0] else today.year
                
                for y in range(start_year, today.year + 1):
                    dt = date(y, 1, 1)
                    key = str(y)
                    label_str = str(y)
                    timeframe_list.append((key, label_str, dt))

            # Inicializar estructura
            for key, label_str, dt_obj in timeframe_list:
                series_dict[key] = {
                    "period": key,
                    "label": label_str,
                    "fecha_ref": dt_obj.isoformat(),
                    "total_volume": 0.0,
                    "max_estimated_1rm": 0.0,
                    "max_weight": 0.0,
                    "total_reps": 0,
                    "total_sessions": 0,
                    "total_distance": 0.0,
                    "total_time_seconds": 0.0,
                    "avg_ritmo_min_km": 0.0
                }

            # 2. Consultar registros DuckDB (Removido 'AND weight IS NOT NULL' para incluir cardio)
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
                    SUM(coalesce(weight, 0) * coalesce(reps, 0)) AS total_volume,
                    MAX(CASE WHEN weight IS NOT NULL THEN weight * (1 + coalesce(reps, 0) / 30.0) ELSE 0 END) AS max_est_1rm,
                    MAX(coalesce(weight, 0)) AS max_weight,
                    SUM(coalesce(reps, 0)) AS total_reps,
                    COUNT(DISTINCT fecha) AS total_sessions,
                    SUM(coalesce(distance, 0)) AS total_distance,
                    SUM(coalesce(tiempo_segundos, 0)) AS total_time_seconds,
                    AVG(coalesce(ritmo_min_km, 0)) AS avg_ritmo_min_km
                FROM v_workout
                {date_filter} {"AND" if date_filter else "WHERE"} LOWER(ejercicio) = LOWER(?)
                GROUP BY group_key
            """

            rows = conn.execute(query, [ejercicio_nombre]).fetchall()

            for row in rows:
                g_key, vol, rm, max_w, reps, sessions, dist, t_seg, avg_ritmo = row
                g_key_str = str(g_key)
                if g_key_str in series_dict:
                    series_dict[g_key_str]["total_volume"] = round(float(vol or 0), 1)
                    series_dict[g_key_str]["max_estimated_1rm"] = round(float(rm or 0), 1)
                    series_dict[g_key_str]["max_weight"] = round(float(max_w or 0), 1)
                    series_dict[g_key_str]["total_reps"] = int(reps or 0)
                    series_dict[g_key_str]["total_sessions"] = int(sessions or 0)
                    series_dict[g_key_str]["total_distance"] = round(float(dist or 0), 2)
                    series_dict[g_key_str]["total_time_seconds"] = round(float(t_seg or 0), 1)
                    series_dict[g_key_str]["avg_ritmo_min_km"] = round(float(avg_ritmo or 0), 2)

            return list(series_dict.values())
        finally:
            conn.close()
    
    @staticmethod
    def get_all_exercises_ordered() -> List[Dict[str, Any]]:
        conn = get_db()
        try:
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