// frontend/src/lib/services/dashboard.js
import { request } from './client';

export const dashboardApi = {
  getNextWorkout: () => request('/dashboard/next-workout'),
  getLastWorkout: () => request('/dashboard/last-workout'),
  getSummary: (period = 'month') => request(`/dashboard/summary?period=${period}`),
  getCompactCalendar: (year, month) => {
    const query = year && month ? `?year=${year}&month=${month}` : '';
    return request(`/dashboard/calendar-compact${query}`);
  },  
  
  getDayDetail: (fecha) => request(`/dashboard/day-detail/${fecha}`),

  getExerciseMax: (ejercicio) => request(`/dashboard/exercise-max/${encodeURIComponent(ejercicio)}`),
  getExerciseHistory: (ejercicio, limit = 10, offset = 0) => 
    request(`/dashboard/exercise-history/${encodeURIComponent(ejercicio)}?limit=${limit}&offset=${offset}`),
  getExerciseChart: (ejercicio, timeframe = '30d') => 
    request(`/dashboard/exercise-chart/${encodeURIComponent(ejercicio)}?timeframe=${timeframe}`)
};