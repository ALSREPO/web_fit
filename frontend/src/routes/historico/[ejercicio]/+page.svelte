<!-- frontend/src/routes/historico/[ejercicio]/+page.svelte -->
<script>
    import { page } from '$app/state';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
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
    let exercisesList = $state([]);

    let ejercicio = $derived(decodeURIComponent(page.params.ejercicio || ''));

    onMount(() => {
        dashboardApi.getAllExercisesOrdered()
            .then((res) => {
                exercisesList = Array.isArray(res) ? res : [];
            })
            .catch(() => {
                exercisesList = [];
            });
    });

    $effect(() => {
        const currentExercise = ejercicio;
        if (!currentExercise) return;

        loading = true;
        error = null;
        offset = 0;
        hasMore = true;

        Promise.all([
            dashboardApi.getExerciseMax(currentExercise).catch(() => null),
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

    function handleSelectChange(e) {
        const selected = e.target.value;
        if (selected && selected !== ejercicio) {
            goto(`/historico/${encodeURIComponent(selected)}`);
        }
    }

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

    function formatTime(seconds) {
        if (!seconds) return '';
        const m = Math.floor(seconds / 60);
        const s = Math.round(seconds % 60);
        return `${m}m ${s < 10 ? '0' : ''}${s}s`;
    }
</script>

<div class="space-y-4">
    <!-- Volver -->
    <a href="/historico" class="inline-flex items-center text-xs font-medium text-blue-400 hover:text-blue-300">
        ← Volver al listado
    </a>

    <!-- Cabecera con Selector Desplegable -->
    <header class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-5 shadow-md">
        <p class="text-xs font-medium uppercase tracking-wider text-slate-400">Histórico de Ejercicio</p>

        <div class="relative mt-2">
            <select
                value={ejercicio}
                onchange={handleSelectChange}
                class="w-full appearance-none rounded-xl border border-slate-700/80 bg-slate-900/90 py-2 pl-3 pr-8 text-xl font-bold text-white shadow-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 cursor-pointer"
            >
                {#if !exercisesList.some(e => (e.nombre || e.ejercicio) === ejercicio)}
                    <option value={ejercicio}>{ejercicio}</option>
                {/if}
                {#each exercisesList as ex}
                    {@const name = ex.nombre || ex.ejercicio}
                    <option value={name}>
                        {name} {ex.recent_volume > 0 ? '🔥' : ''}
                    </option>
                {/each}
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2.5 text-slate-400">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
            </div>
        </div>
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
        <ExerciseStatsCards stats={maxStats} />
        <ExerciseChart {ejercicio} />

        <section class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-4 shadow-md">
            <h3 class="mb-3 text-base font-semibold text-white">Histórico de sesiones</h3>

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
                                {:else if session.total_distance}
                                    <span class="text-xs text-slate-400 font-mono">
                                        Distancia total: {session.total_distance.toLocaleString('es-ES')} m
                                    </span>
                                {/if}
                            </div>

                            {#if session.sets?.length}
                                <ol class="space-y-1.5">
                                    {#each session.sets as set, index}
                                        <li class="flex items-center justify-between gap-2 text-xs text-slate-300">
                                            <span class="w-6 shrink-0 font-semibold text-slate-500">S{index + 1}</span>
                                            
                                            <span class="flex-1 font-mono">
                                                {#if set.weight !== null && set.reps !== null}
                                                    {set.weight} kg × {set.reps}
                                                {:else if set.distance !== null}
                                                    {set.distance} {set.distance_unit || 'm'}
                                                    {#if set.tiempo_segundos}
                                                        · {formatTime(set.tiempo_segundos)}
                                                    {/if}
                                                    {#if set.ritmo_min_km}
                                                        · <span class="text-blue-400">{set.ritmo_min_km} min/km</span>
                                                    {/if}
                                                {/if}
                                            </span>

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