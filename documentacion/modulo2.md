# Módulo 2: Pantalla de Inicio (Dashboard)

## 1. Arquitectura de Endpoints (Backend)

En el backend ampliaremos fitnotes.py (o añadiremos un router dedicado como dashboard.py) para exponer los datos estructurados en formato JSON.

Crearemos 3 bloques de endpoints principales:

- GET /api/v1/dashboard/next-workout
   - Retorna la planificación del siguiente entrenamiento (o estimación según patrón).
   - Estructura JSON: eta_label ("Mañana", "En 2 días"), routine_name ("Fuerza - Tren Superior"), exercises (["Press banca", "Remo barra", ...]).

 - GET /api/v1/dashboard/last-workout
   - Retorna la última sesión registrada en DuckDB.
   - Estructura JSON: date, category, duration_minutes, total_volume_kg, exercise_count.

 - GET /api/v1/dashboard/summary?period={week|month|year|all}
    - Métricas agregadas según el filtro.
    - Estructura JSON: total_workouts, total_volume_kg, total_hours, total_distance_km.

 - GET /api/v1/dashboard/calendar-compact?year=YYYY&month=MM
   - Devuelve los días del mes actual etiquetados si tuvieron entrenamiento o no, para renderizar la mini-vista de calendario.

## 2. Arquitectura del Frontend (SvelteKit)

Estructuraremos la carpeta frontend/ usando Tailwind CSS v3/v4 con un enfoque Dark Mode native-first (fondo oscuro por defecto, pensado para bajo consumo de batería y consulta en gimnasio).


Estructura de Componentes y Páginas:

```
frontend/
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── BottomNav.svelte      # Navegación inferior persistente (Mobile First)
│   │   │   │   └── Header.svelte         # Cabecera minimalista
│   │   │   └── dashboard/
│   │   │       ├── NextWorkoutCard.svelte
│   │   │       ├── LastWorkoutCard.svelte
│   │   │       ├── MetricsSummary.svelte # Selector de periodo (Semana/Mes/Año/Histórico)
│   │   │       └── CompactCalendar.svelte
│   │   ├── services/
│   │   │   └── api.js                    # Cliente HTTP (fetch / axios) centralizado
│   │   └── types/                        # Tipado JSDoc / TS (si aplica)
│   └── routes/
│       ├── +layout.svelte                # Wrapper global (Dark mode + BottomNav)
│       ├── +page.svelte                  # PANTALLA DE INICIO
│       ├── calendario/                   # (Módulo 3)
│       ├── detalle/[fecha]/              # (Módulo 4)
│       └── historico/[ejercicio]/        # (Módulo 5)
```


## 3. Plan de Ejecución Paso a Paso

Para ir avanzando sobre seguro sin perdernos, te sugiero trabajar en el Módulo 2 en 3 pasos secuenciales:

 - Paso A: Setup e Inicialización de SvelteKit
   - Crear e inicializar el proyecto en la carpeta frontend/.
   - Configurar Tailwind CSS, fuentes tipográficas y layout base oscuro con navegación inferior.

 - Paso B: Desarrollo de Endpoints en FastAPI + DuckDB
   - Definir las Pydantic Models del Dashboard.
   - Implementar las consultas SQL en DuckDB (csv_service.py) y crear las rutas /api/v1/dashboard/*.

- Paso C: Conexión Frontend-Backend y Construcción de Widgets
  - Desarrollar los 4 componentes visuales de la Pantalla de Inicio.
  - Conectar llamadas a la API y dejar la pantalla de inicio totalmente funcional.

---
---

## Instrucciones ejecución

Ejecuta los siguientes comandos desde la raíz del proyecto para crear la app en la carpeta frontend

1. Inicializar proyecto SvelteKit en la carpeta frontend:

    ```
    sudo apt update && sudo apt install -y curl build-essential

    # Instalar NVM
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    
    # Cargar NVM en la sesión actual
    export NVM_DIR="$HOME/.nvm" [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

    # Instalar Node.js 20 LTS
    nvm install 20

    # Usar Node.js 20
    nvm use 20

    # Verificar la versión
    node -v

    # Crear la carpeta del proyecto y generar la app SvelteKit
    cd ~/Web/web_fit_dev
    npx sv create frontend

    # escoger las opciones de configuración:
        ◇  Which template would you like?
        │  SvelteKit minimal
        │
        ◇  Add type checking with TypeScript?
        │  Yes, using JavaScript with JSDoc comments
        │
        ◇  What would you like to add to your project? (use arrow keys / space bar)
        │  tailwindcss
        │
        ◇  Which plugins would you like to add?
        │  typography, forms
        │
        ◆  Project created
        │
        ◇  Which package manager do you want to install dependencies with?
        │  npm
    
    # Una vez finalizado, entra en la carpeta, instala y arranca el servidor
    cd frontend
    npm install
    npm run dev -- --host

    # si entras en la url que te indica el terminal, deberías ver la pantalla de bienvenida de SvelteKit
    ``` 

2. 