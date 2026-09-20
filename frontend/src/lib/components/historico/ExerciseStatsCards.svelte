<!-- frontend/src/lib/components/historico/ExerciseStatsCards.svelte -->
<script>
    let { stats = null } = $props();

    // Cálculo de estimaciones para distintas repeticiones basado en el 1RM
    // Carga estimada = 1RM / (1 + reps/30)
    function estimateWeightForReps(oneRm, reps) {
        if (!oneRm) return null;
        return Math.round(oneRm / (1 + reps / 30.0));
    }
</script>

{#if !stats}
    <div class="h-24 w-full animate-pulse rounded-2xl bg-slate-800"></div>
{:else if !stats.has_recent_data}
    <div class="rounded-2xl border border-amber-900/50 bg-amber-950/30 p-4 text-amber-200">
        <p class="text-xs font-semibold uppercase tracking-wider text-amber-400">Sin registros recientes</p>
        <p class="mt-1 text-sm text-slate-300">
            No has realizado este ejercicio en los últimos 3 meses. Los registros anteriores no se muestran como referencia activa.
        </p>
    </div>
{:else}
    <div class="space-y-3">
        <!-- Récord Máximo y 1RM -->
        <div class="grid grid-cols-2 gap-3">
            <div class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-4 text-center shadow-md">
                <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Máximo (3M)</p>
                <p class="mt-1 font-mono text-xl font-bold text-emerald-400">
                    {stats.max_weight} <span class="text-xs font-normal text-slate-300">{stats.weight_unit}</span>
                </p>
                {#if stats.reps_at_max}
                    <p class="mt-0.5 text-xs text-slate-400">{stats.reps_at_max} reps realizad{stats.reps_at_max > 1 ? 'as' : 'a'}</p>
                {/if}
            </div>

            <div class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-4 text-center shadow-md">
                <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400">1RM Estimado</p>
                <p class="mt-1 font-mono text-xl font-bold text-blue-400">
                    {stats.estimated_1rm} <span class="text-xs font-normal text-slate-300">{stats.weight_unit}</span>
                </p>
                <p class="mt-0.5 text-xs text-slate-400">Fórmula de Epley</p>
            </div>
        </div>

        <!-- Tabla de proyecciones para series objetivo -->
        {#if stats.estimated_1rm}
            <div class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-4 shadow-md">
                <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">Estimación por Repeticiones</p>
                <div class="grid grid-cols-4 gap-2 text-center">
                    {#each [2, 3, 4, 5] as reps}
                        <div class="rounded-xl bg-slate-900/70 py-2">
                            <p class="text-[10px] text-slate-400">{reps} RM</p>
                            <p class="font-mono text-xs font-bold text-slate-200">
                                ~{estimateWeightForReps(stats.estimated_1rm, reps)} <span class="text-[9px] font-normal text-slate-400">{stats.weight_unit}</span>
                            </p>
                        </div>
                    {/each}
                </div>
            </div>
        {/if}
    </div>
{/if}