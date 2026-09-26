FROM node:20-slim

WORKDIR /app

# Copiamos los archivos de dependencias desde la carpeta frontend/
COPY frontend/package*.json ./

# Cambiamos npm ci por npm install
RUN npm install

# Copiamos el resto del código fuente del frontend
COPY frontend/ ./

ENV TZ=Europe/Madrid
EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]