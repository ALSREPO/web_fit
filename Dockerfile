# ==========================================
# ETAPA 1: Compilar Frontend (SvelteKit)
# ==========================================
FROM node:20-slim AS builder-frontend
WORKDIR /app/frontend

# Copiar package.json e instalar dependencias
COPY frontend/package*.json ./
RUN npm ci

# Copiar el código fuente y compilar a archivos estáticos
COPY frontend/ ./
RUN npm run build

# ==========================================
# ETAPA 2: Runtime Final (FastAPI + Static Files)
# ==========================================
FROM python:3.10-slim AS runtime

# Dependencias necesarias de sistema para DuckDB / C++
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar dependencias de Python
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar el código del backend
COPY backend/ /app/backend/

# Copiar el build estático del frontend generado en la ETAPA 1
COPY --from=builder-frontend /app/frontend/build /app/frontend/build

ENV TZ=Europe/Madrid
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Exponemos el puerto interno
EXPOSE 8888

# Arrancamos Uvicorn en producción
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8888"]