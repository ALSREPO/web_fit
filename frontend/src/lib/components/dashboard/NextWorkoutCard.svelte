<!-- 
frontend/src/lib/components/dashboard/NextWorkoutCard.svelte 
Widget Próximo Entrenamiento
-->
<script>
  /** @type {{ data: { eta_label: string, routine_name: string, exercises: string[] } | null, loading: boolean }} */
  let { data = null, loading = false } = $props();
</script>

<section class="bg-slate-800/80 border border-slate-700/60 rounded-xl p-4 shadow-sm">
  {#if loading}
    <div class="animate-pulse space-y-3">
      <div class="h-4 bg-slate-700 rounded w-1/4"></div>
      <div class="h-6 bg-slate-700 rounded w-3/4"></div>
      <div class="h-4 bg-slate-700 rounded w-1/2"></div>
    </div>
  {:else if data}
    <div class="flex justify-between items-center mb-2">
      <span class="text-xs font-semibold text-blue-400 bg-blue-950/60 px-2.5 py-0.5 rounded-full border border-blue-800/50">
        {data.eta_label}
      </span>
      <span class="text-xs text-slate-400">Planificado</span>
    </div>
    <h3 class="text-lg font-bold text-slate-100">{data.routine_name}</h3>
    
    {#if data.exercises && data.exercises.length > 0}
      <ul class="mt-3 text-sm text-slate-300 space-y-1 pl-1">
        {#each data.exercises as exercise}
          <li class="flex items-center gap-2">
            <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
            {exercise}
          </li>
        {/each}
      </ul>
    {/if}
  {:else}
    <p class="text-sm text-slate-400">Sin previsión disponible.</p>
  {/if}
</section>