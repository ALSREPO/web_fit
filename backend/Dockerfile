FROM python:3.10-slim

# Dependencias de sistema necesarias para DuckDB y compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar las dependencias de Python
COPY ../requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar todo el código del backend
COPY . .

ENV TZ=Europe/Madrid
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8888

# Iniciar Uvicorn exponiendo FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8888"]