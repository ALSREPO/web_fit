<!-- 
frontend/src/lib/components/dashboard/MetricsSummaryCard.svelte 
Widget Resumen General
-->
<script>
  import { createEventDispatcher } from 'svelte';

  /** @type {{ data: { period: string, total_workouts: number, total_volume_kg: number, total_hours: number, total_distance_km: number } | null, loading: boolean, activePeriod: string }} */
  let { data = null, loading = false, activePeriod = 'month' } = $props();

  const periods = [
    { id: 'week', label: 'Semana' },
    { id: 'month', label: 'Mes' },
    { id: 'year', label: 'Año' },
    { id: 'all', label: 'Histórico' }
  ];

  const dispatch = createEventDispatcher();

  function selectPeriod(periodId) {
    dispatch('changePeriod', periodId);
  }
</script>

<section class="bg-slate-800/80 border border-slate-700/60 rounded-xl p-4 shadow-sm">
  <div class="flex justify-between items-center mb-4">
    <h3 class="text-sm font-semibold text-slate-300">Resumen General</h3>
    <!-- Selector de periodo -->
    <div class="flex bg-slate-900/80 p-0.5 rounded-lg border border-slate-700/60 text-xs">
      {#each periods as p}
        <button
          onclick={() => selectPeriod(p.id)}
          class="px-2 py-1 rounded-md transition-colors {activePeriod === p.id ? 'bg-blue-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'}"
        >
          {p.label}
        </button>
      {/each}
    </div>
  </div>

  {#if loading}
    <div class="grid grid-cols-2 gap-3 animate-pulse">
      <div class="h-12 bg-slate-700 rounded"></div>
      <div class="h-12 bg-slate-700 rounded"></div>
    </div>
  {:else if data}
    <div class="grid grid-cols-2 gap-3">
      <div class="bg-slate-900/40 p-2.5 rounded-lg border border-slate-800">
        <p class="text-xs text-slate-400">Entrenamientos</p>
        <p class="text-base font-bold text-slate-100">{data.total_workouts}</p>
      </div>
      <div class="bg-slate-900/40 p-2.5 rounded-lg border border-slate-800">
        <p class="text-xs text-slate-400">Volumen Total</p>
        <p class="text-base font-bold text-slate-100">{data.total_volume_kg.toLocaleString('es-ES')} kg</p>
      </div>
      <div class="bg-slate-900/40 p-2.5 rounded-lg border border-slate-800">
        <p class="text-xs text-slate-400">Horas</p>
        <p class="text-base font-bold text-slate-100">{data.total_hours}h</p>
      </div>
      <div class="bg-slate-900/40 p-2.5 rounded-lg border border-slate-800">
        <p class="text-xs text-slate-400">Distancia</p>
        <p class="text-base font-bold text-slate-100">{data.total_distance_km} km</p>
      </div>
    </div>
  {/if}
</section>