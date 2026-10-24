FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos requirements.txt desde la carpeta backend/
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiamos el contenido de la carpeta backend/ dentro de /app/backend
COPY backend/ /app/backend/

ENV TZ=Europe/Madrid
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8888

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8888"]