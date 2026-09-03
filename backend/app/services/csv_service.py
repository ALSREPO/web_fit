# app/services/csv_service.py
# Servicio de Carga y Parseo CSV
# Módulo para el manejo de archivos CSV y su almacenamiento en DuckDB

import duckdb
import pandas as pd
import numpy as np
from pathlib import Path
from backend.app.database import get_db

class CSVService:
    @staticmethod
    def parse_and_store_csv(file_path: Path) -> int:
        """Lee e ingiere las filas del archivo CSV especificado en DuckDB."""
        if not file_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

        conn = get_db()
        try:
            # Reemplazar tabla de logs con los datos nuevos del CSV parseado
            conn.execute("TRUNCATE TABLE workout_logs")
            
            query = f"""
                INSERT INTO workout_logs (fecha, exercise, category, weight, weight_unit, reps, distance, distance_unit, time_spent, comment)
                SELECT 
                    TRY_CAST("Date" AS DATE) AS fecha,
                    "Exercise" AS exercise,
                    "Category" AS category,
                    TRY_CAST("Weight" AS DOUBLE) AS weight,
                    "Weight Unit" AS weight_unit,
                    TRY_CAST("Reps" AS INT) AS reps,
                    TRY_CAST("Distance" AS DOUBLE) AS distance,
                    "Distance Unit" AS distance_unit,
                    "Time" AS time_spent,
                    "Comment" AS comment
                FROM read_csv_auto('{str(file_path)}')
            """
            conn.execute(query)
            
            # Obtener total de registros insertados
            total_records = conn.execute("SELECT COUNT(*) FROM workout_logs").fetchone()[0]
            return total_records
        finally:
            conn.close()

    @staticmethod
    def get_latest_csv_file(upload_dir: Path) -> Path | None:
        """Devuelve la ruta del archivo CSV más reciente en la carpeta de subidas."""
        csv_files = sorted(upload_dir.glob("*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
        return csv_files[0] if csv_files else None

    @staticmethod
    def get_all_records(limit: int = 100):
        """Consulta los registros de la base de datos DuckDB."""
        conn = get_db()
        try:
            df = conn.execute("""
                SELECT 
                    id,
                    fecha, exercise, category, weight, weight_unit, reps, 
                    distance, distance_unit, time_spent, comment
                FROM workout_logs
                ORDER BY fecha DESC, id DESC
                LIMIT ?
            """, [limit]).df()
            
            if 'fecha' in df.columns:
                df['fecha'] = df['fecha'].astype(str)
            
            # Reemplazamos np.nan y pd.NA de forma explícita antes de to_dict
            df = df.replace({np.nan: None})
            
            return df.to_dict(orient="records")
        finally:
            conn.close()