# backend/app/services/day_detail_service.py
# Servicio especializado para el Detalle del Día
# Módulo para obtener el desglose completo de una sesión de entrenamiento

from datetime import date
from backend.app.database import get_db


class DayDetailService:
    """Servicio encargado de la lógica del detalle del día."""

    @staticmethod
    def _get_svg_ids_for_muscle(conn, muscle_name: str) -> list:
        """Obtiene los IDs SVG para un músculo específico desde la BD."""
        try:
            result = conn.execute("""
                SELECT svg_ids FROM muscle_svg_mapping
                WHERE LOWER(muscle_name) = LOWER(?)
            """, [muscle_name]).fetchone()
            
            if result:
                # Los IDs se guardan como cadena separada por comas
                svg_ids_str = result[0]
                return [id.strip() for id in svg_ids_str.split(",") if id.strip()]
            return []
        except:
            # Si hay error al consultar, retornar lista vacía
            return []

    @staticmethod
    def _format_spanish_date(d: date) -> str:
        """Formatea una fecha en español con día de la semana y mes."""
        days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        return f"{days[d.weekday()]} {d.day} {months[d.month - 1]}"

    @staticmethod
    def _format_duration(seconds: float | None) -> str | None:
        """Convierte segundos a formato legible (h:mm:ss o mm:ss o ss)."""
        if not seconds:
            return None
        total = int(round(seconds))
        hours, rem = divmod(total, 3600)
        minutes, secs = divmod(rem, 60)
        if hours:
            return f"{hours}h {minutes}m"
        if minutes:
            return f"{minutes}m {secs}s"
        return f"{secs}s"

    @staticmethod
    def _normalize_distance_km(distance) -> float:
        """Normaliza distancia a km (si es > 50, asume que está en metros)."""
        dist = distance or 0
        if dist > 50:
            return round(dist / 1000.0, 2)
        return round(dist, 2)

    @staticmethod
    def _format_set_detalle(row) -> str:
        """
        Formatea el detalle de una serie.
        row: (weight, weight_unit, reps, distance, distance_unit, time_spent, ritmo_min_km)
        """
        weight, weight_unit, reps, distance, distance_unit, time_spent, ritmo = row
        if weight is not None and reps is not None:
            return f"{int(weight)}{weight_unit or ''} x {reps}"
        parts = []
        if distance is not None:
            unit = f" {distance_unit}" if distance_unit else ""
            parts.append(f"{int(distance)}{unit}")
        if time_spent:
            parts.append(f"en {time_spent}")
        if ritmo:
            parts.append(f"{round(ritmo, 2)} min/km")
        return " ".join(parts) if parts else "—"

    @staticmethod
    def get_day_detail(target_date: date):
        """Obtiene el desglose completo de entrenamientos y músculos de un día."""
        conn = get_db()
        try:
            # 1. Obtener KPIs globales del día
            kpi_row = conn.execute("""
                SELECT
                    COALESCE(SUM(tiempo_segundos), 0) as duration_seconds,
                    COALESCE(SUM(volumen_total), 0) as total_volume_kg,
                    COALESCE(SUM(distance), 0) as total_distance
                FROM v_resumen_diario
                WHERE fecha = ?
            """, [target_date]).fetchone()

            # 2. Obtener todos los sets del día ordenados por ID
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

            # Si no hay ejercicios, retornar estructura vacía
            if not set_rows:
                return {
                    "has_workout": False,
                    "fecha": target_date,
                    "date_label": DayDetailService._format_spanish_date(target_date),
                    "duration_seconds": 0,
                    "duration_label": None,
                    "total_volume_kg": 0,
                    "total_distance_km": 0,
                    "sessions": [],
                    "muscles": []
                }

            # 3. Procesar KPIs
            duration_seconds = float(kpi_row[0] or 0)
            total_volume_kg = round(float(kpi_row[1] or 0), 2)
            total_distance_km = DayDetailService._normalize_distance_km(kpi_row[2])

            # 4. Obtener resumen de ejercicios
            detail_rows = conn.execute("""
                SELECT ejercicio, detalle_ejercicio
                FROM v_ejercicios_detalle
                WHERE fecha = ?
            """, [target_date]).fetchall()
            summary_map = {row[0]: row[1] or "" for row in detail_rows}

            # 5. Agrupar sets por tipo y ejercicio
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
                    "detalle": DayDetailService._format_set_detalle(
                        (weight, weight_unit, reps, distance, distance_unit, time_spent, ritmo)
                    )
                })

            # 6. Obtener KPIs por tipo de ejercicio
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

            # 7. Construir respuesta de sesiones
            sessions = []
            for tipo, session in sessions_map.items():
                kpi = kpi_by_type.get(tipo)
                sessions.append({
                    "tipo_ejercicio": tipo,
                    "duration_seconds": float(kpi[1]) if kpi else 0.0,
                    "total_volume_kg": round(float(kpi[2] or 0), 2) if kpi else 0.0,
                    "total_distance_km": DayDetailService._normalize_distance_km(kpi[3] if kpi else 0),
                    "exercises": [session["exercises"][name] for name in session["exercises_order"]]
                })

            # 8. Obtener músculos activados
            muscle_rows = conn.execute("""
                SELECT DISTINCT E.musculos, E.tipo_musculos
                FROM v_workout W
                INNER JOIN exercise_muscles E ON W.ejercicio = E.ejercicio
                WHERE W.ejercicio not in ('Correr', 'Natación', 'Ciclismo') and W.fecha = ?
            """, [target_date]).fetchall()

            muscles_map = {}
            for musculo, role in muscle_rows:
                if not musculo:
                    continue
                key = musculo.strip()
                existing = muscles_map.get(key)
                if existing is None or (role == "Principal" and existing["role"] != "Principal"):
                    # Obtener SVG IDs desde la BD
                    svg_ids = DayDetailService._get_svg_ids_for_muscle(conn, key)
                    muscles_map[key] = {
                        "musculo": key,
                        "role": role or "Asistencial",
                        "svg_ids": svg_ids
                    }

            muscles = sorted(
                muscles_map.values(),
                key=lambda m: (0 if m["role"] == "Principal" else 1, m["musculo"])
            )

            return {
                "has_workout": True,
                "fecha": target_date,
                "date_label": DayDetailService._format_spanish_date(target_date),
                "duration_seconds": duration_seconds,
                "duration_label": DayDetailService._format_duration(duration_seconds),
                "total_volume_kg": total_volume_kg,
                "total_distance_km": total_distance_km,
                "sessions": sessions,
                "muscles": muscles
            }
        finally:
            conn.close()
