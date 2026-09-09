<!-- 
frontend/src/lib/components/dashboard/MetricsSummaryCard.svelte 
Widget Resumen General
-->
<script>
  import { createEventDispatcher } from 'svelte';

  /** @type {{ data: { period: string, total_workouts: number, total_volume_kg: number, total_hours: number, total_distance_km: number, weekly_chart: Array<{ day_name: string, has_workout: boolean, volume_kg: number }> } | null, loading: boolean, activePeriod: string }} */
  let { data = null, loading = false, activePeriod = 'week' } = $props();

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

<section class="bg-slate-800/90 border border-slate-700/60 rounded-2xl p-5 shadow-md">
  <h3 class="text-sm font-semibold text-slate-300 mb-3">Resumen</h3>

  <!-- Selector de Periodo -->
  <div class="flex bg-slate-900/80 p-1 rounded-xl border border-slate-700/60 text-xs mb-4 justify-between">
    {#each periods as p}
      <button
        onclick={() => selectPeriod(p.id)}
        class="flex-1 py-1.5 rounded-lg text-center transition-colors {activePeriod === p.id ? 'bg-blue-600 text-white font-semibold' : 'text-slate-400 hover:text-slate-200'}"
      >
        {p.label}
      </button>
    {/each}
  </div>

  {#if loading}
    <div class="h-28 bg-slate-700/40 rounded-xl animate-pulse"></div>
  {:else if data}
    <!-- Cuadrícula de 4 Métricas Clave -->
    <div class="grid grid-cols-4 gap-2 text-center mb-5">
      <div class="bg-slate-900/50 p-2 rounded-xl border border-slate-700/40">
        <p class="text-[10px] text-slate-400">Entrenamientos</p>
        <p class="text-sm font-bold text-slate-100 mt-0.5">{data.total_workouts}</p>
      </div>
      <div class="bg-slate-900/50 p-2 rounded-xl border border-slate-700/40">
        <p class="text-[10px] text-slate-400">Volumen</p>
        <p class="text-sm font-bold text-slate-100 mt-0.5">{data.total_volume_kg > 0 ? `${Math.round(data.total_volume_kg)}kg` : '0kg'}</p>
      </div>
      <div class="bg-slate-900/50 p-2 rounded-xl border border-slate-700/40">
        <p class="text-[10px] text-slate-400">Duración</p>
        <p class="text-sm font-bold text-slate-100 mt-0.5">{data.total_hours}h</p>
      </div>
      <div class="bg-slate-900/50 p-2 rounded-xl border border-slate-700/40">
        <p class="text-[10px] text-slate-400">Distancia</p>
        <p class="text-sm font-bold text-slate-100 mt-0.5">{data.total_distance_km}km</p>
      </div>
    </div>

    <!-- Gráfico de Barras Semanal -->
    {#if data.weekly_chart && data.weekly_chart.length > 0}
      <div class="pt-2 border-t border-slate-700/40">
        <div class="flex items-end justify-between h-20 gap-2 px-1">
          {#each data.weekly_chart as day}
            <div class="flex-1 flex flex-col items-center h-full justify-end">
              <div 
                class="w-full rounded-t transition-all {day.has_workout ? 'bg-blue-600' : 'bg-slate-700/30'}"
                style="height: {day.has_workout ? '75%' : '10%'}"
              ></div>
              <span class="text-[10px] text-slate-400 mt-1">{day.day_name}</span>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  {/if}
</section>