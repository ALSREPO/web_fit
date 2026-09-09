// frontend/src/lib/services/dashboard.js
import { request } from './client';

export const dashboardApi = {
  getNextWorkout: () => request('/dashboard/next-workout'),
  getLastWorkout: () => request('/dashboard/last-workout'),
  getSummary: (period = 'month') => request(`/dashboard/summary?period=${period}`),
  getCompactCalendar: (year, month) => {
    const query = year && month ? `?year=${year}&month=${month}` : '';
    return request(`/dashboard/calendar-compact${query}`);
  }
};