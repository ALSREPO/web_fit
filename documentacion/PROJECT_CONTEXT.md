# 🏋️ Dashboard de Entrenamientos (FitNotes Analytics)

## 📌 Estado del Proyecto
- **Fase Actual:** Módulo 1 Finalizado. Listo para iniciar el Módulo 2 (Lógica Analítica Avanzada en Backend).
- **Metodología:** Desarrollo Modular vía Chat + SvelteKit + FastAPI + DuckDB

---

## 🎯 Requisitos Clave
1. **Entrada y gestión de los datos:** carga completa del fichero csv. Se mostrará la última versión cargada y si hay una disponible. Se recargará con un botón, o quizás de forma automática (cron, demonio...).
2. **Planificación Futura:** Destacado "Hoy / Próximo entrenamiento": Muestra el siguiente día planificado en FitNotes para servir de recordatorio y motivación. Vista de Planificación Futura: Listado o vista rápida de las sesiones agendadas para los próximos días.
3. **Vista General:** Heatmap de consistencia, KPIs globales, visualización del mapa corporal tipo Garmin (Rojo: primario, Amarillo: secundario, Gris: sin usar).
4. **Análisis por Ejercicio:** Histórico en orden cronológico inverso (lo más reciente primero), métricas de 1RM, máximos pesos y gráficos de volumen. Tablas de récords personales.
5. **Análisis de Sesión:** Ejercicios ejecutados, volumen, desglose serie por serie (peso, repeticiones) y notas escritas durante el ejercicio.
6. **Tendencias y Volumen Semanal / Mensual:** Análisis a medio y largo plazo para evaluar fatiga y sobrecarga progresiva. Volumen Semanal por Grupo Muscular: Gráfico de barras apiladas para ver si estás cumpliendo con el rango de series semanales por músculo. Riesgo de Sobreentrenamiento / Fatiga: Tendencia del volumen medio por semana/mes para identificar caídas bruscas o picos excesivos de trabajo.
5. **Diseño:** Mobile-First (Responsive), listo para convertirse en PWA instalable en Android.

---

## 🛠️ Stack Tecnológico
- **Frontend:** SvelteKit (Mobile-First, PWA, Tailwind CSS / componentes SVG para mapa corporal)
  - Svelte es famoso por su sintaxis intuitiva, casi idéntica a HTML/JS nativo pero superpotente. Manipular elementos como el mapa corporal interactivo en SVG y cambiar sus colores (rojo, amarillo, gris) según los datos es absurdamente fácil en Svelte/React.
  - Librería gráfica: Recharts o Chart.js (vienen con componentes interactivos muy limpios).
- **Backend:** FastAPI (Python)
  - FastAPI gestionará la lógica de parseo del CSV, la formulación de 1RM, las agrupaciones musculares y servirá los datos vía endpoints JSON documentados con OpenAPI.
- **Motor de Datos:** DuckDB (análisis en memoria / almacenamiento OLAP superrápido)
  - Es el "SQLite del análisis de datos". Es una base de datos analítica (OLAP) ultra rápida en Python que procesa consultas SQL sobre dataframes o CSVs a velocidad luz, ideal para agregaciones de volumen y métricas por ejercicio.
- **Formato Origen:** CSV exportado de FitNotes

---

## ¿Se puede hacer una App de Android a partir de esto?

Sí, y es sumamente sencillo. No necesitas rehacer el código ni aprender Java/Kotlin. Hay dos formas de tenerla en tu teléfono:

### Como PWA (Progressive Web App) — La opción rápida y recomendada

 - Añadimos un pequeño archivo de configuración (manifest.json) y un service worker a nuestro proyecto SvelteKit.

 - Resultado: Cuando entres desde Chrome en tu Android, te saldrá el botón "Instalar aplicación". Se creará un icono en tu pantalla de inicio, se abrirá a pantalla completa (sin la barra del navegador) y funcionará exactamente igual que cualquier app descargada de Play Store.

 - Dificultad: Muy baja (15-20 minutos de configuración).

### Con Capacitor (Android .apk nativo)

 - Usamos una herramienta llamada Capacitor (desarrollada por Ionic) que envuelve tu web SvelteKit y genera un proyecto Android listo para compilar con Android Studio.

 - Resultado: Un archivo .apk instalable en cualquier teléfono Android que puede acceder a funciones nativas si lo necesitas.

 - Dificultad: Media. Se realizará una vez finalice el proyecto web.

---

## 📋 Hoja de Ruta (Roadmap por Módulos)

- [x] **Módulo 1:** Estructura del proyecto (Monorepo), entorno de desarrollo y definición del esquema de datos + `PROJECT_CONTEXT.md`.
- [ ] **Módulo 2:** Backend en FastAPI + DuckDB (Parseo de CSV, cálculo de 1RM, orden inverso de histórico y separación de sesiones pasadas/futuras).
- [ ] **Módulo 3:** Mapeo anatómico (Relación entre ejercicios del CSV y áreas musculares del cuerpo humano).
- [ ] **Módulo 4:** Frontend SvelteKit (Estructura de vistas, navegación mobile-first y llamadas a la API).
- [ ] **Módulo 5:** Componente interactivo del Mapa Corporal en SVG estilo Garmin.
- [ ] **Módulo 6:** Configuración PWA (Instalación en Android como app).
