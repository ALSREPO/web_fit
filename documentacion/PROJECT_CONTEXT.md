# 🏋️ Dashboard de Entrenamientos (FitNotes Analytics)

## 📌 Estado del Proyecto
- **Fase Actual:** Correcciones menores antes de primer despliegue. Módulos 1, 2, 3, 4 y 5 finalizados.
- **Metodología:** Desarrollo Modular vía Chat + SvelteKit + FastAPI + DuckDB

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

- [x] **Módulo 2:** Base SvelteKit + Pantalla de Inicio
    - Backend: Endpoints para Próximo entrenamiento, Último entrenamiento, Resumen general filtrable (Semana/Mes/Año/Histórico) y mini-calendario.
    - Frontend (SvelteKit): Setup de UI (Tailwind CSS, Dark Mode, Navegación simple Mobile First) + Widgets de la Pantalla de Inicio.

- [x] **Módulo 3:** Pantalla de Calendario
  - Backend: Endpoint que devuelva el estado de cada día del mes (Realizado, Planificado, Descanso) según los registros del CSV.
  - Frontend: Vista de calendario mensual interactiva con estados de color y redirección a la fecha pulsada.

- [x] **Módulo 4:** Pantalla de Detalle del Día
  - Backend: Consulta del desglose de la sesión (ejercicios, series, peso, volumen) + Mapeo anatómico básico (Músculos primarios en rojo, secundarios en amarillo).
  - Frontend: Vista `/detalle/[fecha]` con cabecera de la sesión, desglose serie por serie y componente SVG del Mapa Muscular (Frontal/Trasero).

- [x] **Módulo 5:** Pantalla de Histórico del Ejercicio
  - Backend: Histórico inverso, cálculo de 1RM estimado, peso máximo registrado y puntos para la gráfica de evolución.
  - Frontend: Vista `/historico/[ejercicio]` con métricas clave, listado cronológico y gráfica de progresión.

- [ ] **Módulo 6:** Empaquetado PWA y Despliegue
  - Añadir manifest.json y Service Worker en SvelteKit para instalación directa en pantalla de inicio de Android (PWA sin navegador).

---

## 📋 Cosas que dejo pendientes de arreglar/modificar más adelante
- [] **Cambiar IP y el Puerto 192.168.1.129:** en frontend/src/lib/services/client.js la IP está a fuego. Hay que cambiarla a un fichero .env
- [x] **Pantalla Inicio:** en Siguiente y Anterior ejercicio no sale nada si hay algún ejercicio nuevo que no esté contemplado. Hay que cambiarlo
- [x] **Pantalla Inicio:** cambiar el gráfico para que sea similar al de "Pantalla Histórico de Ejercicios"
- [] **Pantalla Detalle del Día:** el mapa muscular es muy feo. Hay que hacerlo más estético
- [x] **Pantalla Histórico de Ejercicios:** Se puede incluir la maratón en las estimaciones de Carrera, y los 100m en natación
- [x] **Pantalla Histórico de Ejercicios:** Cambiar gráfico para hacer algunos indicadores de líneas, en vez de barras
- [] **Multiusuario:** que se puedan registrar usuarios y cada uno vea sus entrenamientos
- [] **Sistema de log dual:** que se guarde en fichero y que se muestre en consola
- [] **Guardar y modificar los registros en una BBDD propia:** que no dependa de lo que guardo en fitnotes. Añadir la posibilidad de crear ejercicios nuevos, añadir sesiones de entrenamiento, modificar o borrar las antiguas...
- [] **Obtener los ejercicios de garmin Connect:** relacionado con lo anterior, que se conecte a Garmin y guarde los registros en la BBDD