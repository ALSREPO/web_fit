FROM node:20-slim

WORKDIR /app

# Copiar archivos de dependencias e instalar
COPY package*.json ./
RUN npm ci

# Copiar el resto del código del frontend
COPY . .

ENV TZ=Europe/Madrid
EXPOSE 5173

# En entornos de despliegue directo, ejecutamos el servidor preview/dev de SvelteKit
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]