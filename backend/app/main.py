from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# Versión inicial para comprobar que funciona el backend y la infraestructura base.

app = FastAPI(
    title="FitNotes Analytics API",
    description="Backend para el seguimiento y análisis de entrenamientos",
    version="0.1.0"
)

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FitNotes Dashboard - API Status</title>
        <style>
            body {
                font-family: system-ui, -apple-system, sans-serif;
                background-color: #0f172a;
                color: #f8fafc;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .card {
                background-color: #1e293b;
                padding: 2.5rem;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.5);
                text-align: center;
                max-width: 480px;
                border: 1px solid #334155;
            }
            h1 { color: #38bdf8; margin-bottom: 0.5rem; font-size: 1.8rem; }
            p { color: #94a3b8; font-size: 1rem; line-height: 1.5; }
            .badge {
                display: inline-block;
                background-color: #22c55e;
                color: #052e16;
                font-weight: bold;
                padding: 0.3rem 0.8rem;
                border-radius: 9999px;
                font-size: 0.85rem;
                margin-top: 1rem;
            }
            a {
                display: inline-block;
                margin-top: 1.5rem;
                color: #38bdf8;
                text-decoration: none;
                font-weight: 500;
            }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🏋️ FitNotes Analytics</h1>
            <p>Web de seguimiento y análisis avanzado de entrenamientos</p>
            <div class="badge">● Backend Activo (FastAPI + DuckDB)</div>
            <br>
            <a href="/docs" target="_blank">Ver documentación interactiva (Swagger UI) →</a>
        </div>
    </body>
    </html>
    """

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "ok",
        "app": "FitNotes Analytics",
        "module": "Módulo 1 - Configuración e Infraestructura Base"
    }