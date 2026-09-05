<!-- Pantalla de Inicio -->

<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/services/api';
  
  import NextWorkoutCard from '$lib/components/dashboard/NextWorkoutCard.svelte';
  import LastWorkoutCard from '$lib/components/dashboard/LastWorkoutCard.svelte';
  import MetricsSummaryCard from '$lib/components/dashboard/MetricsSummaryCard.svelte';
  import CompactCalendarCard from '$lib/components/dashboard/CompactCalendarCard.svelte';

  // Estados
  let nextWorkout = $state(null);
  let lastWorkout = $state(null);
  let summary = $state(null);
  let calendarData = $state(null);

  let loadingNext = $state(true);
  let loadingLast = $state(true);
  let loadingSummary = $state(true);
  let loadingCalendar = $state(true);

  let activePeriod = $state('month');

  async function loadSummary(period) {
    loadingSummary = true;
    activePeriod = period;
    try {
      summary = await api.getSummary(period);
    } catch (e) {
      console.error(e);
    } finally {
      loadingSummary = false;
    }
  }

  onMount(async () => {
    // Carga paralela de los widgets
    api.getNextWorkout().then(res => { nextWorkout = res; loadingNext = false; }).catch(() => loadingNext = false);
    api.getLastWorkout().then(res => { lastWorkout = res; loadingLast = false; }).catch(() => loadingLast = false);
    api.getCompactCalendar().then(res => { calendarData = res; loadingCalendar = false; }).catch(() => loadingCalendar = false);
    
    loadSummary('month');
  });
</script>

<div class="space-y-4">
  <h2 class="text-xl font-bold text-white">Panel Principal</h2>

  <!-- 1. Próximo Entrenamiento -->
  <NextWorkoutCard data={nextWorkout} loading={loadingNext} />

  <!-- 2. Último Entrenamiento -->
  <LastWorkoutCard data={lastWorkout} loading={loadingLast} />

  <!-- 3. Resumen General (Semana/Mes/Año/Histórico) -->
  <MetricsSummaryCard 
    data={summary} 
    loading={loadingSummary} 
    {activePeriod} 
    on:changePeriod={(e) => loadSummary(e.detail)} 
  />

  <!-- 4. Calendario Compacto -->
  <CompactCalendarCard data={calendarData} loading={loadingCalendar} />
</div>