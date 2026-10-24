# app/database.py
# Conexión a DuckDB
# Módulo optimizado para la gestión de la base de datos DuckDB

import duckdb
import json
from pathlib import Path
from contextlib import contextmanager
from config import DATA_DIR

DB_PATH = DATA_DIR / "fitnotes.duckdb"

def get_db(solo_lectura: bool = True):
  """Fábrica de dependencias para FastAPI.
  Permite alternar entre modo lectura o lectura/escritura.
  """
  def _dependency():
    # Asegura que la carpeta data existe si vamos a escribir
    if not solo_lectura:
      DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(str(DB_PATH), read_only=solo_lectura)
    try:
      yield conn
    finally:
      conn.close()

  return _dependency


def init_db(conn: duckdb.DuckDBPyConnection):
    """Inicializa la secuencia y la tabla 'workout_logs' si no existen."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))

    try:
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

        # 3. Tabla 'exercise_muscles'
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exercise_muscles (
                ejercicio VARCHAR NOT NULL,
                tipo_ejercicio VARCHAR NOT NULL,
                musculos VARCHAR NOT NULL,
                tipo_musculos VARCHAR NOT NULL
            )
        """)

        # 4. Tabla de mapeo 'muscle_svg_mapping' para asociar músculos con IDs SVG
        conn.execute("""
            CREATE TABLE IF NOT EXISTS muscle_svg_mapping (
                muscle_name VARCHAR NOT NULL PRIMARY KEY,
                svg_ids VARCHAR NOT NULL
            )
        """)

        # 5. RECARGA AUTOMÁTICA DESDE EL JSON (Catálogo siempre actualizado)
        seed_file = DATA_DIR / "exercises_seed.json"
        if seed_file.exists():
            with open(seed_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Vaciamos el catálogo anterior para evitar duplicados
                conn.execute("TRUNCATE TABLE exercise_muscles;")
                conn.execute("TRUNCATE TABLE muscle_svg_mapping;")
                
                # Insertamos los datos frescos del JSON
                conn.executemany("""
                    INSERT INTO exercise_muscles (ejercicio, tipo_ejercicio, musculos, tipo_musculos)
                    VALUES (?, ?, ?, ?)
                """, data["exercises"])
                
                conn.executemany("""
                    INSERT INTO muscle_svg_mapping (muscle_name, svg_ids)
                    VALUES (?, ?)
                """, data["muscle_svg"])
        
        
        # 6. Crea las vistas para consultas de logs completos y sesiones
        
        # 6.1. Vista base
        conn.execute("""
            CREATE VIEW IF NOT EXISTS v_workout AS
            SELECT 
                W.id, 
                W.fecha,
                E.tipo_ejercicio,
                W.exercise as ejercicio, 
                W.weight, 
                W.weight_unit, 
                W.reps, 
                W.weight * W.reps AS volumen_total,
                W.distance, 
                W.distance_unit, 
                W.time_spent, 
                EXTRACT(epoch FROM W.time_spent::INTERVAL)  as tiempo_segundos,
                round((W.distance / 1000) / (EXTRACT(epoch FROM W.time_spent::INTERVAL) /3600), 2) AS velocidad_km_hora,
                COALESCE(ROUND((EXTRACT(epoch FROM W.time_spent::INTERVAL) / 60) / (NULLIF(W.distance, 0) / 1000), 2),0) AS ritmo_min_km,
                W.comment
            FROM workout_logs W 
            LEFT JOIN (
                SELECT DISTINCT ejercicio, tipo_ejercicio 
                FROM exercise_muscles
            ) E 
                ON W.exercise = E.ejercicio
            ORDER BY W.id;
        """)


        # 6.2. Vista para agrupar sesiones distintas por fecha
        conn.execute("""
            CREATE VIEW IF NOT EXISTS v_resumen_diario AS
            WITH workout_base AS (
                -- 1. Unimos el log con los tipos de ejercicio
                SELECT 
                    W.id,
                    W.fecha,
                    W.ejercicio,
                    W.tipo_ejercicio,
                    sum(volumen_total) as volumen_total,
                    sum(tiempo_segundos) as tiempo_segundos,
                    sum(distance) as distance
                FROM v_workout W
                group by W.id,
                        W.fecha,
                        W.ejercicio,
                        W.tipo_ejercicio
                order by W.id
            )
            SELECT 
                fecha,
                tipo_ejercicio,
                -- Contamos cuántos ejercicios/series componen esta sesión específica
                COUNT(distinct tipo_ejercicio) AS n_tipo_ejercicio,
                COUNT(distinct ejercicio) AS n_ejercicios,
                COUNT(*) AS n_series,
                sum(volumen_total) as volumen_total,
                sum(tiempo_segundos) as tiempo_segundos,
                sum(distance) as distance,
                round(sum(distance/1000)/sum(tiempo_segundos)*3600, 2) as velocidad_km_hora,
                round(sum(tiempo_segundos)/60/sum(distance)*1000, 2) as ritmo_min_km,
                -- Lista los ejercicios incluidos en esta sesión concreta
                STRING_AGG(DISTINCT ejercicio, ', ') AS ejercicios_realizados
            FROM workout_base
            GROUP BY 
                fecha,
                tipo_ejercicio
            ORDER BY fecha DESC, tipo_ejercicio;
        """)

        # 6.3. Vista para detallar los ejercicios de una sesión específica (por fecha)
        conn.execute("""
            CREATE VIEW IF NOT EXISTS v_ejercicios_detalle AS
            WITH orden_ejercicios as (
                select fecha, ejercicio, min(id) as min_id
                from v_workout
                group by fecha, ejercicio
                ) 
            select O.min_id
                , W.fecha
                , W.tipo_ejercicio
                , W.ejercicio
                , CASE WHEN W.tipo_ejercicio = 'Fuerza' 
                            THEN STRING_AGG(concat('(',W.weight::INT, W.weight_unit,' x ', W.reps, ')'), ',') 
                        ELSE STRING_AGG(concat('',W.distance::INT, W.distance_unit, ' en ', W.time_spent, ', ', round(W.ritmo_min_km, 2), ' min/km'), ', ') 
                END as detalle_ejercicio
            from v_workout W
                INNER JOIN orden_ejercicios O
                    ON W.fecha = O.fecha AND 
                    W.ejercicio = O.ejercicio
            group by O.min_id
                , W.fecha
                , W.tipo_ejercicio
                , W.ejercicio
            order by O.min_id;
        """)
    finally:
        conn.close()

conn = get_db(solo_lectura=False)
init_db(conn)

"""


workout_logs
┌───────┬────────────┬───────────────┬────────────────┬────────┬─────────────┬───────┬──────────┬───────────────┬────────────┬─────────────┐
│  id   │   fecha    │   exercise    │    category    │ weight │ weight_unit │ reps  │ distance │ distance_unit │ time_spent │   comment   │
│ int64 │    date    │    varchar    │    varchar     │ double │   varchar   │ int32 │  double  │    varchar    │  varchar   │   varchar   │
├───────┼────────────┼───────────────┼────────────────┼────────┼─────────────┼───────┼──────────┼───────────────┼────────────┼─────────────┤
│ 31944 │ 2026-09-04 │ Natación      │ Cardio         │        │             │       │   7010.0 │ m             │ 00:45:51   │ 160-175     │
│ 31945 │ 2026-09-04 │ Sentadillas   │ Espalda_pierna │   85.0 │ kgs         │     5 │          │               │            │             │
│ 31946 │ 2026-09-04 │ Sentadillas   │ Espalda_pierna │   85.0 │ kgs         │     5 │          │               │            │             │
│ 31947 │ 2026-09-04 │ Sentadillas   │ Espalda_pierna │   90.0 │ kgs         │     5 │          │               │            │             │
│ 31948 │ 2026-09-04 │ Press militar │ Hombros        │   40.0 │ kgs         │     5 │          │               │            │             │
│ 31949 │ 2026-09-04 │ Press militar │ Hombros        │   45.0 │ kgs         │     5 │          │               │            │ Intenso     │
│ 31950 │ 2026-09-04 │ Press militar │ Hombros        │   45.0 │ kgs         │     5 │          │               │            │ Muy intenso │
│ 31951 │ 2026-09-04 │ Press banca   │ Pecho          │   65.0 │ kgs         │     5 │          │               │            │             │
│ 31952 │ 2026-09-04 │ Press banca   │ Pecho          │   65.0 │ kgs         │     5 │          │               │            │             │
│ 31953 │ 2026-09-04 │ Press banca   │ Pecho          │   70.0 │ kgs         │     5 │          │               │            │             │
│ 31954 │ 2026-09-04 │ Chin Up       │ Espalda        │    0.0 │ kgs         │    15 │          │               │            │             │
│ 31955 │ 2026-09-04 │ Chin Up       │ Espalda        │    0.0 │ kgs         │    15 │          │               │            │             │
│ 31956 │ 2026-09-04 │ Dominadas     │ Espalda        │    0.0 │ kgs         │    15 │          │               │            │             │
│ 31957 │ 2026-09-04 │ Correr        │ Cardio         │        │             │       │   5000.0 │ m             │ 00:33:05   │ 161-172     │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

v_workout
┌───────┬────────────┬────────────────┬───────────────┬────────┬─────────────┬───────┬───────────────┬──────────┬───────────────┬────────────┬─────────────────┬───────────────────┬───────────────────┬─────────────┐
│  id   │   fecha    │ tipo_ejercicio │   exercise    │ weight │ weight_unit │ reps  │ volumen_total │ distance │ distance_unit │ time_spent │ tiempo_segundos │ velocidad_km_hora │   ritmo_min_km    │   comment   │
│ int64 │    date    │    varchar     │    varchar    │ double │   varchar   │ int32 │    double     │  double  │    varchar    │  varchar   │     double      │      double       │      double       │   varchar   │
├───────┼────────────┼────────────────┼───────────────┼────────┼─────────────┼───────┼───────────────┼──────────┼───────────────┼────────────┼─────────────────┼───────────────────┼───────────────────┼─────────────┤
│  2448 │ 2026-12-04 │ Natación       │ Natación      │        │             │       │               │   7010.0 │ m             │ 00:45:51   │          2751.0 │  9.17339149400218 │ 6.540656205420828 │ 160-175     │
│  2449 │ 2026-12-04 │ Correr         │ Correr        │        │             │       │               │   5000.0 │ m             │ 00:33:05   │          1985.0 │  9.06801007556675 │ 6.616666666666667 │ 161-172     │
│  2450 │ 2026-12-04 │ Fuerza         │ Sentadillas   │   85.0 │ kgs         │     5 │         425.0 │          │               │            │                 │                   │                   │             │
│  2451 │ 2026-12-04 │ Fuerza         │ Sentadillas   │   85.0 │ kgs         │     5 │         425.0 │          │               │            │                 │                   │                   │             │
│  2452 │ 2026-12-04 │ Fuerza         │ Sentadillas   │   90.0 │ kgs         │     5 │         450.0 │          │               │            │                 │                   │                   │             │
│  2453 │ 2026-12-04 │ Fuerza         │ Press militar │   40.0 │ kgs         │     5 │         200.0 │          │               │            │                 │                   │                   │             │
│  2454 │ 2026-12-04 │ Fuerza         │ Press militar │   45.0 │ kgs         │     5 │         225.0 │          │               │            │                 │                   │                   │ Intenso     │
│  2455 │ 2026-12-04 │ Fuerza         │ Press militar │   45.0 │ kgs         │     5 │         225.0 │          │               │            │                 │                   │                   │ Muy intenso │
│  2456 │ 2026-12-04 │ Fuerza         │ Press banca   │   65.0 │ kgs         │     5 │         325.0 │          │               │            │                 │                   │                   │             │
│  2457 │ 2026-12-04 │ Fuerza         │ Press banca   │   65.0 │ kgs         │     5 │         325.0 │          │               │            │                 │                   │                   │             │
│  2458 │ 2026-12-04 │ Fuerza         │ Press banca   │   70.0 │ kgs         │     5 │         350.0 │          │               │            │                 │                   │                   │             │
│  2459 │ 2026-12-04 │ Fuerza         │ Chin Up       │    0.0 │ kgs         │    15 │           0.0 │          │               │            │                 │                   │                   │             │
│  2460 │ 2026-12-04 │ Fuerza         │ Chin Up       │    0.0 │ kgs         │    15 │           0.0 │          │               │            │                 │                   │                   │             │
│  2461 │ 2026-12-04 │ Fuerza         │ Dominadas     │    0.0 │ kgs         │    15 │           0.0 │          │               │            │                 │                   │                   │             │
├───────┴────────────┴────────────────┴───────────────┴────────┴─────────────┴───────┴───────────────┴──────────┴───────────────┴────────────┴─────────────────┴───────────────────┴───────────────────┴─────────────┤
│ 14 rows                                                                                                                                                                                                 15 columns │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


v_workout
┌───────┬────────────┬────────────────┬───────────────┬────────┬─────────────┬───────┬───────────────┬──────────┬───────────────┬────────────┬─────────────────┬───────────────────┬──────────────┬─────────────┐
│  id   │   fecha    │ tipo_ejercicio │   ejercicio   │ weight │ weight_unit │ reps  │ volumen_total │ distance │ distance_unit │ time_spent │ tiempo_segundos │ velocidad_km_hora │ ritmo_min_km │   comment   │
│ int64 │    date    │    varchar     │    varchar    │ double │   varchar   │ int32 │    double     │  double  │    varchar    │  varchar   │     double      │      double       │    double    │   varchar   │
├───────┼────────────┼────────────────┼───────────────┼────────┼─────────────┼───────┼───────────────┼──────────┼───────────────┼────────────┼─────────────────┼───────────────────┼──────────────┼─────────────┤
│  2448 │ 2026-12-04 │ Natación       │ Natación      │        │             │       │               │   7010.0 │ m             │ 00:45:51   │          2751.0 │              9.17 │         6.54 │ 160-175     │
│  2449 │ 2026-12-04 │ Correr         │ Correr        │        │             │       │               │   5000.0 │ m             │ 00:33:05   │          1985.0 │              9.07 │         6.62 │ 161-172     │
│  2450 │ 2026-12-04 │ Fuerza         │ Sentadillas   │   85.0 │ kgs         │     5 │         425.0 │          │               │            │                 │                   │              │             │
│  2451 │ 2026-12-04 │ Fuerza         │ Sentadillas   │   85.0 │ kgs         │     5 │         425.0 │          │               │            │                 │                   │              │             │
│  2452 │ 2026-12-04 │ Fuerza         │ Sentadillas   │   90.0 │ kgs         │     5 │         450.0 │          │               │            │                 │                   │              │             │
│  2453 │ 2026-12-04 │ Fuerza         │ Press militar │   40.0 │ kgs         │     5 │         200.0 │          │               │            │                 │                   │              │             │
│  2454 │ 2026-12-04 │ Fuerza         │ Press militar │   45.0 │ kgs         │     5 │         225.0 │          │               │            │                 │                   │              │ Intenso     │
│  2455 │ 2026-12-04 │ Fuerza         │ Press militar │   45.0 │ kgs         │     5 │         225.0 │          │               │            │                 │                   │              │ Muy intenso │
│  2456 │ 2026-12-04 │ Fuerza         │ Press banca   │   65.0 │ kgs         │     5 │         325.0 │          │               │            │                 │                   │              │             │
│  2457 │ 2026-12-04 │ Fuerza         │ Press banca   │   65.0 │ kgs         │     5 │         325.0 │          │               │            │                 │                   │              │             │
│  2458 │ 2026-12-04 │ Fuerza         │ Press banca   │   70.0 │ kgs         │     5 │         350.0 │          │               │            │                 │                   │              │             │
│  2459 │ 2026-12-04 │ Fuerza         │ Chin Up       │    0.0 │ kgs         │    15 │           0.0 │          │               │            │                 │                   │              │             │
│  2460 │ 2026-12-04 │ Fuerza         │ Chin Up       │    0.0 │ kgs         │    15 │           0.0 │          │               │            │                 │                   │              │             │
│  2461 │ 2026-12-04 │ Fuerza         │ Dominadas     │    0.0 │ kgs         │    15 │           0.0 │          │               │            │                 │                   │              │             │
├───────┴────────────┴────────────────┴───────────────┴────────┴─────────────┴───────┴───────────────┴──────────┴───────────────┴────────────┴─────────────────┴───────────────────┴──────────────┴─────────────┤
│ 14 rows                                                                                                                                                                                            15 columns │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

v_resumen_diario
┌────────────┬────────────────┬──────────────────┬──────────────┬──────────┬───────────────┬─────────────────┬──────────┬───────────────────┬──────────────┬─────────────────────────────────────────────────────────────┐
│   fecha    │ tipo_ejercicio │ n_tipo_ejercicio │ n_ejercicios │ n_series │ volumen_total │ tiempo_segundos │ distance │ velocidad_km_hora │ ritmo_min_km │                    ejercicios_realizados                    │
│    date    │    varchar     │      int64       │    int64     │  int64   │    double     │     double      │  double  │      double       │    double    │                           varchar                           │
├────────────┼────────────────┼──────────────────┼──────────────┼──────────┼───────────────┼─────────────────┼──────────┼───────────────────┼──────────────┼─────────────────────────────────────────────────────────────┤
│ 2026-12-04 │ Correr         │                1 │            1 │        1 │               │          1985.0 │   5000.0 │              9.07 │         6.62 │ Correr                                                      │
│ 2026-12-04 │ Fuerza         │                1 │            5 │       12 │        2950.0 │                 │          │                   │              │ Sentadillas, Press militar, Dominadas, Press banca, Chin Up │
│ 2026-12-04 │ Natación       │                1 │            1 │        1 │               │          2751.0 │   7010.0 │              9.17 │         6.54 │ Natación                                                    │
└────────────┴────────────────┴──────────────────┴──────────────┴──────────┴───────────────┴─────────────────┴──────────┴───────────────────┴──────────────┴─────────────────────────────────────────────────────────────┘

v_ejercicios_detalle
┌────────┬────────────┬────────────────┬───────────────┬─────────────────────────────────────┐
│ min_id │   fecha    │ tipo_ejercicio │   ejercicio   │          detalle_ejercicio          │
│ int64  │    date    │    varchar     │    varchar    │               varchar               │
├────────┼────────────┼────────────────┼───────────────┼─────────────────────────────────────┤
│   2448 │ 2026-12-04 │ Natación       │ Natación      │ 7010m en 00:45:51, 6.54 min/km      │
│   2449 │ 2026-12-04 │ Correr         │ Correr        │ 5000m en 00:33:05, 6.62 min/km      │
│   2450 │ 2026-12-04 │ Fuerza         │ Sentadillas   │ (85kgs x 5),(85kgs x 5),(90kgs x 5) │
│   2453 │ 2026-12-04 │ Fuerza         │ Press militar │ (40kgs x 5),(45kgs x 5),(45kgs x 5) │
│   2456 │ 2026-12-04 │ Fuerza         │ Press banca   │ (65kgs x 5),(65kgs x 5),(70kgs x 5) │
│   2459 │ 2026-12-04 │ Fuerza         │ Chin Up       │ (0kgs x 15),(0kgs x 15)             │
│   2461 │ 2026-12-04 │ Fuerza         │ Dominadas     │ (0kgs x 15)                         │
└────────┴────────────┴────────────────┴───────────────┴─────────────────────────────────────┘

exercise_muscles
┌───────────┬────────────────┬────────────────┬───────────────┐
│ ejercicio │ tipo_ejercicio │    musculos    │ tipo_musculos │
│  varchar  │    varchar     │    varchar     │    varchar    │
├───────────┼────────────────┼────────────────┼───────────────┤
│ Chin Up   │ Fuerza         │ Abdominales    │ Asistencial   │
│ Chin Up   │ Fuerza         │ Trapecio       │ Asistencial   │
│ Chin Up   │ Fuerza         │ Braquial       │ Asistencial   │
│ Chin Up   │ Fuerza         │ Dorsal ancho   │ Principal     │
│ Chin Up   │ Fuerza         │ Bíceps         │ Principal     │
│ Ciclismo  │ Cardio         │ Gemelos        │ Principal     │
│ Ciclismo  │ Cardio         │ Isquiotibiales │ Asistencial   │
│ Ciclismo  │ Cardio         │ Cuádriceps     │ Principal     │
│ Ciclismo  │ Cardio         │ Glúteos        │ Principal     │
│ Correr    │ Cardio         │ Cuádriceps     │ Principal     │
└─────────────────────────────────────────────────────────────┘
"""