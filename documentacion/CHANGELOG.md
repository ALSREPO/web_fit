# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.


---

## [0.1.4] - Módulo 1: Infraestructura Base e Ingesta CSV - 2026-09-03

### Added
- **Estructura Monorepo:** Configuración base de carpetas `backend/` y `frontend/`.
- **Motor de Datos (DuckDB):** Conexión persistente en `fitnotes.duckdb` e inicialización automática de tablas/secuencias.
- **Endpoints REST (FastAPI):**
  - `POST /api/v1/fitnotes/upload-csv`: Subida física del archivo CSV conservando su nombre original de FitNotes.
  - `POST /api/v1/fitnotes/import-data`: Ingesta y parseo automático del CSV más reciente hacia DuckDB.
  - `GET /api/v1/fitnotes/records`: Consulta de registros importados ordenados por fecha desc.
  - `DELETE /api/v1/fitnotes/clean-old-csvs`: Mantenimiento y limpieza de archivos CSV antiguos.

