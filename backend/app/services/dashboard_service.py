# backend/app/services/dashboard_service.py
# Servicio de Agregación y Consulta de Datos para el Dashboard
# Módulo para obtener métricas, resúmenes y sugerencias de entrenamiento desde DuckDB

from datetime import date, datetime, timedelta
import calendar
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
    def get_metrics_summary(period: str = "month"):
        conn = get_db()
        try:
            today = date.today()
            
            # 1. Filtro del periodo general
            if period == "week":
                start_date = today - timedelta(days=7)
            elif period == "month":
                start_date = today - timedelta(days=30)
            elif period == "year":
                start_date = today - timedelta(days=365)
            else:
                start_date = date(2000, 1, 1)

            # Usar v_resumen_diario para conteo de sesiones totales y v_workout_sessions para métricas físicas
            total_workouts_res = conn.execute(f"""
                SELECT COALESCE(SUM(n_series), 0)
                FROM v_resumen_diario
                WHERE fecha >= '{start_date}' AND fecha < '{today}'
            """).fetchone()

            totals_res = conn.execute(f"""
                SELECT 
                    COALESCE(SUM(weight * reps), 0.0) as total_volume,
                    COALESCE(SUM(distance), 0.0) as total_distance
                FROM v_workout_sessions
                WHERE fecha >= '{start_date}' AND fecha < '{today}'
            """).fetchone()

            total_workouts = total_workouts_res[0] if total_workouts_res else 0
            total_volume = totals_res[0] if totals_res else 0.0
            total_distance = totals_res[1] if totals_res else 0.0

            # 2. Datos para el gráfico semanal (Lunes a Domingo de la semana actual)
            start_of_week = today - timedelta(days=today.weekday())
            day_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
            weekly_chart = []

            for i in range(7):
                current_day = start_of_week + timedelta(days=i)
                day_stats = conn.execute("""
                    SELECT COALESCE(SUM(weight * reps), 0.0), COUNT(*), COALESCE(SUM(distance), 0.0)
                    FROM v_workout_sessions
                    WHERE fecha = ?
                """, [current_day]).fetchone()

                vol = day_stats[0] or 0.0
                count = day_stats[1] or 0
                distance = day_stats[2] or 0.0

                weekly_chart.append({
                    "day_name": day_names[i],
                    "fecha": current_day,
                    "has_workout": count > 0,
                    "volume_kg": round(vol, 2),
                    "distance_km": round(distance / 1000.0, 2)
                })

            return {
                "period": period,
                "total_workouts": total_workouts,
                "total_volume_kg": round(total_volume, 2),
                "total_hours": 0.0,
                "total_distance_km": round(total_distance / 1000.0, 2),
                "weekly_chart": weekly_chart
            }
        finally:
            conn.close()

    @staticmethod
    def get_compact_calendar(year: int, month: int):
        conn = get_db()
        try:
            rows = conn.execute("""
                SELECT fecha, COALESCE(SUM(weight * reps), 0.0)
                FROM v_workout_sessions
                WHERE YEAR(fecha) = ? AND MONTH(fecha) = ?
                GROUP BY fecha
            """, [year, month]).fetchall()

            workout_map = {row[0]: row[1] for row in rows}
            num_days = calendar.monthrange(year, month)[1]
            days_list = []

            for day in range(1, num_days + 1):
                current_date = date(year, month, day)
                has_workout = current_date in workout_map
                days_list.append({
                    "fecha": current_date,
                    "has_workout": has_workout,
                    "total_volume_kg": round(workout_map.get(current_date, 0.0), 2)
                })

            return {
                "year": year,
                "month": month,
                "days": days_list
            }
        finally:
            conn.close()