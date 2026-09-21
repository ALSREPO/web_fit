# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

---

## [0.5.x] - Correcciones menores - 2026-09-21

- **Pantalla Inicio:** 0.5.3, cambiar el gráfico para que sea similar al de "Pantalla Histórico de Ejercicios"
- **Pantalla Histórico de Ejercicios:** 0.5.2, cambiar gráfico para hacer algunos indicadores de líneas, en vez de barras
- **Pantalla Histórico de Ejercicios:** 0.5.0, incluir la maratón en las estimaciones de Carrera, y los 100m en natación

---

## [0.4.12] - Módulo 5: Histórico del Ejercicio y Proyecciones Cardio - 2026-09-21

### Added
- **Backend (FastAPI & DuckDB):**
  - Endpoint `GET /api/v1/exercises/max-weight/{ejercicio_nombre}` para obtener récords y proyecciones acotados a los últimos 3 meses.
  - Clasificación automática de actividades por disciplina (`fuerza`, `running`, `cycling`, `swimming`).
  - Cálculo de proyecciones de tiempo para actividades de cardio utilizando la **Fórmula de Riegel** ($T_2 = T_1 \times (D_2 / D_1)^{1.06}$).
  - Adaptación de distancias clave y unidades de ritmo según la disciplina:
    - **Correr:** Ritmo en `min/km` con estimaciones para 1k, 5k, 10k y 21k (Media Maratón).
    - **Ciclismo:** Ritmo en `min/km` con estimaciones para 10k, 20k, 40km (Crono) y 90km (Half).
    - **Natación:** Ritmo en `min/100m` con estimaciones para 400m, 800m, 1.500m y 3.800m (Ironman).
- **Frontend (Svelte 5):**
  - Componente `ExerciseStatsCards.svelte` rediseñado con maquetación simétrica entre Fuerza y Cardio:
    - Bloque superior con 2 tarjetas clave (*Mejor Ritmo* y *Estimado 1K / Distancia base*).
    - Bloque inferior con contenedor en cuadrícula para el resto de distancias objetivo adaptadas por disciplina.
  - Integración de los esquemas Pydantic y llamadas API correspondientes en el cliente del frontend.

### Fixed
- **Query DuckDB en Cardio:** Eliminada la restricción `AND W.weight IS NOT NULL` en la consulta del servicio para permitir que los ejercicios de cardio (cuyo peso es `NULL`) recojan correctamente las actividades de los últimos 3 meses.

---

## [0.4.0] - Módulo 5: Pantalla de Histórico de Ejercicio - 2026-09-20

### Added
- **Backend:**
  - Endpoints REST para la búsqueda de ejercicios y recuperación del historial de progresión individual.
  - Vistas DuckDB `v_workout` optimizadas para agregar rendimiento por ejercicio.
- **Frontend:**
  - Vista `/historico/[ejercicio]` con soporte para la selección de ejercicios, gráficos de progresión en el tiempo y tabla detallada de repeticiones y pesos.

---

## [0.3.0] - Módulo 4: Pantalla de Detalle del Día - 2026-09-10

### Added
- **Backend:**
  - `GET /api/v1/dashboard/day-detail/{fecha}`: desglose de la sesión (ejercicios, series, volumen, distancia, duración) y activación muscular (principal / asistencial).
- **Frontend:**
  - Vista `/detalle/[fecha]` con cabecera, listado serie a serie y mapa muscular SVG (frontal / trasero).
  - Vista `/calendario` reutilizando el calendario mensual; cada día abre su detalle.
  - Enlace al histórico del ejercicio (placeholder del Módulo 5).

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

