# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.


---

## [0.2.11] - Módulo 2: Pantalla de Inicio (Dashboard) - 2026-09-10

### Added
- **Frontend SvelteKit (Svelte 5):**
  - Implementación de `+page.svelte` con componentes modulares: `NextWorkoutCard`, `LastWorkoutCard`, `WorkoutSummary` y `CompactCalendarCard`.
  - Tarjetas con el resumen del próximo entrenamiento y último entrenamiento.
  - Gráfico de barras interactivo con métricas alternables (Sesiones, Volumen, Distancia) y soporte touch/click para tooltips en móviles.
  - Calendario interactivo con código de colores por disciplina (Fuerza, Carrera, Ciclismo, Natación), navegación mes/año y redirección por fecha.
  - Cliente API centralizado (`src/lib/services/dashboard.js`) y layout base en modo oscuro con `BottomNav`.

### Changed
- **Endpoints REST (FastAPI & DuckDB):**
  - `GET /api/v1/dashboard/next-workout`: Previsión del próximo entrenamiento.
  - `GET /api/v1/dashboard/last-workout`: Resumen de la última sesión registrada.
  - `GET /api/v1/dashboard/summary`: Agregación de métricas por periodo (semana, mes, año, histórico).
  - `GET /api/v1/dashboard/calendar-compact`: Estado diario y desglose de disciplinas por mes.

## [0.1.4] - Módulo 1: Infraestructura Base e Ingesta CSV - 2026-09-03

### Added
- **Estructura Monorepo:** Configuración base de carpetas `backend/` y `frontend/`.
- **Motor de Datos (DuckDB):** Conexión persistente en `fitnotes.duckdb` e inicialización automática de tablas/secuencias.
- **Endpoints REST (FastAPI):**
  - `POST /api/v1/fitnotes/upload-csv`: Subida física del archivo CSV conservando su nombre original de FitNotes.
  - `POST /api/v1/fitnotes/import-data`: Ingesta y parseo automático del CSV más reciente hacia DuckDB.
  - `GET /api/v1/fitnotes/records`: Consulta de registros importados ordenados por fecha desc.
  - `DELETE /api/v1/fitnotes/clean-old-csvs`: Mantenimiento y limpieza de archivos CSV antiguos.

