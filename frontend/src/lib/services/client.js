// frontend/src/lib/services/client.js
// Ajusta la IP según la dirección de tu servidor backend en la red local
// Nota: Si estás usando Docker, asegúrate de que el contenedor del backend esté accesible desde el contenedor del frontend o desde tu máquina host.

const BASE_URL = 'http://192.168.1.129:8895/api/v1';

export async function request(endpoint, options = {}) {
  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });

    if (!res.ok) {
      throw new Error(`Error HTTP ${res.status}: ${res.statusText}`);
    }

    return await res.json();
  } catch (error) {
    console.error(`Error en petición API [${endpoint}]:`, error);
    throw error;
  }
}