<!-- frontend/src/routes/historico/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { dashboardApi } from '$lib/services';

    let loading = $state(true);
    let error = $state(null);
    let exercises = $state([]);
    let searchQuery = $state('');

    onMount(() => {
        dashboardApi.getAllExercisesOrdered()
            .then((data) => {
                exercises = Array.isArray(data) ? data : [];
            })
            .catch((e) => {
                error = e.message || 'No se pudieron cargar los ejercicios';
            })
            .finally(() => {
                loading = false;
            });
    });

    let filteredExercises = $derived(
        exercises.filter((ex) => {
            const name = ex.nombre || ex.ejercicio || '';
            return name.toLowerCase().includes(searchQuery.toLowerCase().trim());
        })
    );
</script>

<div class="space-y-4">
<!-- Cabecera y Buscador -->
<header class="flex flex-col gap-3 rounded-2xl border border-slate-700/60 bg-slate-800/90 p-5 shadow-md">
    <div class="w-full">
        <h2 class="text-2xl font-bold text-white">Histórico de Ejercicios</h2>
    </div>

    <input
        type="text"
        bind:value={searchQuery}
        placeholder="Buscar ejercicio..."
        class="w-full rounded-xl border border-slate-700/80 bg-slate-900/90 px-3.5 py-2 text-xs text-white placeholder-slate-500 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
    />
</header>

    {#if loading}
        <div class="space-y-2 animate-pulse">
            {#each Array(6) as _}
                <div class="h-16 w-full rounded-xl bg-slate-800"></div>
            {/each}
        </div>
    {:else if error}
        <p class="rounded-xl border border-rose-900/60 bg-rose-950/40 p-4 text-sm text-rose-300">{error}</p>
    {:else if filteredExercises.length === 0}
        <div class="rounded-2xl border border-slate-700/40 bg-slate-800/40 p-8 text-center text-xs text-slate-400">
            No se encontraron ejercicios con ese término.
        </div>
    {:else}
        <!-- Lista Ordenada de Ejercicios -->
        <div class="space-y-2">
            {#each filteredExercises as ex}
                {@const name = ex.nombre || ex.ejercicio}
                <button
                    type="button"
                    onclick={() => goto(`/historico/${encodeURIComponent(name)}`)}
                    class="group flex w-full items-center justify-between rounded-xl border border-slate-700/60 bg-slate-800/90 p-4 text-left transition-all hover:border-blue-500/60 hover:bg-slate-800"
                >
                    <div class="flex items-center gap-3">
                        <span class="font-semibold text-slate-200 group-hover:text-blue-400 transition-colors">
                            {name}
                        </span>
                    <!--
                        {#if ex.recent_volume > 0}
                            <span class="rounded-md bg-blue-950/60 px-2 py-0.5 text-[10px] font-medium text-blue-300 border border-blue-800/40">
                                Reciente
                            </span>
                        {/if}
                    -->
                    </div>

                    <div class="flex items-center gap-2 text-xs text-slate-400">
                        {#if ex.recent_volume > 0}
                            <span class="font-mono">{Math.round(ex.recent_volume).toLocaleString('es-ES')} kg (3M)</span>
                        {:else}
                            <span class="text-slate-500">Sin registros recientes</span>
                        {/if}
                        <svg class="h-4 w-4 text-slate-500 group-hover:text-blue-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                        </svg>
                    </div>
                </button>
            {/each}
        </div>
    {/if}
</div>