# backend/app/services/calendar_service.py
# Servicio especializado para consultas de Calendario
# Módulo para obtener el estado de días del calendario mensual

from datetime import date
from calendar import monthrange
from backend.app.database import get_db


class CalendarService:
    """Servicio encargado de la lógica del calendario compacto."""

    @staticmethod
    def get_compact_calendar(year: int, month: int):
        """
        Obtiene el estado de cada día del mes especificado.
        Retorna los días con entrenamientos y sus tipos/disciplinas.
        """
        conn = get_db()
        try:
            # Validar rango del mes
            if month < 1 or month > 12:
                month = date.today().month
            if year < 2000:
                year = date.today().year

            # Obtener el número de días del mes
            _, days_in_month = monthrange(year, month)

            # Consultar todos los días del mes que tienen entrenamientos
            rows = conn.execute("""
                SELECT DISTINCT
                    CAST(fecha AS TEXT) as date_str,
                    tipo_ejercicio
                FROM v_workout
                WHERE EXTRACT(YEAR FROM fecha) = ?
                  AND EXTRACT(MONTH FROM fecha) = ?
                ORDER BY fecha ASC
            """, [year, month]).fetchall()

            # Agrupar por fecha
            days_map = {}
            for date_str, tipo_ejercicio in rows:
                if date_str not in days_map:
                    days_map[date_str] = []
                if tipo_ejercicio and tipo_ejercicio not in days_map[date_str]:
                    days_map[date_str].append(tipo_ejercicio)

            # Construir la respuesta
            days = []
            for day in range(1, days_in_month + 1):
                formatted_month = str(month).zfill(2)
                formatted_day = str(day).zfill(2)
                date_str = f"{year}-{formatted_month}-{formatted_day}"

                days.append({
                    "date": date_str,
                    "has_workout": date_str in days_map,
                    "types": days_map.get(date_str, [])
                })

            return {
                "year": year,
                "month": month,
                "days": days
            }
        finally:
            conn.close()
