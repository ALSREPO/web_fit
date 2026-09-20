// frontend/src/lib/services/exercise.js
import { request } from './client';

export const exerciseApi = {
  getExerciseMax: (ejercicio) => request(`/exercise-max/${encodeURIComponent(ejercicio)}`),
  getExerciseHistory: (ejercicio) => request(`/exercise-history/${encodeURIComponent(ejercicio)}`)
};