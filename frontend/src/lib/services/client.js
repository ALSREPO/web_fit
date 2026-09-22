// frontend/src/lib/services/client.js

// Si existe la variable de entorno VITE_API_URL (en dev), la usa.
// Si no existe (en staging/prod compilado), usa la ruta relativa '/api/v1' que sirve FastAPI directamente.
const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

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