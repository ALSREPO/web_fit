# backend/app/services/dashboard_service.py
# Servicio del Dashboard Principal
# Módulo para obtener próximo entrenamiento, último entrenamiento y resumen de métricas

from datetime import date, timedelta
from typing import Dict, Any, List
from backend.app.database import get_db

class DashboardService:

    DIAS_ESP = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    MESES_ESP = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    
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
    def get_summary(period: str = "week") -> Dict[str, Any]:
        conn = get_db()
        try:
            today = date.today()
            timeframe_list = []
            series_dict = {}

            where_clause = ""
            params = []

            # 1. Definir rango de fechas y generar la serie temporal completa
            if period in ["week", "7d"]:
                start_date = today - timedelta(days=6)
                end_date = today
                where_clause = "WHERE fecha BETWEEN ? AND ?"
                params = [start_date, end_date]

                curr = start_date
                while curr <= today:
                    key = curr.strftime('%Y-%m-%d')
                    label_str = DashboardService.DIAS_ESP[curr.weekday()]
                    timeframe_list.append((key, label_str))
                    curr += timedelta(days=1)

            elif period in ["month", "30d"]:
                start_date = today - timedelta(days=29)
                end_date = today
                where_clause = "WHERE fecha BETWEEN ? AND ?"
                params = [start_date, end_date]

                curr = start_date
                while curr <= today:
                    key = curr.strftime('%Y-%m-%d')
                    label_str = curr.strftime('%d')
                    timeframe_list.append((key, label_str))
                    curr += timedelta(days=1)

            elif period in ["year", "12m"]:
                start_date = date(today.year - 1, today.month, 1)  # Aprox hace 12 meses
                end_date = today
                # Para filtrar exactamente los últimos 12 meses completos en DuckDB:
                where_clause = "WHERE fecha >= CURRENT_DATE - INTERVAL 12 MONTH"
                params = []

                for i in range(11, -1, -1):
                    y = today.year
                    m = today.month - i
                    while m <= 0:
                        m += 12
                        y -= 1
                    dt = date(y, m, 1)
                    key = dt.strftime('%Y-%m')
                    label_str = DashboardService.MESES_ESP[dt.month - 1]
                    timeframe_list.append((key, label_str))

            elif period in ["all", "historico"]:
                where_clause = ""
                params = []

                min_year_row = conn.execute("SELECT MIN(YEAR(fecha)) FROM v_resumen_diario").fetchone()
                start_year = min_year_row[0] if min_year_row and min_year_row[0] else today.year

                for y in range(start_year, today.year + 1):
                    key = str(y)
                    label_str = str(y)
                    timeframe_list.append((key, label_str))

            # 2. Inicializar la estructura con valores a 0 para todos los periodos
            for key, label_str in timeframe_list:
                series_dict[key] = {
                    "label": label_str,
                    "volume_kg": 0.0,
                    "distance_km": 0.0,
                    "sessions_count": 0
                }

            # 3. KPIs Globales del periodo seleccionado
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
                "total_volume_kg": round(float(kpi_row[2] or 0), 2),
                "total_distance_km": round(float(kpi_row[3] or 0) / 1000.0, 2) if (kpi_row[3] and kpi_row[3] > 50) else round(float(kpi_row[3] or 0), 2)
            }

            # 4. Gráfico por Tiempo (chart_by_time)
            if period in ["week", "7d", "month", "30d"]:
                group_by = "STRFTIME('%Y-%m-%d', fecha)"
            elif period in ["year", "12m"]:
                group_by = "STRFTIME('%Y-%m', fecha)"
            else:  # all / historico
                group_by = "STRFTIME('%Y', fecha)"

            query_time = f"""
                SELECT 
                    {group_by} as group_key,
                    COUNT(*) as sessions_count,
                    COALESCE(SUM(volumen_total), 0) as volume_kg,
                    COALESCE(SUM(distance), 0) as distance
                FROM v_workout
                {where_clause}
                GROUP BY group_key
            """
            time_rows = conn.execute(query_time, params).fetchall()

            for row in time_rows:
                g_key, count, vol, dist = row
                g_key_str = str(g_key)
                if g_key_str in series_dict:
                    dist_val = dist or 0.0
                    series_dict[g_key_str]["sessions_count"] = count or 0
                    series_dict[g_key_str]["volume_kg"] = round(float(vol or 0), 2)
                    series_dict[g_key_str]["distance_km"] = round(float(dist_val / 1000.0), 2) if dist_val > 50 else round(float(dist_val), 2)

            chart_by_time = list(series_dict.values())

            # 5. Gráfico por Tipo de Ejercicio (chart_by_type)
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
                dist_val = dist or 0.0
                chart_by_type.append({
                    "label": str(label),
                    "volume_kg": round(float(vol or 0), 2),
                    "distance_km": round(float(dist_val / 1000.0), 2) if dist_val > 50 else round(float(dist_val), 2),
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