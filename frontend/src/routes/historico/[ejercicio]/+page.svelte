<!-- frontend/src/routes/historico/[ejercicio]/+page.svelte -->
<script>
    import { page } from '$app/state';
	import { dashboardApi } from '$lib/services';

    import ExerciseStatsCards from '$lib/components/historico/ExerciseStatsCards.svelte';
    import ExerciseChart from '$lib/components/historico/ExerciseChart.svelte';

    const PAGE_SIZE = 10;

    let loading = $state(true);
    let loadingMore = $state(false);
    let error = $state(null);
    let maxStats = $state(null);
    let history = $state([]);
    let offset = $state(0);
    let hasMore = $state(true);

    let ejercicio = $derived(decodeURIComponent(page.params.ejercicio || ''));

    $effect(() => {
        const currentExercise = ejercicio;
        if (!currentExercise) return;

        loading = true;
        error = null;
        offset = 0;
        hasMore = true;

        Promise.all([
            dashboardApi.getExerciseMax(currentExercise),
            dashboardApi.getExerciseHistory(currentExercise, PAGE_SIZE, 0).catch(() => [])
        ])
            .then(([statsRes, historyRes]) => {
                maxStats = statsRes;
                const items = Array.isArray(historyRes) ? historyRes : [];
                history = items;
                if (items.length < PAGE_SIZE) hasMore = false;
            })
            .catch((e) => {
                error = e.message || 'No se pudieron obtener los datos del ejercicio';
            })
            .finally(() => {
                loading = false;
            });
    });

    function loadMore() {
        if (loadingMore || !hasMore) return;
        loadingMore = true;
        const nextOffset = offset + PAGE_SIZE;

        dashboardApi.getExerciseHistory(ejercicio, PAGE_SIZE, nextOffset)
            .then((newItems) => {
                if (Array.isArray(newItems) && newItems.length > 0) {
                    history = [...history, ...newItems];
                    offset = nextOffset;
                    if (newItems.length < PAGE_SIZE) hasMore = false;
                } else {
                    hasMore = false;
                }
            })
            .finally(() => {
                loadingMore = false;
            });
    }

    // Formato con año: "vie, 4 dic 2024"
    function formatDateWithYear(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        return d.toLocaleDateString('es-ES', { 
            weekday: 'short', 
            day: 'numeric', 
            month: 'short', 
            year: 'numeric' 
        });
    }
</script>

<div class="space-y-4">
    <!-- Volver -->
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
            <div class="h-44 w-full rounded-2xl bg-slate-800"></div>
            <div class="h-64 w-full rounded-2xl bg-slate-800"></div>
        </div>
    {:else if error}
        <p class="rounded-xl border border-rose-900/60 bg-rose-950/40 p-4 text-sm text-rose-300">{error}</p>
    {:else}
        <!-- KPIs y Récords -->
        <ExerciseStatsCards stats={maxStats} />

        <!-- Gráfico Multi-Métrica y Multi-Temporal -->
        <ExerciseChart {ejercicio} />

        <!-- Lista de Sesiones Anteriores (Paginada) -->
        <section class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-4 shadow-md">
            <h3 class="mb-3 text-base font-semibold text-white">Sesiones Anteriores</h3>

            {#if history.length === 0}
                <p class="text-sm text-slate-400">No hay historial registrado para este ejercicio.</p>
            {:else}
                <div class="space-y-4">
                    {#each history as session}
                        <div class="rounded-xl border border-slate-700/70 bg-slate-900/60 p-3">
                            <div class="mb-2 flex items-center justify-between border-b border-slate-800 pb-2">
                                <a href="/detalle/{session.fecha}" class="text-xs font-bold text-blue-400 hover:underline capitalize">
                                    {formatDateWithYear(session.fecha)}
                                </a>
                                {#if session.total_volume_kg}
                                    <span class="text-xs text-slate-400 font-mono">
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

                <!-- Botón Cargar Más -->
                {#if hasMore}
                    <button
                        type="button"
                        onclick={loadMore}
                        disabled={loadingMore}
                        class="mt-4 w-full rounded-xl border border-slate-700 bg-slate-900/80 py-2.5 text-xs font-semibold text-slate-300 transition-colors hover:bg-slate-700 hover:text-white disabled:opacity-50"
                    >
                        {loadingMore ? 'Cargando...' : 'Cargar más sesiones'}
                    </button>
                {/if}
            {/if}
        </section>
    {/if}
</div>