// frontend/src/lib/services/api.js
// Ajusta la IP según la dirección de tu servidor backend en la red local
// Nota: Si estás usando Docker, asegúrate de que el contenedor del backend esté accesible desde el contenedor del frontend o desde tu máquina host.

//const BASE_URL = 'http://localhost:8000/api/v1/dashboard';
const BASE_URL = 'http://192.168.1.129:8895/api/v1/dashboard'; 

async function fetchAPI(endpoint) {
  try {
    const res = await fetch(`${BASE_URL}${endpoint}`);
    if (!res.ok) {
      throw new Error(`Error HTTP: ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.error(`Error al consultar ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  getNextWorkout: () => fetchAPI('/next-workout'),
  getLastWorkout: () => fetchAPI('/last-workout'),
  getSummary: (period = 'month') => fetchAPI(`/summary?period=${period}`),
  getCompactCalendar: (year, month) => {
    const query = year && month ? `?year=${year}&month=${month}` : '';
    return fetchAPI(`/calendar-compact${query}`);
  }
};