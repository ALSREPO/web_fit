<!-- 
frontend/src/lib/components/dashboard/LastWorkoutCard.svelte 
Widget Último Entrenamiento
-->
<script>
  /** @type {{ data: { fecha: string, category: string, duration_minutes: number|null, total_volume_kg: number, exercises_count: number } | null, loading: boolean }} */
  let { data = null, loading = false } = $props();

  function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'short' });
  }
</script>

<section class="bg-slate-800/80 border border-slate-700/60 rounded-xl p-4 shadow-sm">
  {#if loading}
    <div class="animate-pulse space-y-3">
      <div class="h-4 bg-slate-700 rounded w-1/3"></div>
      <div class="h-6 bg-slate-700 rounded w-2/3"></div>
      <div class="grid grid-cols-3 gap-2 pt-2">
        <div class="h-8 bg-slate-700 rounded"></div>
        <div class="h-8 bg-slate-700 rounded"></div>
        <div class="h-8 bg-slate-700 rounded"></div>
      </div>
    </div>
  {:else if data}
    <div class="flex justify-between items-center mb-1">
      <span class="text-xs font-medium text-slate-400 capitalize">{formatDate(data.fecha)}</span>
      <span class="text-xs text-emerald-400 bg-emerald-950/50 px-2 py-0.5 rounded border border-emerald-800/40">
        Completado
      </span>
    </div>
    <h3 class="text-lg font-bold text-slate-100 mb-3">{data.category}</h3>
    
    <div class="grid grid-cols-3 gap-2 text-center pt-2 border-t border-slate-700/50">
      <div>
        <p class="text-xs text-slate-400">Duración</p>
        <p class="text-sm font-semibold text-slate-200">
          {data.duration_minutes ? `${data.duration_minutes}m` : '--'}
        </p>
      </div>
      <div>
        <p class="text-xs text-slate-400">Volumen</p>
        <p class="text-sm font-semibold text-slate-200">{data.total_volume_kg.toLocaleString('es-ES')} kg</p>
      </div>
      <div>
        <p class="text-xs text-slate-400">Ejercicios</p>
        <p class="text-sm font-semibold text-slate-200">{data.exercises_count}</p>
      </div>
    </div>
  {:else}
    <p class="text-sm text-slate-400">No hay registros recientes.</p>
  {/if}
</section>