# 🏋️ Dashboard de Entrenamientos (FitNotes Analytics)

## 📌 Estado del Proyecto
- **Fase Actual:** Migración de arquitectura Frontend completada (Monolito FastAPI + Jinja2 + HTMX + Alpine.js). Correcciones menores de UI/UX y preparación para despliegue y producción.
- **Metodología:** Desarrollo Modular vía Chat + FastAPI + Jinja2 + HTMX + DuckDB

---

## 🎯 Requisitos Clave
La aplicación debe permitir:

- Consultar rápidamente el próximo entrenamiento.
- Revisar el último entrenamiento realizado.
- Navegar por un calendario de entrenamientos.
- Consultar el detalle de una sesión concreta.
- Analizar la evolución histórica de cada ejercicio.

El diseño será **Mobile First**, aunque también deberá funcionar correctamente en escritorio.

### Funcionalidades Excluidas de la Primera Versión

Las siguientes funcionalidades quedan aplazadas para futuras versiones:

- Objetivos deportivos.
- Fatiga y recuperación.
- Riesgo de sobreentrenamiento.
- Registro de sensaciones.
- Récords globales.
- Comparativas avanzadas.
- Tendencias de volumen.
- Análisis por grupos musculares.
- Buscador global.
- Frecuencia de entrenamiento.
- KPIs avanzados.
- Informes automáticos.
- Recomendaciones inteligentes.


---

## Principios de Diseño

- Mobile First.
- Navegación simple.
- Máximo 2-3 clics para acceder a cualquier dato importante.
- Pantallas con poca densidad visual.
- Modo oscuro como diseño principal.
- Prioridad absoluta a la velocidad de consulta frente a la cantidad de información mostrada.
- Añadir nuevas funcionalidades únicamente cuando exista una necesidad real detectada durante el uso diario.

---

## 🛠️ Stack Tecnológico
- **Frontend y Vistas:** Jinja2 Templates + Tailwind CSS + HTMX + Alpine.js
  - Renderizado desde el servidor con FastAPI, utilizando HTMX para actualizaciones parciales y asíncronas de la interfaz (búsquedas, paginación, filtros) y Alpine.js para la interactividad de componentes locales (como la conmutación frontal/trasera del mapa corporal SVG).
- **Backend:** FastAPI (Python)
  - FastAPI gestiona toda la lógica de negocio, rutas HTML/Fragmentos, parseo del CSV, cálculos de 1RM, agrupaciones musculares y servicio de datos integrado de forma monolítica.
- **Motor de Datos:** DuckDB (análisis en memoria / almacenamiento OLAP superrápido)
  - Base de datos analítica (OLAP) ultra rápida en Python que procesa consultas SQL sobre dataframes o CSVs a gran velocidad, ideal para agregaciones de volumen y métricas por ejercicio.
- **Formato Origen:** CSV exportado de FitNotes

---

## 📋 Hoja de Ruta (Roadmap por Módulos)

- [x] **Módulo 1:** Estructura del proyecto, entorno de desarrollo y definición del esquema de datos + `PROJECT_CONTEXT.md`.

- [x] **Módulo 2:** Base FastAPI + Pantalla de Inicio
    - Backend y Vistas: Endpoints y fragmentos HTML para Próximo entrenamiento, Último entrenamiento, Resumen general filtrable (Semana/Mes/Año/Histórico) y mini-calendario interactivo.

- [x] **Módulo 3:** Pantalla de Calendario
  - Backend y Vistas: Renderizado del estado de cada día del mes (Realizado, Planificado, Descanso) según los registros del CSV con filtrado dinámico por disciplina mediante HTMX.

- [x] **Módulo 4:** Pantalla de Detalle del Día (`/sesiones/{fecha}`)
  - Backend y Vistas: Consulta del desglose de la sesión (ejercicios, series, peso, volumen) + Mapeo anatómico (Músculos primarios en rojo, secundarios en amarillo) con soporte SVG interactivo mediante Alpine.js.

- [x] **Módulo 5:** Pantalla de Histórico del Ejercicio (`/ejercicios`)
  - Backend y Vistas: Histórico inverso, cálculo de 1RM estimado (Fórmula de Epley), peso máximo registrado y proyecciones de cardio (Fórmula de Riegel), con buscador en tiempo real y paginación mediante HTMX.

- [ ] **Módulo 6:** Despliegue y Producción
  - Configuración de Dockerfile, volúmenes de persistencia, variables de entorno y requerimientos finales.

---

## 📋 Cosas que dejo pendientes de arreglar/modificar más adelante
- [] **Variables de entorno (.env):** Externalizar configuraciones de red y puertos fuera del código de los servicios.
- [x] **Pantalla Inicio:** Solucionado el manejo de ejercicios nuevos no contemplados en previsiones.
- [x] **Pantalla Inicio:** Actualizado el gráfico de resumen al formato de líneas del histórico.
- [] **Pantalla Detalle del Día:** Mejorar la estética visual del mapa muscular SVG.
- [x] **Pantalla Histórico de Ejercicios:** Incluida la maratón en estimaciones de Carrera y 100m en Natación.
- [x] **Pantalla Histórico de Ejercicios:** Adaptación de gráficos a indicadores de líneas.
- [x] **General:** Enlace en la cabecera directo a inicio y retirada definitiva de configuraciones de PWA/Svelte.
- [x] **Pantalla principal y calendario:** Ajuste del color de fondo del calendario para uniformidad visual.
- [x] **Pantalla principal:** Resumen de semana/mes ocupando toda la fila.
- [] **Multiusuario:** Registro de usuarios y aislamiento de datos de entrenamiento por perfil.
- [] **Sistema de log dual:** Guardado en fichero y salida simultánea en consola.
- [] **Guardar y modificar registros en BBDD propia:** Independizar el sistema de FitNotes permitiendo creación, edición y borrado directo de ejercicios y sesiones.
- [] **Integración Garmin Connect:** Sincronización automática de actividades con la base de datos local.
- [] **BBDD - Tipos de ejercicio:** Soporte para variantes complejas (ej. paseo granjero, métricas mixtas).
- [] **Calendario:** Filtrado interactivo por disciplina al pinchar directamente sobre el tipo de ejercicio.