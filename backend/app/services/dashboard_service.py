# backend/app/services/dashboard_service.py
# Servicio de Agregación y Consulta de Datos para el Dashboard
# Módulo para obtener métricas, resúmenes y sugerencias de entrenamiento desde DuckDB

from datetime import date, datetime, timedelta
import calendar
from calendar import monthrange
from collections import defaultdict
from backend.app.database import get_db

# Mapeo de nombres de músculo (exercise_muscles) a IDs del SVG frontal/trasero
MUSCLE_SVG_IDS = {
    "abdominales": ["abs"],
    "transverso del abdomen": ["abs"],
    "core": ["abs"],
    "hombros": ["shoulders-front", "shoulders-back"],
    "deltoides (hombros)": ["shoulders-front", "shoulders-back"],
    "deltoides": ["shoulders-front", "shoulders-back"],
    "deltoides anterior": ["shoulders-front"],
    "glúteos": ["glutes"],
    "cuádriceps": ["quads"],
    "isquiotibiales": ["hamstrings"],
    "gemelos": ["calves-front", "calves-back"],
    "dorsal ancho": ["lats"],
    "pectoral": ["chest"],
    "pectoral mayor": ["chest"],
    "pectoral superior": ["chest-upper"],
    "tríceps": ["triceps"],
    "bíceps": ["biceps"],
    "braquial": ["biceps"],
    "trapecio": ["traps-front", "traps-back"],
    "redondo mayor": ["teres"],
    "romboide": ["rhomboids"],
    "erectores espinales": ["erectors"],
}

