<!-- 
frontend/src/lib/components/dashboard/CompactCalendarCard.svelte 
Widget Calendario Compacto
-->
<script>
  /** @type {{ data: { year: number, month: number, days: Array<{ fecha: string, has_workout: boolean }> } | null, loading: boolean }} */
  let { data = null, loading = false } = $props();

  const monthNames = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
</script>

<section class="bg-slate-800/80 border border-slate-700/60 rounded-xl p-4 shadow-sm">
  <div class="flex justify-between items-center mb-3">
    <h3 class="text-sm font-semibold text-slate-300">
      {data ? `${monthNames[data.month - 1]} ${data.year}` : 'Calendario'}
    </h3>
    <a href="/calendario" class="text-xs text-blue-400 hover:text-blue-300 font-medium">Ver todo →</a>
  </div>

  {#if loading}
    <div class="h-24 bg-slate-700/50 rounded animate-pulse"></div>
  {:else if data && data.days}
    <!-- Grid de días del mes -->
    <div class="grid grid-cols-7 gap-1 text-center text-xs">
      <span class="text-slate-500 font-medium">L</span>
      <span class="text-slate-500 font-medium">M</span>
      <span class="text-slate-500 font-medium">X</span>
      <span class="text-slate-500 font-medium">J</span>
      <span class="text-slate-500 font-medium">V</span>
      <span class="text-slate-500 font-medium">S</span>
      <span class="text-slate-500 font-medium">D</span>

      {#each data.days as day}
        <div 
          class="aspect-square flex items-center justify-center rounded-md text-[10px] font-medium transition-colors
          {day.has_workout ? 'bg-blue-600 text-white font-bold' : 'bg-slate-900/50 text-slate-400'}"
          title={day.has_workout ? `Entrenado (${day.total_volume_kg} kg)` : ''}
        >
          {new Date(day.fecha).getDate()}
        </div>
      {/each}
    </div>
  {/if}
</section>