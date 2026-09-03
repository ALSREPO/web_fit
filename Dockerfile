# 1. Imagen base oficial de Python ligera
FROM python:3.10-slim

# 2. Evita archivos .pyc y fuerza buffer de salida
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Directorio de trabajo
WORKDIR /app

# 4. Instalación de paquetes de compilación del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Copiamos e instalamos dependencias de Python
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/backend/requirements.txt

# 6. Copiamos el código completo
COPY . /app

# 7. Exponemos el puerto interno
EXPOSE 8888

# 8. Comando por defecto (producción / fallback)
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8888"]