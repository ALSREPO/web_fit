<!-- /frontend/src/routes/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/services/api';

  import NextWorkoutCard from '$lib/components/dashboard/NextWorkoutCard.svelte';
  import LastWorkoutCard from '$lib/components/dashboard/LastWorkoutCard.svelte';
  import WorkoutSummary from '$lib/components/dashboard/WorkoutSummary.svelte';
  import CompactCalendarCard from '$lib/components/dashboard/CompactCalendarCard.svelte';

  // Estados con Runes (Svelte 5)
  let nextWorkout = $state(null);
  let lastWorkout = $state(null);
  let summary = $state(null);
  let calendarData = $state(null);

  let loadingNext = $state(true);
  let loadingLast = $state(true);
  let loadingSummary = $state(true);
  let loadingCalendar = $state(true);

  async function loadSummary(period) {
    loadingSummary = true;
    try {
      summary = await api.getSummary(period);
    } catch (e) {
      console.error("Error al cargar resumen:", e);
    } finally {
      loadingSummary = false;
    }
  }

  onMount(() => {
    // Carga paralela de los widgets
    api.getNextWorkout()
      .then(res => { nextWorkout = res; })
      .catch(console.error)
      .finally(() => { loadingNext = false; });

    api.getLastWorkout()
      .then(res => { lastWorkout = res; })
      .catch(console.error)
      .finally(() => { loadingLast = false; });

    api.getCompactCalendar()
      .then(res => { calendarData = res; })
      .catch(console.error)
      .finally(() => { loadingCalendar = false; });

    // Carga inicial por defecto
    loadSummary('week');
  });
</script>

<div class="space-y-4">
  <h2 class="text-xl font-bold text-white">Panel Principal</h2>

  <!-- 1. Próximo Entrenamiento -->
  <NextWorkoutCard data={nextWorkout} loading={loadingNext} />

  <!-- 2. Último Entrenamiento -->
  <LastWorkoutCard data={lastWorkout} loading={loadingLast} />

  <!-- 3. Resumen General (Llama directamente a WorkoutSummary usando props de Svelte 5) -->
  <WorkoutSummary 
    summaryData={summary} 
    loading={loadingSummary} 
    onPeriodChange={(period) => loadSummary(period)} 
  />

  <!-- 4. Calendario Compacto -->
  <CompactCalendarCard data={calendarData} loading={loadingCalendar} />
</div>