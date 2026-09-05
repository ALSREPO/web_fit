# backend/app/services/dashboard_service.py
# Servicio de Agregación y Consulta de Datos para el Dashboard
# Módulo para obtener métricas, resúmenes y sugerencias de entrenamiento desde DuckDB

from datetime import date, datetime, timedelta
import calendar
from backend.app.database import get_db

class DashboardService:

    @staticmethod
    def get_last_workout():
        """Obtiene el resumen de la última sesión registrada en DuckDB."""
        conn = get_db()
        try:
            # Buscar la fecha más reciente
            latest_date_res = conn.execute("SELECT MAX(fecha) FROM workout_logs").fetchone()
            if not latest_date_res or not latest_date_res[0]:
                return None

            latest_date = latest_date_res[0]

            # Agregados de esa sesión concreta
            stats = conn.execute("""
                SELECT 
                    category,
                    COUNT(DISTINCT exercise) as exercises_count,
                    COALESCE(SUM(weight * reps), 0.0) as total_volume
                FROM workout_logs
                WHERE fecha = ?
                GROUP BY category
                ORDER BY COUNT(*) DESC
                LIMIT 1
            """, [latest_date]).fetchone()

            if not stats:
                return None

            return {
                "fecha": latest_date,
                "category": stats[0],
                "duration_minutes": None,  # Se calculará si existe time_spent
                "total_volume_kg": round(stats[2], 2),
                "exercises_count": stats[1]
            }
        finally:
            conn.close()

    @staticmethod
    def get_next_workout_suggestion():
        """Genera una estimación simple del próximo entrenamiento basado en la última categoría."""
        conn = get_db()
        try:
            latest = conn.execute("""
                SELECT category, MAX(fecha) as fecha 
                FROM workout_logs 
                GROUP BY category 
                ORDER BY fecha DESC 
                LIMIT 1
            """).fetchone()

            if not latest:
                return {
                    "eta_label": "Hoy",
                    "routine_name": "Sesión General",
                    "exercises": []
                }

            last_category, last_date = latest[0], latest[1]
            today = date.today()
            
            # Estimación simple de días
            diff_days = (today - last_date).days if isinstance(last_date, date) else 0

            if diff_days <= 0:
                eta_label = "Mañana"
            elif diff_days == 1:
                eta_label = "Hoy"
            else:
                eta_label = f"Hace {diff_days} días sin entrenar"

            # Ejercicios más habituales de esa categoría para mostrar como resumen
            exercises_res = conn.execute("""
                SELECT exercise 
                FROM workout_logs 
                WHERE category = ? 
                GROUP BY exercise 
                ORDER BY COUNT(*) DESC 
                LIMIT 4
            """, [last_category]).fetchall()

            exercises = [e[0] for e in exercises_res]

            return {
                "eta_label": eta_label,
                "routine_name": f"Rutina - {last_category}",
                "exercises": exercises
            }
        finally:
            conn.close()

    @staticmethod
    def get_metrics_summary(period: str = "month"):
        """Calcula métricas agregadas según el filtro (week, month, year, all)."""
        conn = get_db()
        try:
            where_clause = ""
            today = date.today()

            if period == "week":
                start_date = today - timedelta(days=7)
                where_clause = f"WHERE fecha >= '{start_date}'"
            elif period == "month":
                start_date = today - timedelta(days=30)
                where_clause = f"WHERE fecha >= '{start_date}'"
            elif period == "year":
                start_date = today - timedelta(days=365)
                where_clause = f"WHERE fecha >= '{start_date}'"
            else:  # "all"
                where_clause = ""

            query = f"""
                SELECT 
                    COUNT(DISTINCT fecha) as total_workouts,
                    COALESCE(SUM(weight * reps), 0.0) as total_volume,
                    COALESCE(SUM(distance), 0.0) as total_distance
                FROM workout_logs
                {where_clause}
            """
            res = conn.execute(query).fetchone()

            return {
                "period": period,
                "total_workouts": res[0] or 0,
                "total_volume_kg": round(res[1] or 0.0, 2),
                "total_hours": 0.0,  # Reservado si hay tiempo
                "total_distance_km": round(res[2] or 0.0, 2)
            }
        finally:
            conn.close()

    @staticmethod
    def get_compact_calendar(year: int, month: int):
        """Devuelve los días del mes y marca cuáles tuvieron entrenamiento."""
        conn = get_db()
        try:
            # Obtener días entrenados en ese mes/año
            rows = conn.execute("""
                SELECT 
                    fecha,
                    COALESCE(SUM(weight * reps), 0.0) as vol
                FROM workout_logs
                WHERE YEAR(fecha) = ? AND MONTH(fecha) = ?
                GROUP BY fecha
            """, [year, month]).fetchall()

            workout_map = {row[0]: row[1] for row in rows}

            # Generar lista de todos los días del mes
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