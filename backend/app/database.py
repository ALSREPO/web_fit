# app/database.py
# Conexión a DuckDB
# Módulo para la gestión de la base de datos DuckDB

import duckdb
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "fitnotes.duckdb"

def get_db():
    """Retorna una conexión activa a la base de datos DuckDB."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))
    init_db(conn)
    return conn

def init_db(conn: duckdb.DuckDBPyConnection):
    """Inicializa la secuencia y la tabla 'workout_logs' si no existen."""
    # 1. Creamos la secuencia para los IDs auto-incrementales
    conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_workout_id START 1;")

    # 2. Creamos la tabla asignando el default de la secuencia al ID
    conn.execute("""
        CREATE TABLE IF NOT EXISTS workout_logs (
            id BIGINT PRIMARY KEY DEFAULT nextval('seq_workout_id'),
            fecha DATE NOT NULL,
            exercise VARCHAR NOT NULL,
            category VARCHAR NOT NULL,
            weight DOUBLE,
            weight_unit VARCHAR,
            reps INT,
            distance DOUBLE,
            distance_unit VARCHAR,
            time_spent VARCHAR,
            comment VARCHAR
        )
    """)