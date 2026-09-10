# backend/app/services/dashboard_service.py
# Servicio de Agregación y Consulta de Datos para el Dashboard
# Módulo para obtener métricas, resúmenes y sugerencias de entrenamiento desde DuckDB

from datetime import date, datetime, timedelta
import calendar
from calendar import monthrange
from collections import defaultdict
from backend.app.database import get_db

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