class DashboardService:

    @staticmethod
    def _format_spanish_date(d: date) -> str:
        days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        return f"{days[d.weekday()]} {d.day} {months[d.month - 1]}"

    @staticmethod
    def _get_workout_card_data(is_past: bool):
        """
        Función unificada para obtener la tarjeta de entrenamiento pasada o futura.
        - is_past=True: Obtiene la fecha más reciente anterior a HOY (Último)
        - is_past=False: Obtiene la fecha más cercana mayor o igual a HOY (Siguiente)
        """
        conn = get_db()
        try:
            today = date.today()
            
            # 1. Determinar la fecha objetivo según el comparador
            if is_past:
                query_date = "SELECT MAX(fecha) FROM v_workout WHERE fecha < ?"
            else:
                query_date = "SELECT MIN(fecha) FROM v_workout WHERE fecha >= ?"

            date_res = conn.execute(query_date, [today]).fetchone()

            if not date_res or not date_res[0]:
                return {
                    "has_workout": False,
                    "fecha": None,
                    "date_label": None,
                    "sessions": []
                }

            target_date: date = date_res[0]

            # 2. Formatear etiqueta de fecha relativa (Ayer, Hoy, Mañana o número de días)
            diff_days = (target_date - today).days

            if diff_days == 0:
                rel_label = "Hoy"
            elif diff_days == 1:
                rel_label = "Mañana"
            elif diff_days == -1:
                rel_label = "Ayer"
            elif diff_days > 1:
                rel_label = f"En {diff_days} días"
            else:
                rel_label = f"Hace {abs(diff_days)} días"

            date_label = f"{rel_label} · {DashboardService._format_spanish_date(target_date)}"

            # 3. Obtener el detalle de ejercicios ordenados por tipo desde v_ejercicios_detalle
            rows = conn.execute("""
                SELECT tipo_ejercicio, ejercicio, detalle_ejercicio
                FROM v_ejercicios_detalle
                WHERE fecha = ?
                ORDER BY min_id ASC
            """, [target_date]).fetchall()

            # 4. Agrupar ejercicios por disciplina (tipo_ejercicio)
            sessions_map = {}
            for tipo, ej_name, detalle in rows:
                if tipo not in sessions_map:
                    sessions_map[tipo] = []
                sessions_map[tipo].append({
                    "ejercicio": ej_name,
                    "detalle": detalle
                })

            # Construir la estructura final de sesiones
            sessions = [
                {
                    "tipo_ejercicio": tipo,
                    "ejercicios": ejercicios
                }
                for tipo, ejercicios in sessions_map.items()
            ]

            return {
                "has_workout": True,
                "fecha": target_date,
                "date_label": date_label,
                "sessions": sessions
            }
        finally:
            conn.close()

    @staticmethod
    def get_last_workout():
        return DashboardService._get_workout_card_data(is_past=True)

    @staticmethod
    def get_next_workout():
        return DashboardService._get_workout_card_data(is_past=False)


    @staticmethod
    def get_summary(period: str = "week"):
        conn = get_db()
        try:
            today = date.today()
            where_clause = ""
            params = []

            # 1. Definir rangos de fecha según el periodo
            if period == "week":
                start_date = today - timedelta(days=today.weekday())
                end_date = start_date + timedelta(days=6)
                where_clause = "WHERE fecha BETWEEN ? AND ?"
                params = [start_date, end_date]

            elif period == "month":
                start_date = date(today.year, today.month, 1)
                _, last_day = monthrange(today.year, today.month)
                end_date = date(today.year, today.month, last_day)
                where_clause = "WHERE fecha BETWEEN ? AND ?"
                params = [start_date, end_date]

            elif period == "year":
                start_date = date(today.year, 1, 1)
                end_date = date(today.year, 12, 31)
                where_clause = "WHERE fecha BETWEEN ? AND ?"
                params = [start_date, end_date]

            elif period in ["all", "historico"]:
                where_clause = ""
                params = []

            # 2. KPIs Globales
            query_kpis = f"""
                SELECT 
                    COUNT(DISTINCT fecha) as days_count,
                    COALESCE(SUM(n_tipo_ejercicio), 0) as sessions_count,
                    COALESCE(SUM(volumen_total), 0) as total_volume_kg,
                    COALESCE(SUM(distance), 0) as total_distance
                FROM v_resumen_diario
                {where_clause}
            """
            kpi_row = conn.execute(query_kpis, params).fetchone()

            kpis = {
                "days_count": kpi_row[0] or 0,
                "sessions_count": kpi_row[1] or 0,
                "total_volume_kg": round(kpi_row[2] or 0, 2),
                "total_distance_km": round((kpi_row[3] or 0) / 1000.0, 2) if (kpi_row[3] and kpi_row[3] > 50) else round(kpi_row[3] or 0, 2)
            }

            # 3. Gráfico por Tiempo (chart_by_time) con agrupación dinámica
            chart_by_time = []

            if period == "week":
                days_es = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
                query_time = f"""
                    SELECT 
                        fecha,
                        COUNT(*) as sessions_count,
                        COALESCE(SUM(volumen_total), 0) as volume_kg,
                        COALESCE(SUM(distance), 0) as distance
                    FROM v_workout
                    {where_clause}
                    GROUP BY fecha
                """
                time_rows = conn.execute(query_time, params).fetchall()
                time_map = {row[0]: row for row in time_rows}

                for i in range(7):
                    current_day = start_date + timedelta(days=i)
                    if current_day in time_map:
                        r = time_map[current_day]
                        dist = r[3] or 0
                        chart_by_time.append({
                            "label": days_es[i],
                            "volume_kg": round(r[2] or 0, 2),
                            "distance_km": round(dist / 1000.0, 2) if dist > 50 else round(dist, 2),
                            "sessions_count": r[1]
                        })
                    else:
                        chart_by_time.append({
                            "label": days_es[i],
                            "volume_kg": 0,
                            "distance_km": 0,
                            "sessions_count": 0
                        })

            elif period == "month":
                query_time = f"""
                    SELECT 
                        STRFTIME(fecha, '%Y-%m-%d') as label,
                        COUNT(*) as sessions_count,
                        COALESCE(SUM(volumen_total), 0) as volume_kg,
                        COALESCE(SUM(distance), 0) as distance
                    FROM v_workout
                    {where_clause}
                    GROUP BY fecha
                    ORDER BY fecha ASC
                """
                time_rows = conn.execute(query_time, params).fetchall()
                for label, count, vol, dist in time_rows:
                    dist = dist or 0
                    chart_by_time.append({
                        "label": str(label),
                        "volume_kg": round(vol or 0, 2),
                        "distance_km": round(dist / 1000.0, 2) if dist > 50 else round(dist, 2),
                        "sessions_count": count
                    })

            elif period == "year":
                # Agrupado por Mes (01 a 12) rellenando los 12 meses
                months_es = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
                query_time = f"""
                    SELECT 
                        MONTH(fecha) as num_mes,
                        COUNT(*) as sessions_count,
                        COALESCE(SUM(volumen_total), 0) as volume_kg,
                        COALESCE(SUM(distance), 0) as distance
                    FROM v_workout
                    {where_clause}
                    GROUP BY MONTH(fecha)
                """
                time_rows = conn.execute(query_time, params).fetchall()
                time_map = {row[0]: row for row in time_rows}

                for m in range(1, 13):
                    if m in time_map:
                        r = time_map[m]
                        dist = r[3] or 0
                        chart_by_time.append({
                            "label": months_es[m - 1],
                            "volume_kg": round(r[2] or 0, 2),
                            "distance_km": round(dist / 1000.0, 2) if dist > 50 else round(dist, 2),
                            "sessions_count": r[1]
                        })
                    else:
                        chart_by_time.append({
                            "label": months_es[m - 1],
                            "volume_kg": 0,
                            "distance_km": 0,
                            "sessions_count": 0
                        })

            elif period in ["all", "historico"]:
                # Agrupado por Año (%Y)
                query_time = f"""
                    SELECT 
                        STRFTIME(fecha, '%Y') as label,
                        COUNT(*) as sessions_count,
                        COALESCE(SUM(volumen_total), 0) as volume_kg,
                        COALESCE(SUM(distance), 0) as distance
                    FROM v_workout
                    {where_clause}
                    GROUP BY STRFTIME(fecha, '%Y')
                    ORDER BY label ASC
                """
                time_rows = conn.execute(query_time, params).fetchall()
                for label, count, vol, dist in time_rows:
                    dist = dist or 0
                    chart_by_time.append({
                        "label": str(label),
                        "volume_kg": round(vol or 0, 2),
                        "distance_km": round(dist / 1000.0, 2) if dist > 50 else round(dist, 2),
                        "sessions_count": count
                    })

            # 4. Gráfico por Tipo (chart_by_type)
            query_type = f"""
                SELECT 
                    COALESCE(tipo_ejercicio, 'Otros') as label,
                    COUNT(*) as sessions_count,
                    COALESCE(SUM(volumen_total), 0) as volume_kg,
                    COALESCE(SUM(distance), 0) as distance
                FROM v_workout
                {where_clause}
                GROUP BY COALESCE(tipo_ejercicio, 'Otros')
                ORDER BY sessions_count DESC
            """
            type_rows = conn.execute(query_type, params).fetchall()

            chart_by_type = []
            for label, count, vol, dist in type_rows:
                dist = dist or 0
                chart_by_type.append({
                    "label": str(label),
                    "volume_kg": round(vol or 0, 2),
                    "distance_km": round(dist / 1000.0, 2) if dist > 50 else round(dist, 2),
                    "sessions_count": count
                })

            return {
                "period": period,
                "kpis": kpis,
                "chart_by_time": chart_by_time,
                "chart_by_type": chart_by_type
            }
        finally:
            conn.close()

    @staticmethod
    def get_compact_calendar(year: int, month: int):
        conn = get_db()
        try:
            rows = conn.execute("""
                SELECT DISTINCT
                    fecha, 
                    LOWER(tipo_ejercicio) as tipo 
                FROM v_workout
                WHERE YEAR(fecha) = ? AND MONTH(fecha) = ?
                ORDER BY fecha, LOWER(tipo_ejercicio)
            """, [year, month]).fetchall()

            # Mapeamos por fecha: { date(2026, 9, 10): {"types": ["fuerza", "carrera"]} }
            calendar_map = defaultdict(lambda: {"types": []})
            
            for row in rows:
                fecha_val, tipo_val = row[0], row[1]
                if tipo_val and tipo_val not in calendar_map[fecha_val]["types"]:
                    calendar_map[fecha_val]["types"].append(tipo_val)

            num_days = calendar.monthrange(year, month)[1]
            days_list = []

            for day in range(1, num_days + 1):
                current_date = date(year, month, day)
                day_data = calendar_map.get(current_date, {"types": []})
                
                days_list.append({
                    "date": current_date.isoformat(),  # 'YYYY-MM-DD'
                    "has_workout": len(day_data["types"]) > 0,
                    "types": day_data["types"]
                })

            return {
                "year": year,
                "month": month,
                "days": days_list
            }
        finally:
            conn.close()

    @staticmethod
    def _format_duration(seconds: float | None) -> str | None:
        if not seconds:
            return None
        total = int(round(seconds))
        hours, rem = divmod(total, 3600)
        minutes, secs = divmod(rem, 60)
        if hours:
            return f"{hours}h {minutes:02d}m"
        if minutes:
            return f"{minutes} min"
        return f"{secs}s"

    @staticmethod
    def _format_set_detalle(row) -> str:
        """row: weight, weight_unit, reps, distance, distance_unit, time_spent, ritmo_min_km"""
        weight, weight_unit, reps, distance, distance_unit, time_spent, ritmo = row
        if weight is not None and reps is not None:
            unit = weight_unit or "kgs"
            return f"{int(weight) if weight == int(weight) else weight}{unit} × {reps}"
        parts = []
        if distance is not None:
            unit = distance_unit or "m"
            parts.append(f"{int(distance)}{unit}")
        if time_spent:
            parts.append(f"en {time_spent}")
        if ritmo:
            parts.append(f"{round(ritmo, 2)} min/km")
        return " ".join(parts) if parts else "—"

    @staticmethod
    def _normalize_distance_km(distance) -> float:
        dist = distance or 0
        if dist > 50:
            return round(dist / 1000.0, 2)
        return round(dist, 2)

    @staticmethod
    def get_day_detail(target_date: date):
        conn = get_db()
        try:
            kpi_row = conn.execute("""
                SELECT
                    COALESCE(SUM(tiempo_segundos), 0) as duration_seconds,
                    COALESCE(SUM(volumen_total), 0) as total_volume_kg,
                    COALESCE(SUM(distance), 0) as total_distance
                FROM v_resumen_diario
                WHERE fecha = ?
            """, [target_date]).fetchone()

            set_rows = conn.execute("""
                SELECT
                    id,
                    tipo_ejercicio,
                    ejercicio,
                    weight,
                    weight_unit,
                    reps,
                    volumen_total,
                    distance,
                    distance_unit,
                    time_spent,
                    ritmo_min_km,
                    comment
                FROM v_workout
                WHERE fecha = ?
                ORDER BY id ASC
            """, [target_date]).fetchall()

            if not set_rows:
                return {
                    "has_workout": False,
                    "fecha": target_date,
                    "date_label": DashboardService._format_spanish_date(target_date),
                    "duration_seconds": 0,
                    "duration_label": None,
                    "total_volume_kg": 0,
                    "total_distance_km": 0,
                    "sessions": [],
                    "muscles": []
                }

            duration_seconds = float(kpi_row[0] or 0)
            total_volume_kg = round(float(kpi_row[1] or 0), 2)
            total_distance_km = DashboardService._normalize_distance_km(kpi_row[2])

            detail_rows = conn.execute("""
                SELECT ejercicio, detalle_ejercicio
                FROM v_ejercicios_detalle
                WHERE fecha = ?
            """, [target_date]).fetchall()
            summary_map = {row[0]: row[1] or "" for row in detail_rows}

            sessions_map = {}
            for row in set_rows:
                (
                    _id, tipo, ejercicio, weight, weight_unit, reps, volumen,
                    distance, distance_unit, time_spent, ritmo, comment
                ) = row
                tipo = tipo or "Otros"
                if tipo not in sessions_map:
                    sessions_map[tipo] = {
                        "tipo_ejercicio": tipo,
                        "exercises_order": [],
                        "exercises": {}
                    }
                session = sessions_map[tipo]
                if ejercicio not in session["exercises"]:
                    session["exercises_order"].append(ejercicio)
                    session["exercises"][ejercicio] = {
                        "ejercicio": ejercicio,
                        "tipo_ejercicio": tipo,
                        "summary": summary_map.get(ejercicio, ""),
                        "total_volume_kg": 0.0,
                        "sets": []
                    }
                exercise = session["exercises"][ejercicio]
                set_number = len(exercise["sets"]) + 1
                vol = float(volumen) if volumen is not None else 0.0
                exercise["total_volume_kg"] = round(exercise["total_volume_kg"] + vol, 2)
                exercise["sets"].append({
                    "set_number": set_number,
                    "weight": weight,
                    "weight_unit": weight_unit,
                    "reps": reps,
                    "distance": distance,
                    "distance_unit": distance_unit,
                    "time_spent": time_spent,
                    "volume_kg": round(vol, 2) if volumen is not None else None,
                    "comment": comment,
                    "detalle": DashboardService._format_set_detalle(
                        (weight, weight_unit, reps, distance, distance_unit, time_spent, ritmo)
                    )
                })

            session_kpis = conn.execute("""
                SELECT
                    COALESCE(tipo_ejercicio, 'Otros'),
                    COALESCE(SUM(tiempo_segundos), 0),
                    COALESCE(SUM(volumen_total), 0),
                    COALESCE(SUM(distance), 0)
                FROM v_resumen_diario
                WHERE fecha = ?
                GROUP BY COALESCE(tipo_ejercicio, 'Otros')
            """, [target_date]).fetchall()
            kpi_by_type = {row[0]: row for row in session_kpis}

            sessions = []
            for tipo, session in sessions_map.items():
                kpi = kpi_by_type.get(tipo)
                sessions.append({
                    "tipo_ejercicio": tipo,
                    "duration_seconds": float(kpi[1]) if kpi else 0.0,
                    "total_volume_kg": round(float(kpi[2] or 0), 2) if kpi else 0.0,
                    "total_distance_km": DashboardService._normalize_distance_km(kpi[3] if kpi else 0),
                    "exercises": [session["exercises"][name] for name in session["exercises_order"]]
                })

            muscle_rows = conn.execute("""
                SELECT DISTINCT E.musculos, E.tipo_musculos
                FROM v_workout W
                INNER JOIN exercise_muscles E ON W.ejercicio = E.ejercicio
                WHERE W.fecha = ?
            """, [target_date]).fetchall()

            muscles_map = {}
            for musculo, role in muscle_rows:
                if not musculo:
                    continue
                key = musculo.strip()
                existing = muscles_map.get(key)
                if existing is None or (role == "Principal" and existing["role"] != "Principal"):
                    muscles_map[key] = {
                        "musculo": key,
                        "role": role or "Asistencial",
                        "svg_ids": MUSCLE_SVG_IDS.get(key.lower(), [])
                    }

            muscles = sorted(
                muscles_map.values(),
                key=lambda m: (0 if m["role"] == "Principal" else 1, m["musculo"])
            )

            return {
                "has_workout": True,
                "fecha": target_date,
                "date_label": DashboardService._format_spanish_date(target_date),
                "duration_seconds": duration_seconds,
                "duration_label": DashboardService._format_duration(duration_seconds),
                "total_volume_kg": total_volume_kg,
                "total_distance_km": total_distance_km,
                "sessions": sessions,
                "muscles": muscles
            }
        finally:
            conn.close()