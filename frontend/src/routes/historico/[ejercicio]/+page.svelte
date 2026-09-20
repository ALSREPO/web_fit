<!-- frontend/src/routes/historico/[ejercicio]/+page.svelte -->
<script>
    import { page } from '$app/state';
	import { dashboardApi } from '$lib/services';

    import ExerciseStatsCards from '$lib/components/historico/ExerciseStatsCards.svelte';

    let loading = $state(true);
    let error = $state(null);
    let maxStats = $state(null);
    let history = $state([]);

    let ejercicio = $derived(decodeURIComponent(page.params.ejercicio || ''));

    $effect(() => {
        const currentExercise = ejercicio;
        if (!currentExercise) return;

        loading = true;
        error = null;

        Promise.all([
            dashboardApi.getExerciseMax(currentExercise),
            dashboardApi.getExerciseHistory(currentExercise).catch(() => []) // Fallback por si la lista de historial falla
        ])
            .then(([statsRes, historyRes]) => {
                maxStats = statsRes;
                history = Array.isArray(historyRes) ? historyRes : [];
            })
            .catch((e) => {
                error = e.message || 'No se pudieron obtener los datos del ejercicio';
            })
            .finally(() => {
                loading = false;
            });
    });

    function formatDate(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        return d.toLocaleDateString('es-ES', { weekday: 'short', day: 'numeric', month: 'short' });
    }
</script>

<div class="space-y-4">
    <!-- Navegación superior -->
    <a href="/calendario" class="inline-flex items-center text-xs font-medium text-blue-400 hover:text-blue-300">
        ← Volver
    </a>

    <!-- Cabecera -->
    <header class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-5 shadow-md">
        <p class="text-xs font-medium uppercase tracking-wider text-slate-400">Histórico de Ejercicio</p>
        <h2 class="mt-1 text-2xl font-bold text-white">{ejercicio}</h2>
    </header>

    {#if loading}
        <div class="space-y-3 animate-pulse">
            <div class="h-28 w-full rounded-2xl bg-slate-800"></div>
            <div class="h-40 w-full rounded-2xl bg-slate-800"></div>
            <div class="h-64 w-full rounded-2xl bg-slate-800"></div>
        </div>
    {:else if error}
        <p class="rounded-xl border border-rose-900/60 bg-rose-950/40 p-4 text-sm text-rose-300">{error}</p>
    {:else}
        <!-- KPIs y Tarjetas de Récord -->
        <ExerciseStatsCards stats={maxStats} />

        <!-- Historial Cronológico Inverso -->
        <section class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-4 shadow-md">
            <h3 class="mb-3 text-base font-semibold text-white">Sesiones Anteriores</h3>

            {#if history.length === 0}
                <p class="text-sm text-slate-400">No hay historial registrado para este ejercicio.</p>
            {:else}
                <div class="space-y-4">
                    {#each history as session}
                        <div class="rounded-xl border border-slate-700/70 bg-slate-900/60 p-3">
                            <div class="mb-2 flex items-center justify-between border-b border-slate-800 pb-2">
                                <a href="/detalle/{session.fecha}" class="text-xs font-bold text-blue-400 hover:underline">
                                    {formatDate(session.fecha)}
                                </a>
                                {#if session.total_volume_kg}
                                    <span class="text-xs text-slate-400">
                                        Volumen: {Math.round(session.total_volume_kg).toLocaleString('es-ES')} kg
                                    </span>
                                {/if}
                            </div>

                            {#if session.sets?.length}
                                <ol class="space-y-1.5">
                                    {#each session.sets as set, index}
                                        <li class="flex items-center justify-between gap-2 text-xs text-slate-300">
                                            <span class="w-6 shrink-0 font-semibold text-slate-500">S{index + 1}</span>
                                            <span class="flex-1 font-mono">{set.weight} kg × {set.reps}</span>
                                            {#if set.comment}
                                                <span class="max-w-[40%] truncate text-right text-slate-500">{set.comment}</span>
                                            {/if}
                                        </li>
                                    {/each}
                                </ol>
                            {/if}
                        </div>
                    {/each}
                </div>
            {/if}
        </section>
    {/if}
</div>